
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms 
from sklearn.calibration import calibration_curve

spec_orfees = OrfeesSpectrogram("./orfees_files/int_orf20151104_120000_0.1.fts")
spec = CallistoSpectrogram.from_url('http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2015/11/04/GLASGOW_20151104_120000_59.fit.gz')

data_orfees= spec_orfees.data
data_spec = spec.data
.transpose()