import os
import glob
import sys
import astropy.io.fits
import matplotlib
import numpy as np
import time
import timeit
import skimage.transform

import psycopg2
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import pandas.io.sql as psql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import re
from eCallistoProject import plot_config
import  config as  test_config
module_path = os.path.abspath(os.path.join('radiospectra'))
if module_path not in sys.path:
    sys.path.append(module_path)

import radiospectra

from radiospectra.sources import CallistoSpectrogram

from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf, PdfFile
import datetime
import warnings

warnings.filterwarnings("ignore")


# Source: https://gist.github.com/salotz/8b4542d7fe9ea3e2eacc1a2eef2532c5 by Kushtrim

def get_connect_DB():
    global cursor
    connection = psycopg2.connect(host=test_config.DB_HOST,
                                  database=test_config.DB_DATABASE,
                                  user=test_config.DB_USER,
                                  port=test_config.DB_PORT,
                                  password=test_config.DB_PASSWORD)
    cursor = connection.cursor()


get_connect_DB()




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
