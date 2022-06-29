from validation import *
print("Start")
#sql_query = "Select stations.station_name,avg(fits.std) as std_avg, avg(fits.snr) as snr_avg, stations.duration From stations left join instruments on stations.id= instruments.fk_station left join virtual_instruments on stations.id = virtual_instruments.fk_instrument left join fits on stations.id  = fits.fk_virtual_instrument where snr is not null Group by stations.station_name, stations.duration order by snr_avg desc ;"
sql_query = "select * from validation_data where snr_values is not null order by snr_values desc ;"

def get_db():
    database = psycopg2.connect(host=test_config.DB_HOST,
                                user=test_config.DB_USER,
                                database=test_config.DB_DATABASE,
                                port=test_config.DB_PORT,
                                password=test_config.DB_PASSWORD)

    return database


database = get_db()

def get_all_instruments(database, sql_query):

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    instruments = [row for row in cursor.fetchall()]

    return instruments, cursor


rows, cursor = get_database(database, sql_query)

def convert_to_stars(score):
    ranking=[1.0,2.0,3.0,4.0,5.0]
    list_of_stars=[]
    percent=np.percentile(score,[0,25,50,75,100])

    ratings=np.interp(score,percent,ranking)

    for rating in ratings:
        list_of_stars.append(int(rating))

    return list_of_stars


list_of_snr = []

for row in rows:
   list_of_snr.append(row[7])

ratings = convert_to_stars(list_of_snr)

for rate, row in zip(ratings, rows):

    sql_update_query = f"""UPDATE validation_data SET snr_rating = {rate} where id = {row[0]} """

    cursor.execute( sql_update_query )
    database.commit()

print("Done")


