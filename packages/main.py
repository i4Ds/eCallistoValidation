from modules import *

def get_connection_db():
    connection = psycopg2.connect(host=test_config.DB_HOST,
                                   database=test_config.DB_DATABASE,
                                   user=test_config.DB_USER,
                                   port=test_config.DB_PORT,
                                   password=test_config.DB_PASSWORD)
    cursor = connection.cursor()
    return cursor



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


def move_axes(fig, ax_source, ax_target):
    old_fig = ax_source.figure
    ax_source.remove()
    ax_source.figure = fig
    ax_source.set_ylabel('')
    ax_source.set_xlabel('')

    ax_source.set_position(ax_target.get_position())
    ax_target.remove()
    ax_target.set_aspect("equal")
    fig.axes.append(ax_source)
    fig.add_subplot(ax_source)

    plt.close(old_fig)



def get_abs_data(Arr):
    """
    Get the absolute values from the arrays.
    Parameters
    ----------
    Arr = the data arrays from the spectrograms

    Returns
    -------
    Return an array with absolute values

    """
    abs_data = np.absolute(Arr.data.flatten())

    return abs_data



def get_min_data(data1, data2):
    """
    Get the minimum from the mentioned data.
    Parameters
    ----------
    data1 : the data from spectrogram using the function 'Constbacksub + elimwrongchannels'
    data2 : the data from spectrogram using the function  'subtract_bg_sliding_window'

    Returns
    -------
    Return the minimum from data1, data2
    """
    min_value = int(min(np.nanmin(data1), np.nanmin(data2)))
    return min_value



def get_max_data(data1, data2):
    """
     Get the maximum from the mentioned data.
    Parameters
    ----------
    data1 : the data from spectrogram using the function 'Constbacksub + elimwrongchannels'
    data2 : the data from spectrogram using the function  'subtract_bg_sliding_window'

    Returns
    -------
    Return the maximum from data1, data2.
    """
    max_value = int(max(np.nanmax(data1), np.nanmax(data2)))
    return max_value