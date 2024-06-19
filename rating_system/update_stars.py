import sys
import numpy as np
import psycopg2.extras
import psycopg2
# Config :
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "radiospectra2"))

PATH_PREFIX = '/data'
DATA_PATH = os.path.join(PATH_PREFIX, 'radio/2002-20yy_Callisto')

# database
DB_HOST = 'localhost'
# DB_DATABASE='validation'
DB_DATABASE = 'validation_ecallisto'
DB_USER = 'postgres'
DB_PASSWORD = 'ecallistohackorange'
DB_PORT = '5432'


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
    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments, cursor


# sql_query = "Select * from fits where snr is not null  order by snr desc limit 1000;"
sql_query = "Select * from stations;"
database = get_db()

rows, cursor = get_all_instruments(database, sql_query)


def convert_to_stars(score):
    ranking = [1.0, 2.0, 3.0, 4.0, 5.0]
    list_of_stars = []
    percent = np.percentile(score, [0, 25, 50, 75, 100])

    ratings = np.interp(score, percent, ranking)

    for rating in ratings:
        list_of_stars.append(int(rating))

    return list_of_stars


list_of_snr = []

for row in rows:
    print(row)


# list_of_snr.append(row[7])
# print(row[7])

# ratings = convert_to_stars(list_of_snr)

# for rate, row in zip(ratings, rows):

#   sql_update_query = f"""UPDATE fits SET rating = {rate} where id = {row[0]}"""


#   cursor.execute( sql_update_query )
#   database.commit()

# print("Done")

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
    percent = np.percentile(score, [0, 25, 50, 75, 100])
    rating = np.interp(score, percent, ranking)
    rating = np.round(rating, 2)

    return rating


database = get_db()

database.cursor()

sql_query = "Select * from fits where snr is not null  order by snr desc limit 1000;"

files = get_all_instruments(database, sql_query)

list_of_snr = []
for file in files:
    list_of_snr.append(file[5])

ratings = convert_to_stars(list_of_snr)

for rate, file in zip(ratings, files):
    sql_update_query = f"""UPDATE fits SET rating = {rate} where id = {file[0]}"""
    cursor.execute(sql_update_query)
    database.commit()

print("Done")
# sql_select_path = """SELECT i.instrument_name, i.origin, i.location, f.id, f.path FROM fits f LEFT JOIN virtual_instruments v ON f.fk_virtual_instrument = v.id LEFT JOIN instruments i ON v.fk_instrument = i.id WHERE %s && f.observation_times AND f.std IS NULL ORDER BY observation_times"""
