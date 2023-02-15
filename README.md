
# eCallisto Validation

The e-Callisto Validation project aims to evaluate the performance of the actual e-Callisto product. The project consists of two independent validation campaigns. The first campaign is focused on assessing the data quality, while the second is focused on each station's availability and cross-comparison level. The e-Callisto network, which consists of multiple CALLISTO spectrometers deployed worldwide, can continuously observe the solar radio spectrum 24/7. The e-Callisto provides radio spectrograms, which are time series of radio flux measurements at a relatively high number of radio frequencies, and the purpose of the validation campaign is to determine the intended cross-comparison within the e-Callisto network and test cases. The project aims to validate the e-Callisto product's ability to observe different types of solar radio bursts, such as type II, type III, or type IV, and to classify bursts and perform long-term trend analyses. The two main use cases for the validation of the product are the determination of the speed of accelerated electron beams, as they appear in Type III bursts, and the provision of spectrograms as complementary information for analysis of events observed by instruments on spacecraft that look at the same events, but in different wavelengths.

## Data Source:
- The entire Data: [Hier](http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/)

This is a quick overview of the folder structure:
- docs
- radiospectra2:
- validation:
    - Orfees:
        - eca_files
        - Orfees_files
        - Orfees_read.py
        - Test_orfees.ipynb
    - rating_stars:
        - config.py
        - convert_to_stars
        - rating.py
        - test_rating.py
        - final_rate.xlsx
    - source:
        - validation.py
        - update.py
        - save_to_sql.py
        - hist_test.py
        - test_validation.ipynb
- README.ipynb
- requirements.txt

Here is a brief description for each file:

### Sphinx documentation:
Contains the documentation of the project. [eCallistoValidation Dokumentation](https://i4ds.github.io/eCallistoValidation/)

### radiospectra2: 
- radiospectra2: submodule of i4ds radiospectra project (https://github.com/i4Ds/radiospectra).

# validation:

- Orfees: Contains all Orfees files and scripts.
- rating_stars: Contains the scripts for the Rating system.
- source: Contains all files we need for validation.


- requirements.txt: Contains all the modules we need to install.


## Usage/Examples

### OrfeesSpectrogram:
This class reads data from Orfees spectrograms and allows the user to manipulate the data in various ways.

### Reading data from an Orfees spectrogram:
To read data from an Orfees spectrogram, use the read_orfees() method. The method takes a filename as a parameter and returns a dictionary containing the spectrogram data, as well as various other metadata. For example:


```python
from ecallisto_validation import OrfeesSpectrogram

spec = OrfeesSpectrogram('data/spec.fits')
```

### Resizing a spectrogram:
To resize the spectrogram, use the resize() method. The method takes a target shape (in the form of a tuple) as a parameter and returns the resized spectrogram. For example:


```python
orfees = OrfeesSpectrogram('path to orfees files')

spec=CallistoSpectrogram.from_url('http://soleil.i4ds.ch/solarradio/data/200220yy_Callisto/2017/09/06/GREENLAND_20170906_115514_62.fit.gz')

resized_spec = orfees_2.resize((spec.shape[1],spec.shape[0]))
plt.imshow(data,vmin=100, vmax=1000, aspect="auto")
plt.show()
```

### Selecting a time range:
To select a time range from the spectrogram, use the time_range() method. The method takes a start time and an end time (in the format HH:MM:SS) as parameters and returns the subset of the spectrogram that falls within the specified time range. For example:

```python
orfees = OrfeesSpectrogram('path to orfees files')
subset_spec = spec.time_range(start_time, end_time)
```

### Plotting the spectrogram:
To plot the spectrogram, use the peek() method. The method takes a start time and an end time (in the format HH:MM:SS) as optional parameters and plots the spectrogram for the specified time range. If no time range is specified, the entire spectrogram is plotted. For example:

```python
orfees = OrfeesSpectrogram('path to orfees files')
spec =CallistoSpectrogram.from_url('http://soleil.i4ds.ch/solarradio/data/2002-20yy_Callisto/2015/11/04/BIR_20151104_120000_03.fit.gz')

# plot without parameters:
orfees.peek()
# plot with parameters:
orfees.peek(start_time='06:00:00', end_time='06:30:00')
# plot with the frequency range of ecallisto frequency:
orfees.plot_range_freq(spec)
```

### Rating System:
This system rates the stations based on their SNR and standard deviation values. The rating is done on a scale of 1 to 5, and the data is sorted into different bins to assign a specific rating to each station. The results are displayed in a tabular format that shows the SNR, SNR rating, standard deviation, standard deviation rating, and the number of files for each station.


This script connects to a database and retrieves data for a specific time range and returns a database object:
```python
from validation import *

database = psycopg2.connect(host=test_config.DB_HOST,
                            user=test_config.DB_USER,
                            database=test_config.DB_DATABASE,
                            port=test_config.DB_PORT,
                            password=test_config.DB_PASSWORD)

sql_query = "select * from validation_data"

def get_database(database, sql_query):

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall()]

    return index, cursor


rows, cursor = get_database(database, sql_query)
```

This function generates a PDF report containing 4 spectrogram plots for each input row. Each row is expected to contain the path of a spectrogram file and some metadata, which is used to calculate and display the standard deviation, signal-to-noise ratio, and maximum mean values of the spectrogram.

To use this function, provide a list of rows where each row is a list containing the spectrogram file path and the corresponding metadata. The PDF report will be saved in the same directory as the script with the name 'bg_sub_images.pdf'.

```python
def get_plot(rows):
    with PdfPages('bg_sub_images.pdf') as pdf:
        for row in rows:
            try:
                file_path = row[1]
                file_name = row[1].split("/")[4]

                spec = CallistoSpectrogram.read(test_config.DATA_PATH + file_path)
                fig1, axs1 = plt.subplots(1, 4, figsize=(27, 6))
                ax1 = spec.plot()
                ax1.title.set_text("Original Data")
                plt.close()

                # Second column, Constbacksub + elimwrongchannels
                spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")
                fig2 = plt.subplots(1, 4, figsize=(27, 6))
                ax2 = spec2.plot()
                ax2.title.set_text("Background subtracted")
                plt.close()

                # Third column, subtract_bg_sliding_window
                spec3 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                        amount=0.05, change_points=True)
                fig3 = plt.figure(figsize=(27, 6))
                ax3 = spec3.plot()
                ax3.title.set_text(
                    "Gliding background subtracted (window=800)")
                plt.close()

                # Fourth column, Histograms
                fig4, ax4 = plt.subplots(figsize=(27, 6))

                # Fourth column, Histograms
                data_absolute3 = get_abs_data(spec2)
                data_absolute4 = get_abs_data(spec3)

                n, bins, patches = ax4.hist([data_absolute3, data_absolute4], histtype='step', bins=25, log = True,
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

                pdf.savefig(fig_target)
                plt.close()

            except Exception as err:
                print(f"The Error message is: {err} and the file name is {file_name}")
               
```
