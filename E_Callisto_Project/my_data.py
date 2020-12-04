import os
import glob
import astropy.io.fits
import iso8601
import numpy as np
import datetime
import re
import mysql.connector
import pandas as pd
import sunpy.data.sample
from sqlalchemy import create_engine
import sqlite3
from time import gmtime, strftime

import os
import sys

top_dir = os.path.split(os.path.realpath('.'))[0]
top_dir = 'C:\\Users\\delbe\\OneDrive\\Desktop\\i4ds\\radiospectra'
if top_dir != sys.path[0] and top_dir != sys.path[1]:
    sys.path.insert(1, top_dir)
path_to_import = os.path.abspath(top_dir + os.sep + "radiospectra")
print(path_to_import)

import radiospectra

if path_to_import != os.path.abspath(radiospectra.__path__[0]):
    print(f'Module to import: {path_to_import}')
    print(f'Module that was imported: {os.path.abspath(radiospectra.__path__[0])}')
    raise Exception('Wrong radiospectra module was imported. (not local)')
else:
    print(f'Imported local radiospectra from: {os.path.abspath(radiospectra.__path__[0])}')
from radiospectra.sources import CallistoSpectrogram

import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (25, 10)

path = 'R:\\radio\\2002-20yy_Callisto\\2020\\10\\07'


###################################################

def get_db_dataframe():
    engine = create_engine("mysql+pymysql://" + 'root' + ":" 
                           + 'delberin1992' + "@" + 'localhost' 
                           + "/" + 'ecallisto_DB')

    # from sql to DataFrame (pandas)

    SQL_Query = pd.read_sql_query('''SELECT * 
                                  FROM e_callisto
                                  WHERE start_time AND end_time
                                  BETWEEN '2020-10-07 08:30:00' AND '2020-10-07  09:15:00'  GROUP BY start_time;''',
                                  engine)

    ecallisto_data_frame = pd.DataFrame(SQL_Query)

    return ecallisto_data_frame 

###################################################

def get_instrument_name():
    """Return a List of Instrument's names from ecallisto_sql_query table"""
    
    ecallisto_data_frame = get_db_dataframe()

    list_of_names = set()

    for name in ecallisto_data_frame['Instrument_name']:
        list_of_names.add(name)

    return list_of_names


###################################################

def get_file_name():
    """Return a List of File's names from ecallisto_sql_query table """   
    ecallisto_data_frame = get_db_dataframe()

    list_of_file_names = set()

    for name in ecallisto_data_frame['File_name']:
        list_of_file_names.add(name)

    return list_of_file_names


###################################################


def get_callisto_spec():
    """Return a spectrogram from ecallisto_sql_query table"""   
    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:
        full_path = os.path.join(path, file)
        spec = CallistoSpectrogram.read(full_path)

        spec_plot = spec.peek()

    return spec_plot


###################################################


def avg_of_std():
    std_of_instrument = {}

    ecallisto_data_frame = get_db_dataframe()

    list_of_names = get_instrument_name()

    for instr_name in list_of_names:

        file_of_name = []

        for index, row in ecallisto_data_frame.iterrows():

            if row["Instrument_name"] == instr_name:
                file_of_name.append(row["File_name"])

        list_of_std = []

        for file in file_of_name:
            full_path = os.path.join(path, file)
            spec = CallistoSpectrogram.read(full_path)

            array_std = spec.data.std()
            list_of_std.append(array_std)

        avg_of_std = sum(list_of_std) / len(list_of_std)
        round_of_std = round(avg_of_std, 2)

        std_of_instrument.update({instr_name: round_of_std})

    return std_of_instrument


###################################################

def get_single_array_hist(file_name):
    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:

        if file == file_name:
            full_path = os.path.join(path, file)
            spec = CallistoSpectrogram.read(full_path)

            array = spec.data.data.flatten()

            return plt.hist(array)

    return None


###################################################


def get_hist_same_instrument(instrument_name):
    ecallisto_data_frame = get_db_dataframe()

    file_of_name = []

    for index, row in ecallisto_data_frame.iterrows():

        if row["Instrument_name"] == instrument_name:
            file_of_name.append(row["File_name"])

    list_of_arrays = []

    for name in file_of_name:
        full_path = os.path.join(path, name)
        spec = CallistoSpectrogram.read(full_path)

        array = spec.data.data.flatten()
        list_of_arrays.append(array)

    array_conc = np.concatenate(list_of_arrays)

    return plt.hist(array_conc)


###################################################

def get_all_arrays_hist():
    list_of_hist = []

    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:
        full_path = os.path.join(path, file)
        spec = CallistoSpectrogram.read(full_path)

        array = spec.data.data.flatten()

        list_of_hist.append(array)

    array_conc = np.concatenate(list_of_hist)

    array_plot = plt.hist(array_conc)

    return array_plot


###################################################


def get_single_delta(file_name):
    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:

        if file == file_name:
            full_path = os.path.join(path, file)

            hdulist = astropy.io.fits.open(full_path)
            c_delta = hdulist[0].header['CDELT1']

            return c_delta

    return None


###################################################


def get_single_delta_spec(spec):
    c_delta = spec.header['CDELT1']

    return c_delta


################################################### 

def get_list_of_specs():
    ecallisto_data_frame = get_db_dataframe()
    
    list_of_specs = []

    for file in ecallisto_data_frame['File_name']:
        full_path = os.path.join(path, file)
        spec = CallistoSpectrogram.read(full_path)
        list_of_specs.append(spec)

    return list_of_specs


################################################### 


