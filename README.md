
# eCallisto Validation

SSA eCallisto ist ein Webservice, der Daten aus dem International Network of Solar Radio Spectrometers bereitstellt.


## Datenquelle :
- Alle fits Dateien: [Hier](http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/)

Dies ist ein schneller Überblick über die Ordnerstruktur:

- radiospectra2:
- validation:
    
    - fits_files
    - source:
        - validation.py
        - update.py
        - save_to_sql.py
        - hist_test.py
        - SNR_test.ipynb
        - test_validation.ipynb
        
    - config.py
    
- dokumentation.ipynb
- requirements.txt

Hier ist eine kurze Beschreibung für jede Datei:

#### radiospectra: 

- radiospectra: Submodul des github i4ds radiospectra project (https://github.com/i4Ds/radiospectra).

#### validation:

- fits_files: Enthält alle Fits-Daten zum Testen.

- source: Enthält die Funktionen und die Modules für den Code.
    - SNR_test.ipynb: Dieser File ist zum testing der signal-to-noise.
    
    - hist_test.py: Dieses Skript soll das Spektrogramm mit 4 Spalten testen:
        - Die erste Spalte ist das ursprüngliche Spektrogramm.
        - die zweite Spalte ist das Spektrogramm mit der Funktion (constbacksub, elimwrongchannels).
        - Die dritte Spalte ist das Spektrogramm mit der Funktion (subtract_bg_sliding_window).
        - Die vierte Spalte ist das Histogramm für beide Funktionen, zeigt die Werte des Signal-Rausch-Verhältnisses +Standardabweichung an.

    - Save_to_Sql:
          - Aufruf der MetaData aus der Header_liste.
          - Erstellen a DataFrame im Pandas.
          - Hinzufügen die MetaDaten in der DatenBank

    - update.py:
      - Subtrahiere den Hintergrund mit der Funktion („subtract_bg_sliding_window“)
      - Berechnen die Standardabweichungen(STD) und dann Update in die Datenbank.


    - validation.py: Enthält alle Funktionen die wir zum testen brauchen.
    
    - config.py: Enthält informationen über die Datenbank und den Path.

- dokumentation.ipynb: Enthält Beschreibung für alle Funktionen die wir haben.

- requirements.txt: Enthält alle module die wir installieren müssen.

## Installation

Install eCallistoValidation with pip

```bash
  pip install eCallistoValidation
  cd eCallistoValidation
```
    
    
## Usage/Examples

### Testing the function interpolate2d :
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

### Testing the snr and std values :

```python
from validation import *

spec = CallistoSpectrogram.read("..//fit_files//GREENLAND_20170906_115501_63.fit.gz")

spec2 = spec.subtract_bg("constbacksub", "elimwrongchannels")

data = abs(spec.data.flatten())
data_bg = abs(spec2.data.flatten())

data_mean = data.mean()
data_std = np.std(data)

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

Dieser Function erstellt 4 Spalten von Plots: 
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
