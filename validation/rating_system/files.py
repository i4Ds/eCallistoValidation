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
import requests
# Config :
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))
from radiospectra.sources import CallistoSpectrogram

PATH_PREFIX = '/data'
DATA_PATH = os.path.join(PATH_PREFIX, 'radio/2002-20yy_Callisto')

#database
DB_HOST='localhost'
# DB_DATABASE='validation'
DB_DATABASE='validation_ecallisto'
DB_USER='postgres'
DB_PASSWORD='ecallistohackorange'
DB_PORT='5432'

# 5 stars means best station
# 1 star means bad station
def get_db():
    """ connect to the database"""
    database = psycopg2.connect(host=DB_HOST,
                                user=DB_USER,
                                database=DB_DATABASE,
                                port=DB_PORT,
                                password=DB_PASSWORD)
    return database


def get_all_instruments(database, sql_query):
    """ Get the all data from the database"""

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments


def convert_to_stars(score):
    ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Compute the percentile of the data
    percent = np.percentile( score, [0, 25, 50, 75, 100] )
    rating = np.interp( score, percent, ranking )
    rating = np.round(rating, 2)

    return rating


def get_fits():

    database = get_db()
    database.cursor()
    #sql_query = "Select stations.station_name, fits.snr , fits.observation_times From stations left join instruments on stations.id=instruments.fk_station left join virtual_instruments on stations.id=virtual_instruments.fk_instrument left join fits on stations.id=fits.fk_virtual_instrument where snr is not null Group by stations.station_name, fits.snr , fits.observation_times order by fits.snr desc limit 50 ;"
    sql_query = "Select path, snr from test where snr is not null  order by snr desc limit 10000;"

    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )

    df = df[df['snr'].notna()]
    #print( df["path"].str.split( '[/|_]', expand=True )[4] )
    print( df["path"])

    #df["instrument"] = df["path"].str.split( '[/|_]', expand=True )[4]

   # df["end_time"] = df["observation_times"].str.split( ',', expand=True )[1]
    #df["snr_rating"] = convert_to_stars( df["snr"] )
    #  df['start'] = df.observation_times.str.split( ',', expand=True )[0]
    #df["snr_stars"] = [int( star ) * "*" for star in df["snr_rating"]]

    #df = df.groupby('instrument').mean().round( decimals=2 ).sort_values(by='snr_rating', ascending=False)
    #print(df)

get_fits()

def get_fits_files(start, end):
    database = get_db()
    database.cursor()
    sql_query = "Select * from fits where snr is not null  order by nullif(snr, 'NAN') desc nulls last limit 1000;"
    files = get_all_instruments( database, sql_query)

    data_df = []

    for file in files:
        file_name = os.path.basename( file[6] ).split(".")[0]
        station = re.sub( r"[_\d{8}_\d{6}_\d{2}]",' ' ,file_name )
        start_time= str(file[3]).split(",")[0][1:]
        end_time = str(file[3]).split(",")[1][:-1]
        snr = file[5]


        data ={
            "station":station,
            "start_time" : start_time,
            "end_time" : end_time,
            "snr" : snr
        }
        data_df.append(data)

    df = pd.DataFrame( data_df )
    pd.set_option( 'display.max_rows', None )
    df["snr_rating"] = convert_to_stars( df["snr"] )
    #df = df.groupby('station').mean().round( decimals=2 ).sort_values(by='snr_rating', ascending=False)
    result1 = df.loc[df["start_time"] > start]
    result2 = df.loc[df["start_time"] > end]

    return result1, result2








# print(get_fits_files('2021-01-30 14:45:00','2021-01-21 21:00:00'))


