import os
import glob
import sys
import astropy.io.fits
import matplotlib
import numpy as np
import time
import timeit
import skimage.transform
import psycopg2.extras
import psycopg2
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import pandas.io.sql as psql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import re
import packages.config as test_config
from scipy import interpolate
from copy import deepcopy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "radiospectra"))
module_path = os.path.abspath(os.path.join('radiospectra'))
if module_path not in sys.path:
    sys.path.append(module_path)


import radiospectra
from radiospectra.sources import CallistoSpectrogram

from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf, PdfFile
import datetime
import warnings

warnings.filterwarnings("ignore")


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


def get_all_instruments(database, sql_query):
    """Get the all instruments data from the Database.

     :param database: a database 'Validation'.
     :param sql_query: Sql query from the database.
     :returns index: index of the cursor frm database.
     :returns cursor: the cursor frm database.
    """

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall()]

    return index, cursor


def get_plot(rows):
    """Plot 4 columns(original Spec,Background subtracted("constbacksub", "elimwrongchannels"),
        Gliding background subtracted, Histograms.

    :param rows: The rows from the database.
    :returns: 4 columns of the Input spec
    """
    for row in rows:
        try:
            spec = CallistoSpectrogram.read(test_config.DATA_PATH + row[1])
            fig1, axs1 = plt.subplots(1, 4, figsize=(27, 6))
            ax1 = spec.plot()
            ax1.title.set_text("Original Data")
            plt.close()

            # Second column, Constbacksub + elimwrongchannels
            spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
            fig2 = plt.subplots(1, 4, figsize=(27, 6))
            ax2 = spec2.plot()
            ax2.title.set_text("Background subtracted")
            plt.close()

            # Third column, subtract_bg_sliding_window
            spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)
            fig3 = plt.figure(figsize=(27, 6))
            ax3 = spec3.plot()
            ax3.title.set_text(
                "Gliding background subtracted (window=800)")
            plt.close()

            # Fourth column, Histograms
            fig4, ax4 = plt.subplots(figsize=(27, 6))

            # Fourth column, Histograms
            data_absolute3 = get_abs_data(spec2)
            data_absolute4 = get_abs_data(spec3)

            # take the min and max from the data to set the bins.
            min_value = get_min_data(data_absolute3, data_absolute4)
            max_value = get_max_data(data_absolute3, data_absolute4)

            ax4.hist(data_absolute3, histtype='step', bins=range(
                min_value, max_value + 1), label='Background subtracted')
            ax4.hist(data_absolute4, histtype='step', bins=range(
                min_value, max_value + 1), label='Gliding background subtracted')

            # Calculate the standard deviation and signal-to-noise => rounded them to have 3 digits.
            std_data = round(np.std(data_absolute4), 3)
            snr_data = round(signal_to_noise(data_absolute4), 3)

            # Set title for the histograms and show the std/snr values.
            ax4.title.set_text(
                f"Histograms, std = {std_data}, snr = {snr_data}")
            plt.legend()
            plt.close()

            # Plot final plot by moving axes to the figure
            fig_target, (axA, axB, axC, axD) = plt.subplots(
                1, 4, figsize=(30, 9))
            plt.suptitle(fig1._suptitle.get_text())

            move_axes(fig_target, ax1, axA)
            move_axes(fig_target, ax2, axB)
            move_axes(fig_target, ax3, axC)
            move_axes(fig_target, ax4, axD)

            for ax in (ax1, ax2, ax3):
                ax.set_xlabel('Time[UT]')
                ax.set_ylabel('Frequency[MHz]')

            ax4.set_xlabel('Pixel values')
            ax4.set_ylabel('Number of pixels')
            plt.show()
        except Exception as err:

            print(f"The Error message is: {err} and the file name is {row[2]}")
            # print("The Error message is: %s and the file name is %s" % (err, row[2]))


def update_all_values(rows):
    """Calculate the std and snr, then update them into the table in Database.
    :param rows: The rows from the database.
    """
    for row in rows:
        try:
            spec = CallistoSpectrogram.read(test_config.DATA_PATH + row[1])
            spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)

            data = np.absolute(spec2.data.flatten())
            std_data = np.std(data)
            snr_data = signal_to_noise(data)

            sql_update_query = f"""UPDATE data SET std = {std_data}, snr= {snr_data} where id = {row[0]} """
            print(f"std_data: {std_data}")
            print(f"snr_data: {snr_data}")
            cursor.execute(sql_update_query)
            database.commit()

        except Exception as err:
            print(f"The Error message is: {err} and the file name is {row[2]}")


def interpolate2d(spec, overwrite=True):
    """
    Interpolate the input data and it returns a new Spectrogram.

    :param object spec: The original Spectrogram.
    :param bool overwrite: if function interpolated_spec has been called directly,there will be a possibility to overwrite it's current          spectrogram data. 
    :returns: New Spectrogram with the interpolated data.

    """
    spec_copy = deepcopy(spec)

    spec_sub = spec_copy.subtract_bg("constbacksub", "elimwrongchannels")

    # Interpolation
    time_x = spec_sub.time_axis
    freq_y = spec_sub.freq_axis
    data_z = spec_sub.data

    inter_f = interpolate.interp2d(time_x, freq_y, data_z)

    # the Frequency before the Interpolation
    ynew = spec_copy.freq_axis
    znew = inter_f(time_x, ynew)

    # If overwrite= True => it will overwrite the new values into the Spec_sub.

    if overwrite:
        spec_sub.time_axis = time_x
        spec_sub.freq_axis = ynew
        spec_sub.data = znew[::-1]

        # TODO
        # Update the FITS Header history => .header.set('Card_name', 'The content')

        spec_sub.header.set('HISTORY', ': The Interpolate data after using the constbacksub, elimwrongchannels.')

    return spec_sub





