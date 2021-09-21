import matplotlib.pyplot as plt

from main import *


def get_final_spec():


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

    def get_connect_DB():

        global cursor
        connection = psycopg2.connect(host=test_config.DB_HOST,
                                      database=test_config.DB_DATABASE,
                                      user=test_config.DB_USER,
                                      port=test_config.DB_PORT,
                                      password=test_config.DB_PASSWORD)
        cursor = connection.cursor()

    get_connect_DB()

    def get_1000_spec():
        """
        Select all data from the table "validation_data" to update the Std and Snr values.
        Returns
        -------
        A query of the Table.
        """
        cursor.execute(
            """SELECT * from validation_data WHERE std is not null ORDER BY snr_values DESC LIMIT 1000""")

    get_1000_spec()

    def moved_axes():
        move_axes(fig_target, ax1, axA)
        move_axes(fig_target, ax2, axB)
        move_axes(fig_target, ax3, axC)
        move_axes(fig_target, ax4, axD)

    def get_plots():
        global index, ax1, ax2, ax3, ax4, fig_target, axA, axB, axC, axD
        for index in cursor.fetchall():

            try:
                spec = CallistoSpectrogram.read(test_config.DATA_PATH + index[1])
                fig1, ax1 = plt.subplots(1, 4, figsize=(25, 7))
                ax1 = spec.plot()
                ax1.title.set_text("Original Data")
                plt.close()

                # Second column, Constbacksub + elimwrongchannels
                spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
                fig2 = plt.subplots(1, 4, figsize=(25, 7))
                ax2 = spec2.plot(vmin=-5, vmax=5)
                ax2.title.set_text("Background subtracted")
                plt.close()

                # Third column, subtract_bg_sliding_window
                spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                         amount=0.05, change_points=True)
                fig3 = plt.figure(figsize=(25, 7))
                ax3 = spec3.plot(vmin=-5, vmax=5)
                ax3.title.set_text("Gliding background subtracted (window=800)")
                plt.close()

                # Fourth column, Histogramshist
                fig4, ax4 = plt.subplots(figsize=(25, 7))

                # take the absolute data
                data_absolute3 = np.absolute(spec2.data.flatten())
                data_absolute4 = np.absolute(spec3.data.flatten())

                # Remove the NAN from the data
                data3_remove_NAN = data_absolute3[np.logical_not(np.isnan(data_absolute3))]
                data4_remove_NAN = data_absolute4[np.logical_not(np.isnan(data_absolute4))]

                # take the min and max from the data to set the bins.
                min_value = int(min(min(data3_remove_NAN), min(data4_remove_NAN)))
                max_value = int(max(max(data3_remove_NAN), max(data4_remove_NAN)))

                # Calculate the std and snr.
                std_data = float("{:.3f}".format(standard_deviation(data4_remove_NAN)))
                snr_data = float("{:.3f}".format(signal_to_noise(data4_remove_NAN)))

                # Plot the Histograms
                ax4.hist(data_absolute3, histtype='step', bins=range(min_value, max_value + 1),
                         label='Background subtracted')
                ax4.hist(data_absolute4, histtype='step', bins=range(min_value, max_value + 1),
                         label='Gliding background subtracted')

                # Set title for the histograms and show the std/snr values.
                ax4.title.set_text(f"Histograms, std={std_data}, snr={snr_data}")
                plt.legend()

                # Plot final plot by moving axes to the figure
                fig_target, (axA, axB, axC, axD) = plt.subplots(1, 4, figsize=(30, 8))
                plt.suptitle(fig1._suptitle.get_text())

                moved_axes()

                for ax in (ax1, ax2, ax3):
                    ax.set_xlabel('Time[UT]')
                    ax.set_ylabel('Frequency[MHz]')

                ax4.set_xlabel('Pixel values')
                ax4.set_ylabel('Number of pixels')

                plt.show()
                plt.close()

            except Exception as err:
                print(err)
                exception_type = type(err).__name__
                print(exception_type, index[1])
        print("Finished plotting!")

    get_plots()


get_final_spec()
