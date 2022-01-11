
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

Der Path: eCallistoValidation\validation\sources\validation.py.

### Test die Function interpolate2d :
In diesem Skript importieren wir aus der validation.py alle Funktionen, die wir für unser Programm benötigen.
Zuerst lesen wir die Fits-Datei mit der Funktion "read" aus dem Class **CallistoSpectrogram**,
dann wird die Funktion *interpolate2d* (Interpolation) aufgerufen

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

### Test das Signal-Rausch-Verhältnis und die Standardabweichung Werte: 

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

Diese Function erstellt 4 Spalten von Plots mit (Original-Spektrogramm, Background subtracted ("constbacksub", "elimwrongchannels"),
Gliding background subtracted und Histogramm, zusätzlich werden die Standardabweichung und das Signal-Rausch-Verhältnis berechnet und dann dem Histogramm hinzugefügt: 
```python
def get_plot(self):
    try:
        # First Column, Original Spectrogram
        spec = CallistoSpectrogram.read(self)
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

        fig4, ax4 = plt.subplots(figsize=(25, 7))

        # If Log is True, the histogram axis will be set to a log scale
        n, bins, patches = ax4.hist([data_absolute3, data_absolute4], histtype='step', bins=25, log = True,
                                    label=['Background subtracted', 'Gliding background subtracted'])

        # Set title for the histograms and show the std/snr values.
        ax4.title.set_text(f"Histograms, std = {std_data_elim}, snr = {snr_data_elim}")
        plt.legend()

        plt.legend()
        plt.close()

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

    except Exception as err:
        
        # => file is the name of the file in case if there is an error
        print(f"The Error message is: {err} and the file name is {file}")

```

Speichern als PDF-Datei:

```python
with PdfPages('BgSubImages_test.pdf') as pdf:

for root, dirs, files in os.walk(".."):
        for file in files:
            if file.endswith('.fit.gz'):
                full_path = os.path.join(root, file)

                spec_pdf = get_plot(full_path)

                pdf.savefig(spec_pdf)
                plt.close()

```