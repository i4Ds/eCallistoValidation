import sys
sys.path.append('/Users/delbe/OneDrive/Desktop/eCallistoValidation/packages')

from packages.main import *
from packages.modules import *

Path = 'Spec_test'

plt.rcParams['font.size'] = '16'

def get_plot(Path, pdf):
    for root, dirs, files in os.walk(Path):
        for name in files:
            if name.endswith('.fit.gz'):
                full_path = os.path.join(root, name)
                spec = CallistoSpectrogram.read(full_path)
                fig1, axs1 = plt.subplots(1, 4, figsize=(27, 6))
                ax1 = spec.plot()
                ax1.title.set_text("Original Data")
                plt.close()

                # Second column, Constbacksub + elimwrongchannels
                spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
                fig2 = plt.subplots(1, 4, figsize=(27, 6))
                ax2 = spec2.plot(vmin=-5, vmax=5)
                ax2.title.set_text("Background subtracted")
                plt.close()

                # Third column, subtract_bg_sliding_window
                spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                         amount=0.05, change_points=True)
                fig3 = plt.figure(figsize=(27, 6))
                ax3 = spec3.plot(vmin=-5, vmax=5)
                ax3.title.set_text(
                    "Gliding background subtracted (window=800)")
                plt.close()

                # Fourth column, Histograms
                fig4, ax4 = plt.subplots(figsize=(27, 6))

                # Fourth column, Histograms
                data_absolute3 = get_abs_data(spec2)
                data_absolute4 = get_abs_data(spec3)

                # take the min and max from the data to set the bins.
                min_value = get_min_data(data_absolute3, data_absolute4)
                max_value = get_max_data(data_absolute3, data_absolute4)

                print("min_value: ", min_value)
                print("max_value: ", max_value)
                print("---")

                ax4.hist(data_absolute3, histtype='step', bins=range(
                    min_value, max_value + 1), label='Background subtracted')
                ax4.hist(data_absolute4, histtype='step', bins=range(
                    min_value, max_value + 1), label='Gliding background subtracted')

                # Calculate the standard deviation and signal-to-noise => rounded them to have 3 digits.
                std_data = round(standard_deviation(data_absolute4), 3)
                snr_data = round(signal_to_noise(data_absolute4), 3)

                # Set title for the histograms and show the std/snr values.
                ax4.title.set_text(
                    f"Histograms, std = {std_data}, snr = {snr_data}")
                plt.legend()
                plt.close()

                # Plot final plot by moving axes to the figure
                fig_target, (axA, axB, axC, axD) = plt.subplots(
                    1, 4, figsize=(34, 9))
                plt.suptitle(fig1._suptitle.get_text())

                move_axes(fig_target, ax1, axA)
                move_axes(fig_target, ax2, axB)
                move_axes(fig_target, ax3, axC)
                move_axes(fig_target, ax4, axD)

                for ax in (ax1, ax2, ax3):
                    ax.set_xlabel('Time[UT]')
                    ax.set_ylabel('Frequency[MHz]')

                ax4.set_xlabel('Pixel values')
                ax4.set_ylabel('Number of pixels')

            pdf.savefig(fig_target)
            plt.close()


def get_pdf():
    with PdfPages('SubBG_Images.pdf') as pdf:

        get_plot(Path, pdf)
        
        print("Finished plotting!")




if __name__ == '__main__':
    print("This file is for testing")
    get_pdf()
    
