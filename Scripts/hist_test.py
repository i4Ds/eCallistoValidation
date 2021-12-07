from validation import *

for root, dirs, files in os.walk("."):
    for name in files:
        if name.endswith('.fit.gz'):

            full_path = os.path.join(root, name)
            spec = CallistoSpectrogram.read(full_path)

            data_absolute = get_abs_data(spec)
            std_data_org = round(np.std(data_absolute), 3)
            mean_data_org = round(np.mean(data_absolute), 3)
            snr_data_org = round((mean_data_org / std_data_org), 3)

            fig1, axs1 = plt.subplots(1, 4, figsize=(25, 7))
            ax1 = spec.plot()
            ax1.title.set_text(f"Original Data, \n std = {std_data_org}, mean = {mean_data_org}, snr = {snr_data_org}")
            plt.close()

            # Second column, Constbacksub + elimwrongchannels
            spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")

            data_absolute3 = get_abs_data(spec2)
            std_data_elim = round(np.std(data_absolute3), 3)
            mean_data_elim = round(np.mean(data_absolute3), 3)
            snr_data_elim = round((mean_data_elim / std_data_elim), 3)

            fig2 = plt.subplots(1, 4, figsize=(25, 7))
            ax2 = spec2.plot()
            ax2.title.set_text(f"Background subtracted,\n std = {std_data_elim}, mean = {mean_data_elim}, snr = {snr_data_elim}")
            plt.close()

            # Third column, subtract_bg_sliding_window
            spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1, amount=0.05,
                                     change_points=True)

            data_absolute4 = get_abs_data(spec3)
            std_data_sub = round(np.std(data_absolute4), 3)
            mean_data_sub = round(np.mean(data_absolute4), 3)
            snr_data_sub = round((mean_data_sub / std_data_sub), 3)
            fig3 = plt.figure(figsize=(25, 7))
            ax3 = spec3.plot()
            ax3.title.set_text(f"Gliding background subtracted (window=800),\n std = {std_data_sub}, mean = {mean_data_sub}, snr = {snr_data_sub}")
            plt.close()

            # Fourth column, Histograms

            data_absolute4 = get_abs_data(spec3)
            fig4, ax4 = plt.subplots(figsize=(25, 7))

            # If Log is True, the histogram axis will be set to a log scale
            n, bins, patches = ax4.hist([data_absolute3, data_absolute4], histtype='step', bins=25, log = True,
                                        label=['Background subtracted', 'Gliding background subtracted'])


            # Set title for the histograms and show the std/snr values.
            ax4.title.set_text(f"Histograms, std = {std_data_elim}, snr = {snr_data_elim}")
            plt.legend()

            # Plot final plot by moving axes to the figure
            fig_target, (axA, axB, axC, axD) = plt.subplots(
                1, 4, figsize=(27, 7))
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





