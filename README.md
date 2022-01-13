
# eCallisto Validation

eCallisto-Validation konzentriert sich auf die Bewertung der Datenqualität: Für eine bestimmte Beobachtungsstation, wie „gut“ die Qualität der aufgezeichneten Daten ist. Berechnet das Signal-Rausch-Verhältnis und wie gut jede Station gemäß der Standardabweichung ist.
Je das Signal-Rausch-Verhältnis größer, desto bessere Ergebnisse.

## Datenquelle :
- Alle fits Dateien: [Hier](http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/)

Dies ist ein schneller Überblick über die Ordnerstruktur:

- radiospectra2:
- validation:
    
    - fit_files
    - source:
        - validation.py
        - update.py
        - save_to_sql.py
        - hist_test.py
        - test_validation.ipynb
        
    - config.py
    
- README.ipynb
- requirements.txt

Hier ist eine kurze Beschreibung für jede Datei:

#### radiospectra2: 

- radiospectra2: Submodul des github i4ds radiospectra project (https://github.com/i4Ds/radiospectra).

#### validation:

- html: Enthält die Sphinx-Dokumentation. 

- fit_files: Enthält alle Fits-Daten zum Testen.

- source: Enthält alle Dateien, die wir für die Validierung benötigen: 

    - hist_test.py: Dieses Skript soll das Spektrogramm mit 4 Spalten getestet werden:
        - Die erste Spalte ist das ursprüngliche Spektrogramm.
        - Die zweite Spalte ist das Spektrogramm mit der Funktion (constbacksub, elimwrongchannels).
        - Die dritte Spalte ist das Spektrogramm mit der Funktion (subtract_bg_sliding_window).
        - Die vierte Spalte ist das Histogramm für beide Funktionen, zeigt die Werte des Signal-Rausch-Verhältnisses +Standardabweichung an.

    - Save_to_Sql:
      - Aufruf der MetaData aus der Header_liste.
      - Erstellen a DataFrame im Pandas.
      - Hinzufügen die MetaDaten in der DatenBank. 
      
    - test_validation.ipynb: Hier testen wir alle Funktion, die in der Datein(validation.py) sind. 

    - update.py:
      - Subtrahiere den Hintergrund mit der Funktion („subtract_bg_sliding_window“)
      - Berechnen die Standardabweichungen(STD), die Signal-Rausch-Verhältnis(SNR), und dann Update in die Datenbank.
      
    - validation.py: Enthält alle Funktionen, die wir zum Testen brauchen.
    
    - config.py: Enthält alle Informationen über die Datenbank und den Path.

- README.ipynb: Enthält die Beschreibung für alle Funktionen, die wir haben.

- requirements.txt: Enthält alle Module, die wir installieren müssen.


    


## Usage/Examples

### Test die Function interpolate2d :
In diesem Skript importieren wir aus der Dateivalidierung.py alle Funktionen, die wir für unser Programm benötigen.
Zuerst lesen wir die Fits-Datei mit der Funktion "read" aus dem Class **CallistoSpectrogram**,
dann wird die Funktion *interpolate2d* (Interpolation) aufgerufen.
#### CallistoSpectrogram ist eine Klasse im Submodul radiospectra in der Datei (spectrogram.py). 

```python
from validation import *

spec = CallistoSpectrogram.read("..//fit_files//GREENLAND_20170906_115501_63.fit.gz")
spec_plot = interpolate2d(spec)
spec_plot.plot()

print(spec_plot.time_axis.shape)
print(spec_plot.freq_axis.shape)

print(spec_plot.data.shape)
spec_plot.header
```

### Test das Signal-Rausch-Verhältnis und die Standardabweichung Werte : 

In diesem Skript prüfen wir den Unterschied im Signal-Rausch-Verhältnis ohne die Subtraktionsfunktion und dann mit.
Das Signal-Rausch-Verhältnis wird mit Mittelwerten durch der Standardabweichung berechnet.

Die Funktion **subtract_bg** befindet sich im Submodul radiospectra, die verwendet wird, um die Hintergrundsubtraktion durchzuführen

```python
from validation import *

spec = CallistoSpectrogram.read("..//fit_files//GREENLAND_20170906_115501_63.fit.gz")

spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")

data = abs(spec.data.flatten())
data_bg = abs(spec2.data.flatten())

data_mean = round(data.mean(), 3)
data_std = round(np.std(data), 3)

data_mean_bg = round(data_bg.mean(), 3)
data_std_bg = round(np.std(data_bg), 3)

print(f"Std for original Spec: {data_std}")
print(f"Mean for original Spec: {data_mean}")
print(f"SNR for original Spec: {data_mean / data_std}")

print("\n")

print(f"Std for subtracted Spec: {data_std_bg}")
print(f"Mean for subtracted Spec: {data_mean_bg}")
print(f"SNR for subtracted Spec: {data_mean_bg / data_std_bg}")
spec2.plot()
plt.show()
```



Hier erstellen wir eine Verbindung mit der Datenbank und dann eine SQL Query:
```python
from validation import *

database = psycopg2.connect(host=test_config.DB_HOST,
                            user=test_config.DB_USER,
                            database=test_config.DB_DATABASE,
                            port=test_config.DB_PORT,
                            password=test_config.DB_PASSWORD)

sql_query = "select * from validation_data"
```

Hier rufen wir die Daten von der Datenbank:
```python
def get_database(database, sql_query):

    sql_query_instruments = sql_query
    cursor = database.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(sql_query_instruments)
    index = [row for row in cursor.fetchall()]

    return index, cursor


rows, cursor = get_database(database, sql_query)
```
Diese Function erstellt eine PDF-Datei mit 4 Spalten von Plots (Original-Spektrogramm, Background subtracted ("constbacksub", "elimwrongchannels"),
Gliding background subtracted und Histogramm, zusätzlich werden die Standardabweichung und das Signal-Rausch-Verhältnis berechnet und dann dem Histogramm hinzugefügt: 
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
