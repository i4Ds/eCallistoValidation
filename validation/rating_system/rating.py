import os
import re
import sys
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
import config as ecallisto_config
sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))


class Rating:
    """
    Class to get data from the database

    :param start_time: The start time of the data in format 'YYYY-MM-DD HH:MM:SS'
    :param end_time: The end time of the data in format 'YYYY-MM-DD HH:MM:SS'
    """

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.database = self.get_db()

    @staticmethod
    def get_db():
        """
        Get the database connection
        :return: The database connection
        """
        database = psycopg2.connect(host=ecallisto_config.DB_HOST,
                                    user=ecallisto_config.DB_USER,
                                    database=ecallisto_config.DB_DATABASE,
                                    port=ecallisto_config.DB_PORT,
                                    password=ecallisto_config.DB_PASSWORD)
        return database

    def get_all_instruments(self):
        """
        Get all instruments from the database
        :return: The instruments
        """
        sql_query_instruments = f"SELECT path, snr, std, lower(observation_times) AS start_time, upper(observation_times) AS end_time FROM fits WHERE observation_times && tsrange('{self.start_time}', '{self.end_time}') AND snr IS NOT NULL ORDER BY snr DESC;"

        cursor = self.database.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql_query_instruments)
        instruments = [row for row in cursor.fetchall()]
        return instruments

    @staticmethod
    def convert_to_stars(score):
        """
        Convert the score to a rating.
        :param score: The score
        :return: The rating
        """
        ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Compute the percentile of the data
        percent = np.percentile(score, [0, 25, 50, 75, 100])
        rating = np.interp(score, percent, ranking)
        rating = np.round(rating, 2)

        return rating

    @staticmethod
    def extract_station_name(file_path):
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

    def rate_stations(self):
        """
        Rate the stations
        :return: The rating
        """
        instruments = self.get_all_instruments()

        df = pd.DataFrame(instruments, columns=["path", "snr", "std", "start_time", "end_time"])

        df = df[df['snr'].notna()]

        df["station_name"] = df["path"].apply(self.extract_station_name)

        df["snr_rating"] = self.convert_to_stars(df["snr"])
        df["std_rating"] = self.convert_to_stars(df["std"])

        df["counter"] = df["station_name"].tolist()
        values, counts = np.unique(df["counter"], return_counts=True)

        df = df.groupby('station_name', as_index=False).agg({
            'snr': 'mean',
            'std': 'mean',
            'snr_rating': 'mean',
            'std_rating': 'mean'
        }).round(decimals=2).sort_values(by='snr_rating', ascending=False)

        df.columns = ['station_name', 'snr', 'std', 'snr_rating', 'std_rating']

        return df


if __name__ == '__main__':
    start_time = input("Enter start time (YYYY-MM-DD HH:MM:SS): ")
    end_time = input("Enter end time (YYYY-MM-DD HH:MM:SS): ")

    rating = Rating(start_time, end_time)
    df = rating.rate_stations()
    print(df)
