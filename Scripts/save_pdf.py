from packages.modules import *
from packages.main import *
from packages import config as test_config

cursor = get_connection_db()

def get_all_instruments(cursor):
    sql_query_instruments = "select * from validation_data"
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall() ]

    return index


def get_plot_pdf(cursor, pdf):
    """Plot the 10'000 spectrograms and then save them into a pdf file.
    :param an array cursor:  the data from DB.
    :param pdf: to save as pdf file.
    :returns: return four columns (Original Data, 'Constbacksub + elimwrongchannels' , subtract_bg_sliding_window, Histograms).
    :rtype: fig
    """
    rows = get_all_instruments(cursor)
    for index in rows:
        try:
            # First column Original Data
            spec = CallistoSpectrogram.read(
                test_config.DATA_PATH + index[1])
            fig1, ax1 = plt.subplots(1, 4, figsize=(20, 5))
            ax1 = spec.plot()
            ax1.title.set_text("Original Data")
            plt.close()

            # Second column, Constbacksub + elimwrongchannels
            spec2 = spec.subtract_bg(
                "constbacksub", "elimwrongchannels")
            fig2 = plt.subplots(1, 4, figsize=(20, 5))
            ax2 = spec2.plot(vmin=-5, vmax=5)
            ax2.title.set_text("Background subtracted")
            plt.close()

            # Third column, subtract_bg_sliding_window
            spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)
            fig3 = plt.figure(figsize=(20, 5))
            ax3 = spec3.plot(vmin=-5, vmax=5)
            ax3.title.set_text(
                "Gliding background subtracted (window=800)")
            plt.close()

            # Fourth column, Histograms
            data_absolute3 = get_abs_data(spec2)
            data_absolute4 = get_abs_data(spec3)

            fig4, ax4 = plt.subplots(figsize=(20, 5))

            # take the min and max from the data to set the bins.
            min_value = get_min_data(data_absolute3, data_absolute4)
            max_value = get_max_data(data_absolute3, data_absolute4)

            ax4.hist(data_absolute3, histtype='step', bins=range(min_value, max_value + 1),
                     label='Background subtracted')
            ax4.hist(data_absolute4, histtype='step', bins=range(min_value, max_value + 1),
                     label='Gliding background subtracted')

            # Calculate the standard deviation and signal-to-noise => rounded them to have 3 digits.
            std_data = round(standard_deviation(data_absolute4), 3)
            snr_data = round(signal_to_noise(data_absolute4), 3)

            # Set title for the histograms and show the std/snr values.
            ax4.title.set_text(f"Histograms, std = {std_data}, snr = {snr_data}")
            plt.legend()


            # Plot final plot by moving axes to the figure
            fig_target, (axA, axB, axC, axD) = plt.subplots(
                1, 4, figsize=(30, 7))
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
            plt.show()
            pdf.savefig(fig_target)
            plt.close()

        except Exception as err:
            print("The Error message is: %s and the file name is %s" % (err, index[2]))


def get_pdf_file():
    """
    Save the spectrograms into the pdf file.
    Returns
    -------

    """
    with PdfPages('BgSubImages_test.pdf') as pdf:
        get_plot_pdf(cursor, pdf)

        print("Finished plotting!")


if __name__ == "__main__":
    get_pdf_file()


