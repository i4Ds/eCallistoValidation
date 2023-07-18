import re
from datetime import datetime
import psycopg2
from astral import Observer
from astral.sun import sun
from matplotlib import pyplot as plt

from radiospectra.sources import CallistoSpectrogram
import pandas as pd
import numpy as np
import config as ecallisto_config


class DailyObservation:
    """
    A class for processing daily observations within a specified date range.

    Parameters:
        start_date (str): The start date of the observation range in the format '%Y-%m-%d %H:%M:%S'.
        end_date (str): The end date of the observation range in the format '%Y-%m-%d %H:%M:%S'.
        station_name (str): The name of the station to filter the observation data.

    Attributes:
        start_date (str): The start date of the observation range.
        end_date (str): The end date of the observation range.
        station_name (str): The name of the station to filter the observation data.
        rows (list): List of instrument data fetched from the database.
        data (pandas.DataFrame): Processed observation data.

    Methods:
        _get_db(): Connects to the database and returns a database connection object.
        _get_all_instruments(): Retrieves all instrument data from the database.
        _calculate_sunrise_sunset(latitude, longitude, date): Calculates the sunrise and sunset times for a given location and date.
        _process_stations(): Processes the observation data for each day within the specified date range.

    Usage Example:
        start_date = '2022-01-01 00:00:00'
        end_date = '2022-01-05 23:59:59'
        station_name = 'MyStation'
        daily_observation = DailyObservation(start_date, end_date, station_name)
        observation_data = daily_observation.data
        print(observation_data)
    """

    def __init__(self, start_date, end_date, station_name):
        self.start_date = start_date
        self.end_date = end_date
        self.station_name = station_name
        self.rows = self._get_all_instruments()
        self.data = self._process_stations()
        self.duration_by_station = self.calculate_total_duration()

    @staticmethod
    def _get_db():
        """
        Connects to the database and returns a database connection object.

        Returns:
            psycopg2.extensions.connection: The database connection object.
        """
        database = psycopg2.connect(
            host=ecallisto_config.DB_HOST,
            user=ecallisto_config.DB_USER,
            database=ecallisto_config.DB_DATABASE,
            port=ecallisto_config.DB_PORT,
            password=ecallisto_config.DB_PASSWORD
        )
        return database

    def _get_all_instruments(self):
        """
        Retrieves all instrument data from the database.

        Returns:
            list: List of instrument data.
        """
        database = self._get_db()
        sql_query_instruments = """
        SELECT *, lower(observation_times) AS start_date, upper(observation_times) AS end_date 
        FROM test 
        WHERE observation_times && tsrange(%s, %s) AND snr IS NOT NULL 
        ORDER BY snr DESC;
        """

        with database.cursor() as cursor:
            cursor.execute(sql_query_instruments, (self.start_date, self.end_date))
            instruments = cursor.fetchall()

        return instruments

    @staticmethod
    def convert_to_stars(score):
        ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Compute the percentile of the data
        percent = np.percentile(score, [0, 25, 50, 75, 100])
        rating = np.interp(score, percent, ranking)
        rating = np.round(rating, 2)

        return rating

    @staticmethod
    def _calculate_sunrise_sunset(latitude, longitude, date):
        """
        Calculates the sunrise and sunset times for a given location and date.

        Parameters:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
            date (datetime): The date for which to calculate sunrise and sunset.

        Returns:
            tuple: A tuple containing the sunrise and sunset times in the format '%Y-%m-%d %H:%M:%S'.
        """
        observer = Observer(latitude=latitude, longitude=longitude)
        sun_times = sun(observer, date=date)
        sunrise = sun_times['sunrise'].strftime('%H:%M:%S')
        sunset = sun_times['sunset'].strftime('%H:%M:%S')
        return sunrise, sunset

    def extract_station_name(self, file_path):
        """
        Extracts the station name from the file path.

        Parameters:
            file_path (str): The file path containing the station name.

        Returns:
            str: The extracted station name.
        """
        match = re.search(r"/(\w+[-\w]*)_(\d{8})_\d{6}_(\d{2})\.fit\.gz$", file_path)
        if match:
            station_name = match.group(1)
            station_number = match.group(3)
            return f"{station_name}_{station_number}"

        return ""


    def _process_stations(self):
        """
        Processes the observation data for each day within the specified date range.

        Returns:
            pandas.DataFrame: Processed observation data.
        """
        data = []
        pd.set_option('display.max_columns', None)

        # Process each day within the time range
        current_date = pd.Timestamp(self.start_date)
        end_date = pd.Timestamp(self.end_date)

        while current_date <= end_date:
            rows_to_append = []
            snr_values = []
            std_values = []

            # Process each row
            for row in self.rows:
                spec = CallistoSpectrogram.read(ecallisto_config.DATA_PATH + row[6])
                station_name = self.extract_station_name(row[6])
                latitude = spec.header["OBS_LAT"]
                longitude = spec.header["OBS_LON"]
                date_obs = spec.header['DATE-OBS']
                time_obs = spec.header['TIME-OBS']
                std = row[4]
                snr = row[5]

                obs_date = datetime.strptime(f"{date_obs} {time_obs}", '%Y/%m/%d %H:%M:%S.%f')

                # Check if the observation date matches the current date and station name matches
                if obs_date.date() != current_date.date() or station_name != self.station_name:
                #if obs_date.date() != current_date.date():
                    continue

                sunrise, sunset = self._calculate_sunrise_sunset(latitude, longitude, obs_date)

                rows_to_append.append({
                    'Station': station_name,
                    'Date': obs_date.strftime('%Y-%m-%d'),
                    'Sunrise': sunrise,
                    'Sunset': sunset,
                    'Obs_start': spec.start,
                    'Obs_end': spec.end,
                    'SNR': snr,
                    'STD': std
                })

                snr_values.append(snr)
                std_values.append(std)

            # Determine the minimum Obs_start and maximum Obs_end for the current date
            if rows_to_append:
                min_obs_start = min(rows_to_append, key=lambda x: x['Obs_start'])['Obs_start']
                max_obs_end = max(rows_to_append, key=lambda x: x['Obs_end'])['Obs_end']
                duration = max_obs_end - min_obs_start
                duration_str = str(duration).split('.')[0]  # Remove microseconds
                duration = datetime.strptime(duration_str, '%H:%M:%S')

                avg_snr = sum(snr_values) / len(snr_values)
                avg_std = sum(std_values) / len(std_values)

                row_to_append = {
                    'Station': rows_to_append[0]['Station'],
                    'Sunrise': rows_to_append[0]['Sunrise'],
                    'Sunset': rows_to_append[0]['Sunset'],
                    'Obs_start': min_obs_start,
                    'Obs_end': max_obs_end,
                    'Duration': duration.strftime('%H:%M:%S'),
                    'Avg-SNR': avg_snr,
                    'Avg-STD': avg_std
                }

                # Append a single row for the current date with the combined information
                data.append(row_to_append)

            # Move to the next day
            current_date += pd.DateOffset(days=1)

        if not data:
            print("There are no files for the given station in the given time range.")

        return pd.DataFrame(data)

    def calculate_total_duration(self):
        """
        Calculates the total duration and average SNR and std for each station.

        Returns:
            pandas.DataFrame: Total duration and average SNR and std data by station.
        """
        total_duration = self.data.groupby('Station')['Duration'].apply(
            lambda x: pd.to_timedelta(x).sum()
        ).reset_index()

        #total_duration['Duration'] = total_duration['Duration'].apply(lambda duration: f"{duration.days} days, {duration}" if duration.days > 0else str(duration))
        total_duration['Duration'] = total_duration['Duration'].apply(
            lambda duration: f"{duration.days} days, {str(duration)[-8:]}"
            if duration.days > 0
            else str(duration)
        )

        # Calculate the average SNR and std
        average_stats = self.data.groupby('Station').agg({'Avg-SNR': 'mean', 'Avg-STD': 'mean'}).reset_index()

        # Convert Avg-SNR and Avg-STD to stars
        #average_stats['snr_rating'] = self.convert_to_stars(average_stats['Avg-SNR'])
        #average_stats['std_rating'] = self.convert_to_stars(average_stats['Avg-STD'])

        # Merge total duration and average stats
        total_duration = total_duration.merge(average_stats, on='Station')


        return total_duration


start_date = '2022-03-08 14:30:03'
end_date = '2022-03-09 14:30:03'
station_name = 'MRT3_02'


#daily_observation = DailyObservation(start_date, end_date, station_name)
#print(daily_observation.data)

#total_duration_data = daily_observation.calculate_total_duration()
#print(total_duration_data)
