import os
import io
import glob
import sys
import astropy.io.fits
import matplotlib
import numpy as np
import time

import skimage.transform

import psycopg2

import pandas as pd
import pandas.io.sql as psql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

from eCallistoProject import plot_config

module_path = os.path.abspath(os.path.join('radiospectra'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
import radiospectra

from radiospectra.sources import CallistoSpectrogram

from matplotlib.backends.backend_pdf import PdfPages

import warnings
warnings.filterwarnings("ignore")

path = 'R:\\radio\\2002-20yy_Callisto\\2017\\09'

connection = psycopg2.connect(user="postgres",
                              password="ecallistohackorange",
                              host="localhost",
                              port="5432",
                              database="validation")

cursor = connection.cursor()

print("Table Before updating record ")

cursor.execute("""SELECT * from ecallisto WHERE std is null ORDER BY id""")

for file in cursor.fetchall():
    full_path = os.path.join(path, file[1])
    try:
        spec = CallistoSpectrogram.read(full_path)

        spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                 amount=0.05, change_points=True)
        spec_std = spec2.data.std()

        sql_update_query = f"""UPDATE ecallisto_data SET std = {spec_std} where id = {file[0]} """ 

        cursor.execute(sql_update_query)

        connection.commit()

    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type, file[1])

