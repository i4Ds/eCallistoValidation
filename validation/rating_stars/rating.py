import sys
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt

import config as ecallisto_config
import os


sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))
from radiospectra.sources import CallistoSpectrogram
from collections import Counter


class Rating:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.database = self.get_db()

    def get_db(self):
        """Connect to the database"""
        database = psycopg2.connect(host=ecallisto_config.DB_HOST,
                                    user=ecallisto_config.DB_USER,
                                    database=ecallisto_config.DB_DATABASE,
                                    port=ecallisto_config.DB_PORT,
                                    password=ecallisto_config.DB_PASSWORD)
        return database

    def get_all_instruments(self):
        """Get all data from the database"""
        sql_query_instruments = f"SELECT path, snr, std FROM test WHERE start_time BETWEEN '{self.start_time}' AND '{self.end_time}' AND snr IS NOT NULL ORDER BY snr DESC;"
        cursor = self.database.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql_query_instruments)
        instruments = [row for row in cursor.fetchall()]
        return instruments

    def convert_to_stars(self, score):
        ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Compute the percentile of the data
        percent = np.percentile(score, [0, 25, 50, 75, 100])
        rating = np.interp(score, percent, ranking)
        rating = np.round(rating, 2)

        return rating

    def rate_stations(self):
        instruments = self.get_all_instruments()

        df = pd.DataFrame(instruments, columns=["path", "snr", "std"])

        df = df[df['snr'].notna()]

        df["station_name"] = df["path"].str.split('[/|_]', expand=True)[4]

        df["snr_rating"] = self.convert_to_stars(df["snr"])
        df["std_rating"] = self.convert_to_stars(df["std"])

        df["counter"] = df["station_name"].tolist()
        values, counts = np.unique(df["counter"], return_counts=True)

        df = df.groupby('station_name').mean().round(decimals=2).sort_values(by='snr_rating', ascending=False)
        df["number_of_files"] = counts

        return df[["snr", "snr_rating", "std", "std_rating", "number_of_files"]]



if __name__ == '__main__':
    rating = Rating('2021-09-08 08:00:00', '2021-09-08 18:45:00')
    df = rating.rate_stations()
    print(df)
