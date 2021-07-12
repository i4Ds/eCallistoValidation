import os
import io
import glob
import sys
import astropy.io.fits
import matplotlib
import numpy as np
import time
import timeit
import skimage.transform
import cv2
import psycopg2
from PIL import Image, ImageDraw, ImageFont
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

from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf, PdfFile

import warnings
warnings.filterwarnings("ignore")

path = 'R:\\radio\\2002-20yy_Callisto\\2017\\09\\06'

# Source: https://gist.github.com/salotz/8b4542d7fe9ea3e2eacc1a2eef2532c5

def move_axes(fig, ax_source, ax_target):
    old_fig = ax_source.figure
    ax_source.remove()
    ax_source.figure = fig
    ax_source.set_ylabel('')
    ax_source.set_xlabel('')
        
    ax_source.set_position(ax_target.get_position())
    ax_target.remove()
    ax_target.set_aspect("equal")
    fig.axes.append(ax_source)
    fig.add_subplot(ax_source)
    
    plt.close(old_fig)
    

    
    
# Connection between Jupyter notebook and Postgres
connection = psycopg2.connect(user="postgres",
                              password="ecallistohackorange",
                              host="localhost",
                              port="5432",
                              database="validation")

cursor = connection.cursor()

cursor.execute("""select * from (
                                 select ROW_NUMBER() OVER (partition by instrument_name order by id)
                                 as row_num, ecallisto2017.* FROM ecallisto2017
                                 ) t
                                 where row_num <=10
                                 order by instrument_name""")



my_colormap = matplotlib.colors.LinearSegmentedColormap.from_list("myColorMap", plot_config.COLORMAP / 255)

with PdfPages('C:\\Users\\delbe\\OneDrive\\Desktop\\eCallisto_validation\\Plot_PDF.pdf') as pdf:
    
    for file in cursor.fetchall():

        full_path = os.path.join(path, file[2]) # 2 is the index of file_name in the cursor
        spec = CallistoSpectrogram.read(full_path)
        fig1, axs1 = plt.subplots(1, 4, figsize=(25,5))
        ax1 = spec.plot(cmap=my_colormap, colorbar=None)
        ax1.title.set_text("Original Data")
        plt.close()

        # Second column, Constbacksub + elimwrongchannels
        spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
        fig2 = plt.subplots(1, 4, figsize=(25,5))
        ax2 = spec2.plot(cmap=my_colormap, colorbar=None, vmin=-5, vmax=5)
        ax2.title.set_text("Bg_cbs_rfi")
        plt.close()

        # Third column, subtract_bg_sliding_window
        spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                 amount=0.05, change_points=True)
        fig3 = plt.figure(figsize=(25,5))
        ax3 = spec3.plot(cmap=my_colormap, colorbar=None, vmin=-5, vmax=5)
        ax3.title.set_text("Bg_sub_sliding_rfi")
        plt.close()

        # Fourth column, Histograms
        data_hist3 = np.absolute(spec2.data.flatten())

        data_hist4 = np.absolute(spec3.data.flatten())
        fig4, ax4 = plt.subplots(figsize=(25,5))
        ax4.hist(data_hist3 ,histtype='step',range= (0, 10), bins= 40, label='Bg_cbs_rfi')
        ax4.hist(data_hist4 ,histtype='step',range= (0, 10), bins= 40, label='Bg_sub_sliding_rfi')
        ax4.title.set_text("Histograms")
        plt.legend()
        plt.close()

        # Plot final plot by moving axes to the figure
        fig_target, (axA, axB, axC, axD) = plt.subplots(1, 4, figsize=(30,5))
        plt.suptitle(fig1._suptitle.get_text())


        move_axes(fig_target, ax1, axA)
        move_axes(fig_target, ax2, axB)
        move_axes(fig_target, ax3, axC)
        move_axes(fig_target, ax4, axD)
        plt.show()

        pdf.savefig(fig_target)
        plt.close()

print("Finished plotting!")