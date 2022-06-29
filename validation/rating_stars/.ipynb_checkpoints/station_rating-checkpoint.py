import sys
import astropy.io.fits
import numpy as np
import psycopg2.extras
import psycopg2
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt
from validation import get_db, get_database
sys.path.append('../')
import config as validation_config




sqlquery = "select * from validation_data where snr_values is not null order by snr_values desc ;"


database = get_db()
rows, cursor = get_database(database, sqlquery)


# 5 stars means best station
# 1 star means bad station
def rating():
    while True:
        name = input( "Enter the file name: " )
        if name == "Stop":
            break
        else:
            for row in rows:
                #file_name = os.path.basename( row[2])
                file_name = row[2]
                if name == file_name:
                    print( f"The file name {file_name} got {row[9]*'*'}")

#rating()

def stations_with_stars(start_time, end_time):
    database = psycopg2.connect(host=validation_config.DB_HOST,
                                user=validation_config.DB_USER,
                                database=validation_config.DB_DATABASE,
                                port=validation_config.DB_PORT,
                                password=validation_config.DB_PASSWORD)
    cursor = database.cursor()
    sql_query ="select file_name, snr_rating from validation_data where start_time between '%s' AND '%s' order by snr_rating desc ;" % (start_time, end_time)
    pd.set_option('display.max_rows', None)
    df = pd.read_sql_query(sql_query , database )

    return df


print(stations_with_stars('2017-09-06 09:15:00','2017-09-06 09:30:00'))