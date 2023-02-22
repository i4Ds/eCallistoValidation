import numpy as np
from astropy.io import fits
import datetime 
import matplotlib.pyplot as plt
import sys
sys.path.append('../radiospectra2')
from radiospectra.sources import CallistoSpectrogram
from matplotlib.ticker import MaxNLocator
import cv2


class OrfeesSpectrogram():
    """
    Class to read Orfees data files and plot the data
    
    :param file: The filename of the Orfees data file
    :param t_label: The label for the time axis
    :param f_label: The label for the frequency axis
    
    :Example:
    
    >>> import sources.orfees
    >>> import matplotlib.pyplot as plt
    >>> orfees = sources.orfees.OrfeesSpectrogram(file="orfees.fits")
    >>> orfees.plot()
    >>> plt.show()

    """
    
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
        """
        Read the Orfees data file and return a dictionary with the data, time and frequency axis

        :param filename: The filename of the Orfees data file
        :return: A dictionary with the data, time and frequency axis
        """


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

        # TIME_B: Time in seconn per band
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
            "data": data,  #[:, 240:370],
            "time_axis": time_axis,
            "freq_axis": freq_axis,
            "date_obs": date_obs,
            "time_start_obs": time_start_obs,
            "time_end_obs": time_end_obs
        }


    def resize(self, target_shape):
        """
        Resize the spectrogram to the target shape
        
        :param target_shape: The target shape
        :return: The resized spectrogram
        """

        return cv2.resize(self.data.transpose(), target_shape, cv2.INTER_CUBIC)
    

    def convert_ms_to_date(self):
        """
        Convert the time axis from milliseconds to a date format
        
        :return: A list of dates
        """
        list_of_times = []
        for time in self.time_axis:
            delta = datetime.timedelta(0, 0, 0, int(time))
            list_of_times.append(str(delta).split(".")[0])

        return list_of_times
    
    
    def time_range(self, start_time, end_time):
        """
        Return the data between the start and end time
        
        :param start_time: The start time
        :param end_time: The end time
        :return: The data between the start and end time
        """

        converted_times = self.convert_ms_to_date()
        start_index = converted_times.index(start_time)
        end_index = converted_times.index(end_time)
        return self.data[start_index:end_index+1]
    

    

    def peek(self, start_time=None, end_time=None):
            """
            Plot the spectrogram
            
            :param start_time: The start time
            :param end_time: The end time
            :return: The plot
            """
            converted_times = self.convert_ms_to_date()
            dates = self.convert_ms_to_date()
            fig, ax = plt.subplots()
            
            if start_time is not None and end_time is not None:
                data = self.time_range(start_time, end_time)
                time_axis = self.time_axis[converted_times.index(start_time):converted_times.index(end_time)+1]
            else:
                data = self.data
                time_axis = self.time_axis

            ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=6))
            ax.set_xticklabels(dates[::int(len(dates)//30)], rotation=50, horizontalalignment="right")

            xmin = min(time_axis)
            xmax = max(time_axis)
            ymin = min(self.freq_axis)
            ymax = max(self.freq_axis)
            
            plt.imshow(data.T, vmin=data.min(), origin='lower', vmax=1000, aspect='auto', extent=[xmin, xmax, ymin, ymax])
            plt.colorbar()
            # ax.get_xlim(xmin, xmax)
            plt.gca().set_ylim(ymax, ymin)
            
            plt.title(f"ORFEES, {self.date_obs}")
            plt.xlabel('Time[UT]')
            plt.ylabel('Frequency [MHz]')

            plt.show()



    def plot_range_freq(self, spec):

        """
        Plot the spectrogram in a range of frequencies
        
        :param spec: The spectrogram
        :return: The plot
        """

        min_freq = spec.freq_axis.min()
        max_freq= spec.freq_axis.max()

        mask = (self.freq_axis > min_freq) & (self.freq_axis < max_freq)
        range_freq = self.freq_axis[mask]

        dates = self.convert_ms_to_date()
        range_pixels = self.data[:, mask]
        
        fig, ax = plt.subplots()
        xmin = min(self.time_axis)
        xmax = max(self.time_axis)
        ymin = min(range_freq)
        ymax = max(range_freq)

        ax.xaxis.set_major_locator(MaxNLocator(prune='both', nbins=6))
        ax.set_xticklabels(dates[::int(len(dates)//30 )], rotation = 50, horizontalalignment="right")

        plt.imshow(range_pixels.T,origin='lower', vmin=range_pixels.min(), vmax=1000, aspect='auto', extent=[xmin, xmax, ymin, ymax])
        plt.gca().set_ylim(ymax, ymin)
        plt.colorbar()
        plt.show()



    def plot_subplots(self, spec): 
        """
        Plot the spectrogram in subplots
        
        :param spec: The spectrogram
        :return: The plot
        """
        

        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        axs[0, 0].imshow(self.data.T,vmin=100, vmax=1000, aspect="auto")
        axs[0, 0].set_title("Orfees")
        axs[1, 0].imshow(spec.data[::-1], aspect="auto")
        axs[1, 0].set_title("eCallisto_BIR")
        axs[0, 1].plot(self.data[50])
        axs[1, 1].plot(spec.data[50])



    def plot_subplots_with_range(self, spec):
        """
        Plot the spectrogram in subplots with a range of frequencies
        
        :param spec: The spectrogram
        :return: The plot
        """

        min_freq = spec.freq_axis.min()
        max_freq= spec.freq_axis.max()
        min_time = spec.time_axis.min()
        max_time = spec.time_axis.max()

        mask = (self.freq_axis > min_freq) & (self.freq_axis < max_freq)
        range_freq = self.freq_axis[mask]

        dates = self.convert_ms_to_date()
        range_pixels = self.data[:, mask]
        fig, ax = plt.subplots(2, 1, figsize=(10, 9))

        xmin = min(self.time_axis)
        xmax = max(self.time_axis)
        ymin = min(range_freq)
        ymax = max(range_freq)

        
        ax[0].imshow(range_pixels.T,origin='lower', vmax=1000, aspect='auto', extent=[xmin, xmax, ymin, ymax])
        ax[0].set_ylim(ymax, ymin)
        ax[0].set_title("Orfees")
        ax[1].imshow(spec.data[::-1], origin='lower', aspect='auto', extent=[min_time, max_time, min_freq, max_freq])
        ax[1].set_ylim(max_freq, min_freq)
        ax[1].set_title("eCallisto_BIR")
