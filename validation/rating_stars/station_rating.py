import sys
import astropy.io.fits
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt
from validation import  get_database
sys.path.append('../')
import config as validation_config




# 5 stars means best station
# 1 star means bad station
def get_db():
    database = psycopg2.connect(host=validation_config.DB_HOST,
                                user=validation_config.DB_USER,
                                database=validation_config.DB_DATABASE,
                                port=validation_config.DB_PORT,
                                password=validation_config.DB_PASSWORD)
    return database

def get_all_instruments(database, sql_query):

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments


def rating_with_files():

    sql_query = "select * from validation_data where snr_values is not null order by snr_values desc ;"
    database = get_db()
    rows, cursor = get_database( database, sql_query )

    while True:
        name = input( "Enter the file name: " )
        if name == "Stop":
            break
        else:
            for row in rows:
                if name == row[2]:
                    print( f"The file name {name} got {row[9]*'*'}")


rating_with_files()





def stations_with_stars(start_time, end_time):
    cursor = database.cursor()
    sql_query ="select file_name, snr_rating from validation_data where start_time between '%s' AND '%s' order by snr_rating desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )

    return df


#print(stations_with_stars('2017-09-06 09:15:00','2017-09-06 09:30:00'))

def avg_stations(start_time, end_time):
    database = psycopg2.connect(host=validation_config.DB_HOST,
                                user=validation_config.DB_USER,
                                database=validation_config.DB_DATABASE,
                                port=validation_config.DB_PORT,
                                password=validation_config.DB_PASSWORD)
    cursor = database.cursor()
    sql_query ="select instrument_name, avg(snr_rating) as avg_rating  from validation_data where start_time between '%s' AND '%s' group by instrument_name order by avg_rating desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df["avg_rating"] = df["avg_rating"].round( decimals=0 )

    return df

#print(avg_stations('2017-09-01 09:15:00','2017-09-03 09:30:00'))


def rating_with_stations(name):

    database = psycopg2.connect(host=validation_config.DB_HOST,
                                user=validation_config.DB_USER,
                                database=validation_config.DB_DATABASE,
                                port=validation_config.DB_PORT,
                                password=validation_config.DB_PASSWORD)
    # cursor = database.cursor()


    sql_query = "SELECT instrument_name , avg(snr_rating) as avg_rating from validation_data group by instrument_name, snr_rating order by snr_rating desc;"
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df["avg_rating"] = df["avg_rating"].round( decimals=0 )

    for index, row in df.iterrows():
        if name == row[0]:
            print( f"The station {row[0]} got {row[1]} star" )



# rating_with_stations("AUSTRIA")