from validation import *

sql_query = "select * from validation_data"


database = psycopg2.connect(host=test_config.DB_HOST,
                            user=test_config.DB_USER,
                            database=test_config.DB_DATABASE,
                            port=test_config.DB_PORT,
                            password=test_config.DB_PASSWORD)



def get_database(database, sql_query):
    """
    Get the all instruments from the Database
    Parameters
    ----------
    database : a database 'Validation'.
    sql_query: a query of sql to execute the script.
    Returns
    -------
    index : index of the cursor from database.
    """

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall()]

    return index, cursor


rows, cursor = get_database(database, sql_query)

def update_all_values(rows):
    """
    Calculate the std and snr, then update them into the table in Database.
    Returns
    -------
    None
    """

    for row in rows:
        try:
            spec = CallistoSpectrogram.read(test_config.DATA_PATH + row[1])
            file_name = row[1].split("/")[4]


            spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)

            data = np.absolute(spec2.data.flatten())
            std_data = np.std(data)
            mean_data = np.mean(data)
            snr_data = mean_data / std_data

            sql_update_query = f"""UPDATE validation_data SET std_values = {std_data}, snr_values = {snr_data} where id = {row[0]} """
            cursor.execute(sql_update_query)
            database.commit()

        except Exception as err:
            # print(f"The Error message is: {err} and the file name is {row[2]}")
            print(f"The Error message is: {err} and the file name is {file_name}")

        print(f"{file_name} is updated!")


# update_all_values(rows)



def update_max_over_mean(rows):
    """
    Calculate the std and snr, then update them into the table in Database.
    Returns
    -------
    None
    """

    for row in rows:
        try:
            spec = CallistoSpectrogram.read(test_config.DATA_PATH + row[1])
            file_name = row[1].split("/")[4]


            spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)

            data = np.absolute(spec2.data.flatten())
            max_data = np.max(data)
            std_data = np.std(data)
            mean_data = np.mean(data)
            snr_data = mean_data / std_data
            print(snr_data)
            max_mean_data = max_data / mean_data
            print(max_mean_data)

            sql_update_query = f"""UPDATE validation_data SET snr_values = {snr_data}, max_mean_val = {max_mean_data} where id = {row[0]} """
            cursor.execute(sql_update_query)
            database.commit()

        except Exception as err:
            # print(f"The Error message is: {err} and the file name is {row[2]}")
            print(f"The Error message is: {err} and the file name is {file_name}")

        print(f"{file_name} is updated!")

update_max_over_mean(rows)