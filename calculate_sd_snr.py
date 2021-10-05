from packages.modules import *
from packages.main import *


def get_connection():
    global connection, cursor
    connection = psycopg2.connect(host=test_config.DB_HOST,
                                  database=test_config.DB_DATABASE,
                                  user=test_config.DB_USER,
                                  port=test_config.DB_PORT,
                                  password=test_config.DB_PASSWORD)
    cursor = connection.cursor()

    return connection, cursor


def get_cursor():
    get_connection()
    cursor.execute("""SELECT * from data WHERE std is null ORDER BY id""")


def get_spec(index):
    """
    Using CallistoSpectrogram.read to read the path.
    Parameters
    ----------
    index : index of specific column to get the right path
    Returns
    -------
    A spectrogram
    """
    spec = CallistoSpectrogram.read(test_config.DATA_PATH + index[1])
    return spec

def flatted_data(spec):
    """
    Take the spectrogram and subtract the background using the function 'subtract_bg_sliding_window'
    Parameters
    ----------
    spec: A spectrogram.
    Returns
    -------
    The absolute value of the data.
    """
    spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                             amount=0.05, change_points=True)
    data = np.absolute(spec2.data.flatten())
    return data

def calculate_values(index):
    """
    Calculate the std and snr, then update them into the table in Database.
    Parameters
    ----------
    index : index of data in the cursor

    Returns
    -------
    Update the values into DB.
    """
    spec = get_spec(index)
    data = flatted_data(spec)
    std_data = standard_deviation(data)
    snr_data = signal_to_noise(data)
    sql_update_query = f"""UPDATE data SET std = {std_data}, snr= {snr_data} where id = {index[0]} """
    cursor.execute(sql_update_query)
    connection.commit()



def save_values_db():
    """
    Update the values (std and snr ) into the database (validation).
    """
    get_cursor()
    for index in cursor.fetchall():
        try:
            calculate_values(index)

        except Exception as err:
            print(err)
            exception_type = type(err).__name__
            print(exception_type, index[1])


if __name__ == "__main__":
    save_values_db()


