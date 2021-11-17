from packages.modules import *
import packages.config as test_config


def signal_to_noise(arr):
    """Calculate the signal-to-noise ratio of the input data.
    :param array_like arr: an array_like object contain the data.
    :returns: The signal-to-noise ratio of {Arr}, here defined as the mean divided by the standard deviation.
    :rtype: float
    """

    m = arr.mean()
    std = arr.std()
    return m / std


def get_abs_data(arr):
    """Get the absolute values from the arrays.
    :param float arr: the data in the arrays from the spectrograms.
    :returns: Return an array with absolute values.
    :rtype: float.
    """
    abs_data = np.absolute(arr.data.flatten())
    return abs_data


def get_min_data(data1, data2):
    """Get the minimum value from the both data1 and data2.
    :param float * data1 : the data from spectrogram using the function 'Constbacksub + elimwrongchannels'
    :param float * data2 : the data from spectrogram using the function  'subtract_bg_sliding_window'
    :returns: Return the minimum values from data1, data2
    :rtype: float.
    """
    min_value = int(min(np.nanmin(data1), np.nanmin(data2)))
    return min_value


def get_max_data(data1, data2):
    """Get the maximum value from the both data1 and data2.
     :param float data1 : the data from spectrogram using the function 'Constbacksub + elimwrongchannels'
     :param float data2 : the data from spectrogram using the function  'subtract_bg_sliding_window'
     :returns: Return the maximum values from data1, data2
     :rtype: float.
     """
    max_value = int(max(np.nanmax(data1), np.nanmax(data2)))
    return max_value


def move_axes(fig, ax_source, ax_target):
     """ To move the axes to create a new Figure. """
        
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
