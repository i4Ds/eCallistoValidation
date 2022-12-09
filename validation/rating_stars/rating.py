import sys
import astropy.io.fits
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt
import re
import datetime
import math
import mpu
import config as ecallisto_config
import os
import skyfield

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))
from radiospectra.sources import CallistoSpectrogram
from collections import Counter


# 5 stars means best station
# 1 star means bad station


def get_db() :
    """ connect to the database"""
    database = psycopg2.connect( host=ecallisto_config.DB_HOST,
                                 user=ecallisto_config.DB_USER,
                                 database=ecallisto_config.DB_DATABASE,
                                 port=ecallisto_config.DB_PORT,
                                 password=ecallisto_config.DB_PASSWORD )
    return database


def get_all_instruments(database, sql_query):
    """ Get the all data from the database"""

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments


#get_all_instruments(database)

# this function convert the values to ranking system between 1 to 5
def convert_to_stars(score):
    ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Compute the percentile of the data
    percent = np.percentile( score, [0, 25, 50, 75, 100] )
    rating = np.interp( score, percent, ranking )
    rating = np.round(rating, 2)

    return rating

## this rating function uses the quantile normalization to sort the data into different bins =>  every bin represents a certain rating (between  1 and  5)
def rate_stations(start_time, end_time):

    database = get_db()
    database.cursor()
    sql_query = "Select path, snr,std from test where start_time between '%s' And '%s' and  snr is not null order by snr desc;" % (start_time, end_time)


    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df = df[df['snr'].notna()]

    df["station_name"] = df["path"].str.split( '[/|_]', expand=True )[4]

    df["snr_rating"] = convert_to_stars( df["snr"] )
    df["std_rating"] = convert_to_stars( df["std"] )

    df["counter"] = df["station_name"].tolist()
    values, counts = np.unique( df["counter"], return_counts=True )

    df = df.groupby( 'station_name' ).mean().round( decimals=2 ).sort_values( by='snr_rating', ascending=False )
    #df["snr_stars"] = [math.ceil( star ) * "*" for star in df["snr_rating"]]
    #df["std_stars"] = [math.ceil( star ) * "*" for star in df["std_rating"]]
    df["number_of_files"] = counts

    print(df[["snr","snr_rating", "std", "std_rating" , "number_of_files"]])



if __name__ == '__main__':

    rate_stations('2021-09-08 08:00:00', '2021-09-08 18:45:00')




