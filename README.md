# eCallistoValidation

## Projekttitel:
##### eCallistoValidation.

##### SSA eCallisto ist ein Webservice, der Daten aus dem International Network of Solar Radio Spectrometers bereitstellt.

## Datenquelle :
- Alle fits Dateien: [Hier](http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/)


## Einstieg:
Dies ist ein schneller Überblick über die Ordnerstruktur:

- radiospectra:
- validation:
    - configs:
        - __init__.py
        - config.py
    - fits_files
    - source:
        - validation.py
        - update.py
        - save_to_sql.py
        - hist_test.py
        - SNR_test.ipynb
        - test_validation.ipynb

- dokumentation.ipynb
- requirements.txt

Hier ist eine kurze Beschreibung für jede Datei:

#### radiospectra: 

- radiospectra: Submodul des github i4ds radiospectra project (https://github.com/i4Ds/radiospectra).

#### validation:

- configs:
    - config.py: Enthält informationen über die Datenbank und den Path.

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


- dokumentation.ipynb: Enthält Beschreibung für alle Funktionen die wir haben.

- requirements.txt: Enthält alle module die wir installieren müssen.
