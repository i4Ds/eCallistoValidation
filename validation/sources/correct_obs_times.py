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
from astropy.io import fits

sys.path.append( os.path.join( os.path.dirname( __file__ ), "../..", "radiospectra2" ) )
from radiospectra.sources import CallistoSpectrogram
from collections import Counter




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
    cursor = database.cursor( cursor_factory=psycopg2.extras.DictCursor )
    cursor.execute( sql_query_instruments )
    instruments = [row for row in cursor.fetchall()]

    return instruments, cursor


def update_times(rows, cursor):
    for row in rows:
        try:
            hdulist = astropy.io.fits.open( ecallisto_config.DATA_PATH + row[6] )
            instrument_name = hdulist[0].header['INSTRUME']
            date_obs = hdulist[0].header['DATE-OBS']
            time_obs = hdulist[0].header['TIME-OBS']
            date_end = hdulist[0].header['DATE-END']
            time_end = hdulist[0].header['TIME-END']

            start_time = date_obs + " " + time_obs[:8]
            end_time = date_end + " " + time_end

            # start_time = __to_timestamp( date_obs, time_obs[:8] )
            start_timestamp = pd.Timestamp( start_time ).to_julian_date()
            end_timestamp = pd.Timestamp( end_time ).to_julian_date()
            print( end_timestamp )

            sql_update_query = f""" UPDATE validation_ecallisto.public.test SET "start" = {start_timestamp}, "end" = {end_timestamp} where id = {row[0]}"""

            cursor.execute( sql_update_query )
            database.commit()

        except Exception as err:
            # print(f"The Error message is: {err} and the file name is {row[2]}")
            print( f"The Error message is: {err} and the station name is {instrument_name}" )

        print( f"{instrument_name} is updated!" )


if __name__ == '__main__':
    data_base = get_db()
    sql_query = "select * from validation_ecallisto.public.test limit 10;"
    rows, cursor = get_all_instruments( data_base, sql_query )
    update_times( rows, cursor )
