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