import sys
import astropy.io.fits
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt
sys.path.append('../')
import config as validation_config


# 5 stars means best station
# 1 star means bad station
def get_db():
    """ connect to the database"""
    database = psycopg2.connect(host=validation_config.DB_HOST,
                                user=validation_config.DB_USER,
                                database=validation_config.DB_DATABASE,
                                port=validation_config.DB_PORT,
                                password=validation_config.DB_PASSWORD)
    return database


def get_all_instruments(database, sql_query):
    """ Get the all data from the database"""

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments


def rating_with_files():
    """ To evaluate the files according to the file names"""

    sql_query = "select * from validation_data where snr_values is not null order by snr_values desc ;"
    database = get_db()
    rows = get_all_instruments( database, sql_query )

    while True:
        name = input( "Enter the file name: " )
        if name == "Stop":
            break
        else:
            for row in rows:
                if name == row[2]:
                    print( f"The file name {name} got {row[9]*'*'}")

#rating_with_files()


def files_with_stars(start_time, end_time):
    """To get  a list of filenames evaluated with stars"""

    database = get_db()
    cursor = database.cursor()
    sql_query ="select file_name, snr_rating from validation_data where start_time between '%s' AND '%s' order by snr_rating desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )

    print(df)

#files_with_stars('2017-09-06 09:15:00','2017-09-06 09:30:00')

def avg_stations_with_stars(start_time, end_time):

    database = get_db()
    cursor = database.cursor()
    sql_query ="select instrument_name, avg(snr_rating) as avg_rating  from validation_data where start_time between '%s' AND '%s' group by instrument_name order by avg_rating desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df["avg_rating"] = df["avg_rating"].round( decimals=0 )

    print(df)

#avg_stations_with_stars('2017-09-01 09:15:00','2017-09-03 09:30:00')
#print("\n")
#avg_stations_with_stars('2017-09-03 09:15:00','2017-09-06 09:30:00')

def rating_with_stations(name):
    database = get_db()
    sql_query = "SELECT instrument_name , avg(snr_rating) as avg_rating from validation_data group by instrument_name, snr_rating order by snr_rating desc;"
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df["avg_rating"] = df["avg_rating"].round( decimals=0 )

    for index, row in df.iterrows():
        if name == row[0]:
            print( f"The station {row[0]} got {int(row[1])} " )


# rating_with_stations("AUSTRIA")

def snr_values():
    database = get_db()
    cursor = database.cursor()

    sql_query = "select instrument_name, snr_values from validation_data where snr_values is not null group by instrument_name,snr_values order by snr_values desc;"
    rows = get_all_instruments( database, sql_query )
    list_of_snr = []
    for row in rows:
        list_of_snr.append(row[1])

    return list_of_snr


def convert_to_stars(score):
    ranking = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Compute the percentile of the data
    percent = np.percentile( score, [0, 25, 50, 75, 100] )
    rating = np.interp( score, percent, ranking )
    rating = np.round(rating, 1)

    return rating


def get_star_scoring(start_time, end_time):
    database = get_db()
    database.cursor()
    sql_query ="select instrument_name, avg(snr_values) as avg_snr, avg(std_values) as avg_std  from validation_data where start_time between '%s' AND '%s' group by instrument_name order by avg_snr desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )
    df["avg_snr"] = df["avg_snr"].round( decimals=2 )
    df["avg_std"] = df["avg_std"].round( decimals=2 )

    df["snr_rating"] = convert_to_stars(df["avg_snr"])
    df["std_rating"] = convert_to_stars( df["avg_std"] )

    print(df)

#get_star_scoring('2017-09-01 09:15:00','2017-09-30 09:30:00')




