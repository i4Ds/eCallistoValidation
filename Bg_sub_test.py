from main import *

# Connection between Jupyter notebook and Postgres

# Choosing 10 images for each Station

def get_data():
    cursor.execute("""  select * from validation_data """)


get_data()


def get_10000_spec():
    count = 0
    with PdfPages('Bg_Sub_Images.pdf') as pdf:
        for index in cursor.fetchall():
            try:
                if count < 10:
                    spec = CallistoSpectrogram.read(
                        test_config.DATA_PATH + index[1])
                    fig1, axs1 = plt.subplots(1, 4, figsize=(20, 5))
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

                    # Fourth column, Histogramshist
                    data_absolute3 = np.absolute(spec2.data.flatten())
                    data_absolute4 = np.absolute(spec3.data.flatten())

                    fig4, ax4 = plt.subplots(figsize=(20, 5))

                    data3_remove_NAN = data_absolute3[np.logical_not(
                        np.isnan(data_absolute3))]
                    data4_remove_NAN = data_absolute4[np.logical_not(
                        np.isnan(data_absolute4))]

                    #  absolute_data3[np.isnan(absolute_data3)] = 0
                    #  absolute_data4[np.isnan(absolute_data4)] = 0

                    min_value = int(
                        min(min(data3_remove_NAN), min(data4_remove_NAN)))
                    max_value = int(
                        max(max(data3_remove_NAN), max(data4_remove_NAN)))

                    print("min_value: ", min_value)
                    print("max_value: ", max_value)
                    print("---")

                    ax4.hist(data_absolute3, histtype='step', bins=range(min_value, max_value + 1),
                             label='Background subtracted')
                    ax4.hist(data_absolute4, histtype='step', bins=range(min_value, max_value + 1),
                             label='Gliding background subtracted')

                    # Plot final plot by moving axes to the figure
                    fig_target, (axA, axB, axC, axD) = plt.subplots(
                        1, 4, figsize=(30, 7))
                    plt.suptitle(fig1._suptitle.get_text())

                    move_axes(fig_target, ax1, axA)
                    move_axes(fig_target, ax2, axB)
                    move_axes(fig_target, ax3, axC)
                    move_axes(fig_target, ax4, axD)

                    ax1.set_xlabel('Time[UT]')
                    ax1.set_ylabel('Frequency[MHz]')

                    ax2.set_xlabel('Time[UT]')
                    ax2.set_ylabel('Frequency[MHz]')

                    ax3.set_xlabel('Time[UT]')
                    ax3.set_ylabel('Frequency[MHz]')

                    ax4.set_xlabel('Pixel values')
                    ax4.set_ylabel('Number of pixels')

                    plt.show()

                    count += 1
                    pdf.savefig(fig_target)
                    plt.close()

            except Exception as err:
                print(err)
                exception_type = type(err).__name__
                print(exception_type, index[1])

        print("Finished plotting!")


get_10000_spec()



