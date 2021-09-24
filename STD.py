from main import *

def signal_to_noise(Arr):
    """
    The signal-to-noise ratio of the input data.

    Parameters
    ----------

    Arr : array_like
        an array_like object containing the data.

    Returns
    -------
    The signal-to-noise ratio of `Arr`, here defined as the mean
    divided by the standard deviation.

    """
    Arr = np.asanyarray(Arr)
    m = Arr.mean()
    std = Arr.std()
    return m/std


def standard_deviation(Arr):
    """
    The Standard deviation of the input data.
    Parameters
    ----------
    Arr : array_like
        an array_like object containing the data.

    Returns
    -------
    The standard deviation of `Arr`.
    """
    Arr = np.asanyarray(Arr)
    calculate_std = Arr.std()

    return calculate_std


def get_cursor():
    """
    Select all data from the table "validation_data" to update the Std and Snr values.
    Returns
    -------
    A query of the Table.
    """
    cursor.execute("""SELECT * from validation_data WHERE std is null ORDER BY id""")


def update_values():

    sql_update_query = f"""UPDATE validation_data SET std = {std_data}, snr = {snr_data} where id = {index[0]} """
    cursor.execute(sql_update_query)
    print("Table after Update")
    connection.commit()


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
    The absolute value of data.
    """
    spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                             amount=0.05, change_points=True)
    data = np.absolute(spec2.data.flatten())
    return data


def save_values_db():
    """
    Update the values (std and snr ) into the database (validation).
    """
    global index, data, std_data, snr_data
    for index in cursor.fetchall():
        try:
            spec = get_spec(index)

            print("Table before Update")
            data = flatted_data(spec)

            std_data = standard_deviation(data)
            snr_data = signal_to_noise(data)
            update_values()

        except Exception as err:
            exception_type = type(err).__name__
            print(exception_type, index[1])

