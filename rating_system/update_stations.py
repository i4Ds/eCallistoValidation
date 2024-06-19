import datetime
import psycopg2.extras
import psycopg2
from rating_system.radiospectra.sources import CallistoSpectrogram
import ephem
import mysql.connector
import config as ecallisto_config
import pytz


class UpdateStation:
    def __init__(self):
        self.database = self.get_db()
        self.stations = self.get_stations(self.database)
        self.end_date = datetime.datetime.now()  # end date for the update
        self.observation_data = {}

    def get_stations(self, database):
        sql_get_stations = """SELECT * FROM stations_test"""
        cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql_get_stations)
        stations = [dict(i) for i in cursor.fetchall()]
        return stations

    def get_db(self):
        database = psycopg2.connect(
            host=ecallisto_config.DB_HOST,
            user=ecallisto_config.DB_USER,
            database=ecallisto_config.DB_DATABASE,
            port=ecallisto_config.DB_PORT,
            password=ecallisto_config.DB_PASSWORD
        )
        return database

    def get_all_instruments(self):
        """
        Get all instruments from the database
        :return: The instruments
        """
        sql_query_instruments = "SELECT * FROM test WHERE snr IS NOT NULL ORDER BY snr DESC LIMIT 100;"

        with self.database.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_query_instruments)
            instruments = [row for row in cursor.fetchall()]

        return instruments

    def _get_observation_times(self, station, ephemeris_start, ephemeris_end):
        database = self.get_db()
        sql_select_dates = """SELECT f.observation_times FROM test f LEFT JOIN virtual_instruments v ON f.fk_virtual_instrument = v.id LEFT JOIN instruments i ON v.fk_instrument = i.id LEFT JOIN stations s ON i.fk_station = s.id WHERE s.id=%s AND %s && observation_times ORDER BY observation_times;"""
        with database.cursor() as cursor:
            sql_str = cursor.mogrify(
                sql_select_dates, (
                    station["id"],
                    psycopg2.extras.DateTimeRange(ephemeris_start, ephemeris_end, "()")
                )
            )
            cursor.execute(sql_str)
            observations_times_list = cursor.fetchall()
            observations_times = [x[0] for x in observations_times_list]
        cursor.close()
        if observations_times is None or len(observations_times) == 0:
            return None, None
        observation_start = observations_times[0].lower
        observation_end = observations_times[len(observations_times) - 1].upper

        return observation_start, observation_end

    def calculate_ephemeris_time(self, spec):
        latitude = spec.header["OBS_LAT"]
        longitude = spec.header["OBS_LON"]
        obs_location = ephem.Observer()
        obs_location.lat = str(latitude)
        obs_location.lon = str(longitude)

        # Calculate the sunrise and sunset times.
        observation_date = datetime.datetime.strptime(spec.header['DATE-OBS'], '%Y/%m/%d').date()
        observation_times = (observation_date + spec.start.time(), observation_date + spec.end.time())

        try:
            sunrise = ephem.localtime(obs_location.previous_rising(ephem.Sun())).time()
            sunset = ephem.localtime(obs_location.next_setting(ephem.Sun())).time()

            sunrise_datetime = datetime.datetime.combine(datetime.datetime.min, sunrise)
            sunset_datetime = datetime.datetime.combine(datetime.datetime.min, sunset)

        except ephem.AlwaysUpError:
            # Provide default values when the sun is always above the horizon
            sunrise = datetime.time(0, 0, 0)
            sunset = datetime.time(23, 59, 59)

            # Calculate the duration of daylight in hours.
        duration = (sunset.hour + sunset.minute / 60) - (sunrise.hour + sunrise.minute / 60)

        # Switch sunrise and sunset if the duration is negative
        if duration < 0:
            sunrise, sunset = sunset, sunrise
            duration *= -1

        obs_start_utc = spec.start.astimezone(pytz.utc)
        obs_end_utc = spec.end.astimezone(pytz.utc)

        # Store the observation times and ephemeris times for the station
        max_observation_time = (sunset_datetime - sunrise_datetime)
        actual_observation_time = (obs_end_utc - obs_start_utc)

        self.observation_data[spec.header['INSTRUME']] = {
            'observation_times': observation_times,
            'ephemeris_times': (sunrise.strftime('%H:%M:%S'), sunset.strftime('%H:%M:%S')),
            'duration': (max_observation_time - actual_observation_time)
        }

        # Return obs_lon, obs_lat, ephemeris_start, and ephemeris_end
        return longitude, latitude, sunrise, sunset, round(duration, 2)

    def process_stations(self):
        # Retrieve all instruments from the database
        rows = self.get_all_instruments()

        # Process each row
        for row in rows:
            spec = CallistoSpectrogram.read(ecallisto_config.DATA_PATH + row[6])

            # Call the method to calculate the ephemeris time for a given station
            longitude, latitude, sunrise, sunset, duration = self.calculate_ephemeris_time(spec)

            # Prepare the observation data for insertion or update
            data = {
                'instrument': spec.header['INSTRUME'],
                'observation_times': (spec.start, spec.end),
                'ephemeris_times': (sunrise.strftime('%H:%M:%S'), sunset.strftime('%H:%M:%S')),
                'duration': duration
            }

            # Insert or update the observation data in the database
            self.insert_or_update_observation_data(data)

            # Print the observation times and ephemeris times for each station
            print(f"Station: {spec.header['INSTRUME']}")
            print(f"Observation Times: {data['observation_times']}")
            print(f"Ephemeris Times: {data['ephemeris_times']}")
            print(f"Duration: {data['duration']}")
            print()

    print("Data processing completed.")

    def insert_or_update_observation_data(self, data):
        try:
            # Connect to the MySQL database
            conn = psycopg2.connect(
                host=ecallisto_config.DB_HOST,
                user=ecallisto_config.DB_USER,
                database=ecallisto_config.DB_DATABASE,
                port=ecallisto_config.DB_PORT,
                password=ecallisto_config.DB_PASSWORD
            )

            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()

            # Check if the instrument already exists in the table
            instrument = data['instrument']
            query = "SELECT * FROM observation_data WHERE instrument = %s"
            cursor.execute(query, (instrument,))
            result = cursor.fetchone()

            if result:
                # Instrument exists, update the row
                update_query = """
                        UPDATE observation_data
                        SET observation_start = %s, observation_end = %s,
                            sunrise_time = %s, sunset_time = %s, duration = %s
                        WHERE instrument = %s
                    """
                cursor.execute(update_query, (
                    data['observation_times'][0],
                    data['observation_times'][1],
                    data['ephemeris_times'][0],
                    data['ephemeris_times'][1],
                    data['duration'],
                    instrument
                ))
            else:
                # Instrument does not exist, insert a new row
                insert_query = """
                        INSERT INTO observation_data (instrument, observation_start, observation_end,
                                                      sunrise_time, sunset_time, duration)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                cursor.execute(insert_query, (
                    instrument,
                    data['observation_times'][0],
                    data['observation_times'][1],
                    data['ephemeris_times'][0],
                    data['ephemeris_times'][1],
                    data['duration']
                ))

            # Commit the changes to the database
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            print("Data inserted or updated successfully!")
        except mysql.connector.Error as error:
            print(f"Error inserting or updating data: {error}")


update_station = UpdateStation()
update_station.process_stations()
