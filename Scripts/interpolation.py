from packages.modules import *
from scipy import interpolate
from copy import copy


spec = CallistoSpectrogram.read("Spec_test//GREENLAND_20170906_115501_63.fit.gz")

spec_copy = copy(spec)


def interpolated_spec(self, overwrite=True):
    """ 
    Interpolate the input data and it returns a new Spectrogram.
    
    :param object self: The copy of the original Spectrogram.
    :param bool overwrite: if function interpolated_spec has been called directly, 
     there will be a possibility to overwrite it's current spectrogram data. 
    :returns: New Spectrogram with the interpolated data. 
    
    """
    spec_sub = self.subtract_bg("constbacksub", "elimwrongchannels")  

    # Interpolation
    time_x = spec_sub.time_axis
    freq_y = spec_sub.freq_axis
    data_z = spec_sub.data

    inter_f = interpolate.interp2d(time_x, freq_y, data_z)
    
    # the Frequency before the Interpolation
    ynew = self.freq_axis
    znew = inter_f(time_x, ynew)
    
    # If overwrite= True => it will overwrite the new values into the Spec_sub.
    
    if overwrite:
        spec_sub.time_axis = time_x
        spec_sub.freq_axis = ynew
        spec_sub.data = znew[::-1]
        
        # TODO
        # Update the FITS Header history => .header.set('Card_name', 'The content')
        
        spec_sub.header.set('HISTORY', ': The Interpolate data after using the constbacksub, elimwrongchannels.' )
                 
    return spec_sub


spec_plot = interpolated_spec(spec_copy)
spec_plot.plot()
plt.show()
print(spec_plot.time_axis.shape)
print(spec_plot.freq_axis.shape)
print(spec_plot.data.shape)
