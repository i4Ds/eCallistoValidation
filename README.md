# eCallistoValidation

## Projekttitel:
##### eCallistoValidation.

##### SSA eCallisto ist ein Webservice, der Daten aus dem International Network of Solar Radio Spectrometers bereitstellt.

## Datenquelle :
- Alle fits Dateien: [Hier](http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/)


## Einstieg:
Dies ist ein schneller Überblick über die Ordnerstruktur:
- Documents:
    - Avg_of_std.xlsx
    - Documentation.ipynb

- Scripts:
    - Spec_test
    - packages:
        - config.py
        - main.py
        - modules.py
        - requirements.txt
    - radiospectra
    - interpolation.py
    - save_to_sql.py
    - spec_plot.py
    - test_create_pdf.ipynb
    - test_interpolation.ipynb
    - update.py
- eCallistoProject:
    - plot_config.py


Hier ist eine kurze Beschreibung für jede Datei:

#### Documents: 
- Enthält die Dokumente.
#### Scripts:
- Spec_test: Enthält alle Fits-Daten zum Testen.

- packages: Enthält die Funktionen und die Modules für den Code.

- radiospectra: Submodul des github i4ds radiospectra project (https://github.com/i4Ds/radiospectra).

- interpolation.py: führt die Interpolation durch.

- Save_to_Sql:
  - Aufruf der MetaData aus der Header_liste.
  - Erstellen a DataFrame im Pandas.
  - Hinzufügen die MetaDaten in der DatenBank

- spec_plot.py :
  - Auswahl von 10 Spektrogrammen pro Station.
  - Speichern als PDF Datei.
  - Die PDF-Dateien enthält eine Liste mit 4 Spalten.
    1. Die erste Spalte enthält die Originaldaten
    2. Die zweite Spalte enthält (Constbacksub + elimwrongchannels)
    3. Die dritte Spalte enthält (subtract_bg_sliding_window)
    4. Die vierte Spalte enthält (Histogramme)

- test_create_pdf.ipynb: Dies ist zum Testen der Datei spec_plot.py.

- test_interpolation.ipynb: Dies ist zum Testen der Datei interpolation.py.

- update.py:
  - Subtrahiere den Hintergrund mit der Funktion („subtract_bg_sliding_window“)
  - Berechnen die Standardabweichungen(STD) und dann Update in die Datenbank.







