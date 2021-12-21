import os
import numpy
import scipy
import scipy.interpolate
import datetime

FONT_FILE = os.path.join("static", "fonts", "arial.ttf")

TICK_DISTANCE_X = 50
TICK_DISTANCE_Y = 50

# plot requirements
FONT_TITLE = 14
FONT_AXIS = 12
FONT_TICKS = 10

PLOT_MARGIN_TOP = 40
PLOT_MARGIN_BOTTOM = 60
PLOT_MARGIN_RIGHT = 100
PLOT_MARGIN_LEFT = 100

COLORBAR_WIDTH = 10
COLORBAR_HEIGHT = 170

BACKGROUND_COLOR = (240, 240, 240)


def __generate_colormap():
    __colormap_colors = numpy.array([
        [0,     0, 255],
        [255,   0,   0],
        [255, 255,   0],
        [255, 255, 255],
    ])
    n_colors = len(__colormap_colors)
    step = 255 / (n_colors - 1)
    x = [i*step for i in range(n_colors)]
    interpol_r = scipy.interpolate.interp1d(x, __colormap_colors[:, 0], kind='slinear')
    interpol_g = scipy.interpolate.interp1d(x, __colormap_colors[:, 1], kind='slinear')
    interpol_b = scipy.interpolate.interp1d(x, __colormap_colors[:, 2], kind='slinear')
    interpol_value = lambda v: [int(numpy.round(interpol_r(v))), int(numpy.round(interpol_g(v))), int(numpy.round(interpol_b(v)))]
    ret = numpy.array(list(map(interpol_value, range(256))), numpy.uint8)
    # invalid values (zero) are black
    ret[0] = numpy.array([0, 0, 0], numpy.uint8)
    return ret


COLORMAP = __generate_colormap()

# helper for map function
ColorMapping = lambda v: COLORMAP[int(round(v))]

# rounding on X-axis
TIME_ROUNDING = [
    datetime.timedelta(seconds=1),
    datetime.timedelta(seconds=2),
    datetime.timedelta(seconds=5),
    datetime.timedelta(seconds=10),
    datetime.timedelta(seconds=15),
    datetime.timedelta(seconds=20),
    datetime.timedelta(seconds=30),
    datetime.timedelta(minutes=1),
    datetime.timedelta(minutes=2),
    datetime.timedelta(minutes=5),
    datetime.timedelta(minutes=10),
    datetime.timedelta(minutes=15),
    datetime.timedelta(minutes=30),
    datetime.timedelta(hours=1),
    datetime.timedelta(hours=2),
    datetime.timedelta(hours=3),
    datetime.timedelta(hours=4),
    datetime.timedelta(hours=6),
    datetime.timedelta(hours=12),
    datetime.timedelta(days=1),
    datetime.timedelta(days=2),
    datetime.timedelta(days=7),
    datetime.timedelta(days=14),
    # roundings higher than days should be changed because this requires special handling in code
    datetime.timedelta(days=30),
    datetime.timedelta(days=365),
]