def get_smallest_delta(list_of_specs):
    list_of_deltas = []

    for specs in list_of_specs:
        c_delta = specs.header['CDELT1']
        list_of_deltas.append(c_delta)

    min_delta = list_of_deltas[0]

    for small_delta in list_of_deltas:

        if small_delta < min_delta:
            min_delta = small_delta

    return min_delta


################################################### 
'''
def get_single_array_interp(file_name):
    ecallisto_data_frame  = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:

        if file == file_name:

            full_path = os.path.join(path, file)
            spec = CallistoSpectrogram.read(full_path)

            array_data = spec.data.data

            list_of_data = []
            for array in array_data:
                list_of_data.append(array)

            array_fp = list_of_data[0]
            array_x = np.linspace(0, 3600, 20)
            array_xp = np.arange(0, 3600)

            array_interp = np.interp(array_x, array_xp, array_fp)

            return array_interp

    return None

'''
###################################################
'''

def get_all_array_interp(file_name):
    ecallisto_data_frame  = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:

        if file == file_name:

            full_path = os.path.join(path, file)
            spec = CallistoSpectrogram.read(full_path)

            array_data = spec.data.data

            for array in array_data:
                array_fp = array
                array_x = np.linspace(0, 3600, 20)
                array_xp = np.arange(0, 3600)

                array_interp_all = np.interp(array_x, array_xp, array_fp)

                return array_interp_all

    return None
'''

################################################### 

def get_list_of_data_std():    
    ecallisto_data_frame = get_db_dataframe()

    list_of_std =[] 

    for file in ecallisto_data_frame['File_name']:
        full_path = os.path.join(path, file)
        spec = CallistoSpectrogram.read(full_path)
        
        bgs,_,_,cps = spec.subtract_bg_sliding_window(window_width=200, affected_width=1,
                                                      amount=0.05, change_points = True)
       
        array_std = bgs.data.std()
       
        rfi_rm = bgs.remove_single_freq_rfi(threshold = 8 * array_std, row_window_height=3)
        
        file_name_save = str(f'Saved_Spec/joined_{rfi_rm.filename}.fit.gz')
        file_path = rfi_rm.save(file_name_save)
        
                
        list_of_std.append(rfi_rm.data.std())
        

    return list_of_std

################################################### 

def get_single_data_std(file_name):
    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:
        if file == file_name:
            
            full_path = os.path.join(path, file)
            spec = CallistoSpectrogram.read(full_path)

            bgs, _, _, cps = spec.subtract_bg_sliding_window(window_width=200, affected_width=1, 
                                                             amount=0.05, change_points=True)
            array_std = bgs.data.std()

            rfi_rm = bgs.remove_single_freq_rfi(threshold=8 * array_std, row_window_height=3)

            rfi_rm_std = rfi_rm.data.std()       

    return rfi_rm_std


################################################### 

def store_std_to_db():    
    engine = create_engine(
        "mysql+pymysql://" + 'root' + ":" + 'delberin1992' + "@" + 'localhost' + "/" + 'ecallisto_DB')

    list_of_std = get_list_of_data_std()

    df_std = pd.DataFrame(list_of_std, columns=['STD'])
    
    ecallisto_data_frame = get_db_dataframe()
    
    ecallisto_data_frame.update(df_std)
    
    ecallisto_data_frame.to_sql('e_callisto_df', con = engine,if_exists = 'append', chunksize = 5000, index=False) 
    
    
    return ecallisto_data_frame

################################################### 

def get_group_by_station():
    engine = create_engine(
                            "mysql+pymysql://" + 'root' + ":" + 'delberin1992' 
                            + "@" + 'localhost' + "/" + 'ecallisto_DB')
    SQL_Query = pd.read_sql_query('''SELECT *
                                    FROM e_callisto_df
                                    GROUP BY File_name
                                    ORDER BY Instrument_name
                                    ;
                                    ''', engine)
    
    grouped_data_frame = pd.DataFrame(SQL_Query)
    
    
    return grouped_data_frame

################################################### 


def order_by_station():    
    engine = create_engine("mysql+pymysql://" + 'root' + ":" 
                           + 'delberin1992' + "@" + 'localhost'
                           + "/" + 'ecallisto_DB')
    
    SQL_Query = pd.read_sql_query('''SELECT Instrument_name,AVG(STD) 
                                    FROM e_callisto_df
                                    GROUP BY Instrument_name
                                    ORDER BY STD ASC;
                                    ''', engine)
    
    ordered_data_frame =  pd.DataFrame(SQL_Query)
    
    
    return ordered_data_frame

################################################### 

def order_by_station_2(): 
    engine = create_engine("mysql+pymysql://" + 'root' + ":" 
                           + 'delberin1992' + "@" + 'localhost'
                           + "/" + 'ecallisto_DB')
    
    SQL_Query = pd.read_sql_query('''SELECT *,AVG(STD) 
                                    FROM e_callisto_df
                                    GROUP BY Instrument_name
                                    ORDER BY STD ASC;
                                    ''', engine)
    
    ordered_data_frame_2 = pd.DataFrame(SQL_Query)
    
    
    return ordered_data_frame_2

################################################### 


def saved_specs():    
    ecallisto_data_frame = get_db_dataframe()

    for file in ecallisto_data_frame['File_name']:
        full_path = os.path.join(path, file)
        spec = CallistoSpectrogram.read(full_path)
        
        bgs,_,_,cps = spec.subtract_bg_sliding_window(window_width=200, affected_width=1,
                                                      amount=0.05, change_points = True)
       
        array_std = bgs.data.std()
       
        rfi_rm = bgs.remove_single_freq_rfi(threshold = 8 * array_std, row_window_height=3)
        file_name_save = str(f'Saved_Spec/{rfi_rm.filename}.fit.gz')
        file_path = rfi_rm.save(file_name_save)
        
    return None