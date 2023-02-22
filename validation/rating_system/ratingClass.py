import sys
import astropy.io.fits
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt
import os

PATH_PREFIX = '/data'
DATA_PATH = os.path.join(PATH_PREFIX, 'radio/2002-20yy_Callisto')

DB_HOST = 'localhost'
DB_DATABASE = 'validation_ecallisto'
DB_USER = 'postgres'
DB_PASSWORD = 'ecallistohackorange'
DB_PORT = '5432'

class Rating:
    def __init__(self):
        self.database = self.get_db()

    def get_db(self):
        """ Connect to the database"""
        return psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            database=DB_DATABASE,
            port=DB_PORT,
            password=DB_PASSWORD
        )

    def get_all_instruments(self, sql_query):
        """ Get all data from the database"""
        cursor = self.database.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql_query)
        instruments = [row for row in cursor.fetchall()]
        return instruments

    def rating_with_files(self):
        """ Evaluate files according to their file names"""
        sql_query = "SELECT * FROM validation_data WHERE snr_values IS NOT NULL ORDER BY snr_values DESC;"
        rows = self.get_all_instruments(sql_query)
        while True:
            name = input("Enter the file name: ")
            if name == "Stop":
                break
            else:
                for row in rows:
                    if name == row[2]:
                        print(f"The file name {name} got {row[9] * '*'}")

    def files_with_stars(self, start_time, end_time):
        """ Get a list of filenames evaluated with stars"""
        sql_query = f"SELECT file_name, snr_rating FROM validation_data WHERE start_time BETWEEN '{start_time}' AND '{end_time}' ORDER BY snr_rating DESC;"
        pd.set_option('display.max_rows', None)
        df = pd.read_sql_query(sql_query, self.database)
        print(df)

    def avg_stations_with_stars(self, start_time, end_time):
        """ Get the average rating of stations with stars"""
        sql_query = f"SELECT instrument_name, AVG(snr_rating) AS avg_rating FROM validation_data WHERE start_time BETWEEN '{start_time}' AND '{end_time}' GROUP BY instrument_name ORDER BY avg_rating DESC;"
        pd.set_option('display.max_rows', None)
        df = pd.read_sql_query(sql_query, self.database)
        df["avg_rating"] = df["avg_rating"].round(decimals=0)
        print(df)

    def rating_with_stations(self, name):
        """ Get the rating of a specific station"""
        sql_query = "SELECT instrument_name, AVG(snr_rating) AS avg_rating FROM validation_data GROUP BY instrument_name, snr_rating ORDER BY snr_rating DESC;"
        pd.set_option('display.max_rows', None)
        df = pd.read_sql_query(sql_query, self.database)
        df["avg_rating"] = df["avg_rating"].round(decimals=0)
        for index, row in df.iterrows():
            if name == row[0]:
                print(f"The station {row[0]} got {int(row[1])} ")

    def snr_values(self):
        """ Get a list of SNR values from the database"""
        sql_query = "SELECT instrument_name, snr_values FROM validation_data WHERE snr_values IS NOT NULL GROUP BY instrument_name, snr_values ORDER BY snr_values DESC;"

        rows = self.get_all_instruments(self.database, sql_query)
        list_of_snr = []
        for row in rows:
            list_of_snr.append(row[1])

        return list_of_snr


    def convert_to_stars(self, score):
        ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Compute the percentile of the data
        percent = np.percentile(score, [0, 25, 50, 75, 100] )
        rating = np.interp( score, percent, ranking )
        rating = np.round(rating, 1)

        return rating
    
    def get_star_scoring(self, start_time, end_time):
        database = self.get_db()
        database.cursor()

        sql_query ="select instrument_name, avg(snr_values) as avg_snr, avg(std_values) as avg_std  from validation_data where start_time between '%s' AND '%s' group by instrument_name order by avg_snr desc ;" % (start_time, end_time)
        pd.set_option('display.max_rows', None)
        df = pd.read_sql_query(sql_query , database )

        # round the decimal to 2 digits
        df["avg_snr"] = df["avg_snr"].round( decimals=2 )
        df["avg_std"] = df["avg_std"].round( decimals=2 )

        # adding new columns to the df with the function "convert_to_stars" as values
        df["snr_rating"] = self.convert_to_stars(df["avg_snr"])
        df["std_rating"] = self.convert_to_stars( df["avg_std"] )

        # converting the values to stars *
        df["snr_stars"] = [int( star ) * "*" for star in df["snr_rating"]]

        print(df)
