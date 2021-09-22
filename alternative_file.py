from main import *

list_of_errors = []

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

        # Fourth column, Histograms
        fig4, ax4 = plt.subplots(figsize=(25, 7))

        # take the absolute data
        data_absolute3 = np.absolute(spec2.data.flatten())
        data_absolute4 = np.absolute(spec3.data.flatten())

        # Remove the NAN from the data
        # data3_remove_NAN = data_absolute3[np.logical_not(np.isnan(data_absolute3))]
        # data4_remove_NAN = data_absolute4[np.logical_not(np.isnan(data_absolute4))]

        # take the min and max from the data to set the bins.
        min_value = int(min(np.nanmin(data_absolute3), np.nanmin(data_absolute4)))
        max_value = int(max(np.nanmax(data_absolute3), np.nanmax(data_absolute4)))

        # Calculate the std and snr.
        std_data = float("{:.3f}".format(standard_deviation(data_absolute4)))
        snr_data = float("{:.3f}".format(signal_to_noise(data_absolute4)))

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
        plt.close()

    except Exception as err:

        exception_type = type(err).__name__
        list_of_errors.append(exception_type,index[2])
        print(exception_type)


print("Finished plotting!")



