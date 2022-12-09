import numpy as np
from astropy.io import fits

import numpy.ma as ma
import matplotlib.pyplot as plt

def read_orfees(filename):
    hdu=fits.open(filename)
    
    header_file=hdu[0].header               #Header file
    header_frequency=hdu[1].header          #Header frequency
    header_data=hdu[2].header               #Header data
    frequency=hdu[1].data                   #data Extend1 (ferquency)
    Data=hdu[2].data                        #data Extend2 (data)
    date_obs=header_file[4]                 #Date observation start
    time_start_obs=header_file[5]           #Time observation start
    time_end_obs=header_file[7]             #Date observation End
    
    time_integration=header_data[9]         #Time integration
    
    data_SI_B1=Data.STOKESI_B1              #Data table STOKES I of band 1
    data_SV_B1=Data.STOKESV_B1              #Data table STOKES V of band 1
    data_SI_B2=Data.STOKESI_B2              #Data table STOKES I of band 2
    data_SV_B2=Data.STOKESV_B2              #Data table STOKES V of band 2
    data_SI_B3=Data.STOKESI_B3              #Data table STOKES I of band 3
    data_SV_B3=Data.STOKESV_B3              #Data table STOKES V of band 3
    data_SI_B4=Data.STOKESI_B4              #Data table STOKES I of band 4
    data_SV_B4=Data.STOKESV_B4              #Data table STOKES V of band 4
    data_SI_B5=Data.STOKESI_B5              #Data table STOKES I of band 5
    data_SV_B5=Data.STOKESV_B5              #Data table STOKES V of band 5
    
    TIME_B1=Data.TIME_B1                    #Time table of band 1
    TIME_B2=Data.TIME_B2                    #Time table of band 2
    TIME_B3=Data.TIME_B3                    #Time table of band 3
    TIME_B4=Data.TIME_B4                    #Time table of band 4
    TIME_B5=Data.TIME_B5                    #Time table of band 5
    
    nbr_freq_b1=frequency.NP_B1[0]          #Number of frenquencies of band 1
    nbr_freq_b2=frequency.NP_B2[0]          #Number of frenquencies of band 2
    nbr_freq_b3=frequency.NP_B3[0]          #Number of frenquencies of band 3
    nbr_freq_b4=frequency.NP_B4[0]          #Number of frenquencies of band 4
    nbr_freq_b5=frequency.NP_B5[0]          #Number of frenquencies of band 5
    
    freq_b1=frequency.FREQ_B1[0]            #frenquencies table of band 1
    freq_b2=frequency.FREQ_B2[0]            #frenquencies table of band 2
    freq_b3=frequency.FREQ_B3[0]            #frenquencies table of band 3
    freq_b4=frequency.FREQ_B4[0]            #frenquencies table of band 4
    freq_b5=frequency.FREQ_B5[0]            #frenquencies table of band 5
    
    ####creation_one_data_frequency_and_time_tables
    Freq = np.concatenate((freq_b1,freq_b2,freq_b3,freq_b4,freq_b5)) #frenquencies table
    Data_I = np.concatenate((data_SI_B1,data_SI_B2,data_SI_B3,data_SI_B4,data_SI_B5),axis=1) #Data table
    return Data_I,TIME_B1,Freq,date_obs,time_start_obs,time_end_obs,time_integration

####################orfees#################################d

# ##Test to read fits file##
# filename="../ORFEES/int_orf20170906_115500_10.fts"
# #[data_SI_B1,data_SI_B2,data_SI_B3,data_SI_B4,data_SI_B5,TIME_B1,TIME_B2,TIME_B3,TIME_B4,TIME_B5,freq_b1,freq_b2,freq_b3,freq_b4,freq_b5,date_obs,time_start_obs,time_end_obs,time_integration]=read_orfees(filename)
# [Data_I,Time,Freq,date_obs,time_start_obs,time_end_obs,time_integration]=read_orfees(filename)




