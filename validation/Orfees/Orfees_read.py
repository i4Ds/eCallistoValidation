import numpy as np
from astropy.io import fits
import datetime 
import matplotlib.pyplot as plt
# from matplotlib import cm
##from validation import *
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
#from skimage.transform import resize
import os
import sys
sys.path.append('../radiospectra2')

# import radiospectra2
from radiospectra.sources import CallistoSpectrogram

from matplotlib.ticker import MaxNLocator, IndexLocator
from scipy import interpolate
from copy import deepcopy
import matplotlib.ticker as ticker
from matplotlib.dates import MinuteLocator
# #import julian

# final Version

class OrfeesSpectrogram(CallistoSpectrogram):
    
    def __init__(self, file=None,  t_label="Time",  f_label="Frequency"):
        data = {}
        
        if file:
            data = self.read_orfees(file)
               
        self.__init_values__(**data)
            
    def __init_values__(self, **kwargs):
        self.data = kwargs.get("data", None)
        self.time_axis = kwargs.get("time_axis", None)
        self.freq_axis = kwargs.get("freq_axis", None)
        self.date_obs = kwargs.get("date_obs", None)
        self.time_start_obs = kwargs.get("time_start_obs", None)
        self.time_end_obs = kwargs.get("time_end_obs", None)

        self.t_label = kwargs.get("t_label", None)
        self.f_label = kwargs.get("f_label", None)
  

    def read_orfees(self, filename):
        hdulist=fits.open(filename)

        h_file = hdulist[0].header   # Header file
        frequency = hdulist[1].data  # data Extend1 (ferquency)
        h_data = hdulist[2].data     # data Extend2 (data)


        date_obs = h_file[4]         # Date observation start
        time_start_obs = h_file[5]   # Time observation start
        time_end_obs = h_file[7]     # Date observation End
      

        # STOKESI_B: nata for Stokes parameter I (STOKESI) per bann
        data_SI_B1 = h_data.STOKESI_B1
        data_SI_B2 = h_data.STOKESI_B2
        data_SI_B3 = h_data.STOKESI_B3
        data_SI_B4 = h_data.STOKESI_B4
        data_SI_B5 = h_data.STOKESI_B5

        # TIME_B: Time in seconn per bann
        time_1 = h_data.TIME_B1
        time_2 = h_data.TIME_B2
        time_3 = h_data.TIME_B3
        time_4 = h_data.TIME_B4
        time_5 = h_data.TIME_B5

        # The Frequency 
        freq_b1=frequency.FREQ_B1[0]
        freq_b2=frequency.FREQ_B2[0]
        freq_b3=frequency.FREQ_B3[0]
        freq_b4=frequency.FREQ_B4[0]
        freq_b5=frequency.FREQ_B5[0]
        
        # concatenate all together using np.concatenate
        time_axis = np.concatenate([time_1, time_2, time_3, time_4, time_5])
        freq_axis = np.concatenate([freq_b1,freq_b2,freq_b3,freq_b4,freq_b5])
        data = np.concatenate([data_SI_B1,data_SI_B2,data_SI_B3,data_SI_B4,data_SI_B5],axis=1)

        return {
            "data": data,
            "time_axis": time_axis,
            "freq_axis": freq_axis,
            "date_obs": date_obs,
            "time_start_obs": time_start_obs,
            "time_end_obs": time_end_obs
        }
    
    
    def convert_ms_to_date(self):
        # this function get the time axis from orfees file as miliseconds and convert it to date, return a list.(12:00:04.932000)

        times = self.time_axis
        
        list_of_times= []
        for time in times:
            delta = datetime.timedelta(0, 0, 0, int(time))
            list_of_times.append(str(delta).split(".")[0])

        return list_of_times
    

    def peek(self):

        fig, ax = plt.subplots()
        dates = self.convert_ms_to_date()


        ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=6))
        ax.set_xticklabels(dates[::int(len(dates)//30 )], rotation = 50, horizontalalignment="right")
    
        plt.imshow(self.data[:, 240:370].transpose(), vmin = self.data.min(), vmax = 1000, aspect="auto")
        plt.colorbar()
       
        plt.title(f"ORFEES, {self.date_obs}")
        plt.xlabel('Time[UT]')
        plt.ylabel('Frequency [MHz]')

        plt.show()