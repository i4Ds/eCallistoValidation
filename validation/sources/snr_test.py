from validation import *


#sql_query = "select * from validation_data"
##sql_query = "select * from fits"
sql_query = """SELECT file_name, COALESCE(snr_values,0)
      AS best_score FROM validation_data
where start_time like '2017-09-01%'
order by snr_values desc"""

database = psycopg2.connect(host=test_config.DB_HOST,
                            user=test_config.DB_USER,
                            database=test_config.DB_DATABASE,
                            port=test_config.DB_PORT,
                            password=test_config.DB_PASSWORD)

def get_database(database, sql_query):
    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall()]

    return index, cursor
# call the get data_base function to get the data;
rows, cursor = get_database(database, sql_query)

for row in rows:print(row)

# This class to plot the Spectrogram, then save them as pdf file.
class Plot:

    def __init__(self, rows):
        self.rows = rows

    def get_plot(self) :
        print("Start to create the file .....")

        for row in rows:
            try:
                file_path = row[1]
                file_name = row[1].split("/")[4]

                spec = CallistoSpectrogram.read(test_config.DATA_PATH + file_path)
                fig1, ax1 = plt.subplots(1, 4, figsize=(25, 7))
                ax1 = spec.plot()
                ax1.title.set_text("Original Data")
                plt.close()

                # Second column, Constbacksub + elimwrongchannels
                spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
                plt.subplots(1, 4, figsize=(25, 7))
                ax2 = spec2.plot()
                ax2.title.set_text("Background subtracted")
                plt.close()

                # Third column, subtract_bg_sliding_window
                spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                         amount=0.05, change_points=True)
                plt.figure(figsize=(25, 7))
                ax3 = spec3.plot()
                ax3.title.set_text(
                    "Gliding background subtracted (window=800)")
                plt.close()

                # Fourth column, Histograms
                fig4, ax4 = plt.subplots(figsize=(25, 7))

                # Fourth column, Histograms
                data_absolute3 = get_abs_data(spec2)
                data_absolute4 = get_abs_data(spec3)

                n, bins, _ = ax4.hist([data_absolute3, data_absolute4], histtype='step', bins=25, log=True,
                                      label=['Background subtracted', 'Gliding background subtracted'])

                # Calculate the standard deviation and signal-to-noise => rounded them to have 3 digits.
                std_data = round(row[6], 3)
                snr_data = round(row[7], 3)
                max_mean = round(row[8], 3)

                # Set title for the histograms and show the std/snr values.
                ax4.title.set_text(
                    f"Histograms, std = {std_data}, snr = {snr_data}, max_mean = {max_mean}")
                plt.legend()
                plt.close()

                # Plot final plot by moving axes to the figure
                fig_target, (axA, axB, axC, axD) = plt.subplots(
                    1, 4, figsize=(30, 9))
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

            except Exception as err:

                print(f"The Error message is: {err} and the file name is {file_name}")
                # print("The Error message is: %s and the file name is %s" % (err, row[2]))

        print("Done")
    @classmethod
    def create_pdf(cls):

        with PdfPages('BgSubImages_test.pdf') as pdf:

            pdf.savefig(cls.get_plot(rows))
            plt.close()

#Plot.create_pdf()