# eCallistoValidation

## Projekttitel:
##### eCallistoValidation.

##### SSA eCallisto ist ein Webservice, der Daten aus dem International Network of Solar Radio Spectrometers bereitstellt.

## Datenquelle :
Alle fits Dateien : data//radio//2002-20yy_Callisto//2017//09

## Einstieg :
Dies ist ein schneller Überblick über die Ordnerstruktur:
-	eCallistoProject =>  plot_config.py
-	SubModule (radiospectra)
-	Save_to_Sql.py
-	Std.py
-	Testing_10000.py
-	Plot_PDF.pdf
-	Documentation

Hier ist eine kurze Beschreibung für jede Datei:
#### radiospectra :
-	Submodul des github i4ds radiospectra project
Save_to_Sql:
-	Aufruf der MetaData aus der Header_liste
-	Erstellen a DataFrame Im Pandas
-	Hinzufügen die MetaDaten in der DatenBank
#### Std :
-	Subtrahiere den Hintergrund mit der Funktion („subtract_bg_sliding_window“)
-	Berechnen die Standardabweichnugn(STD) und dann Update in die Datenbank.
#### Testing_10000 :
-	Auswahl von 10 Spektrogrammen pro Station.
-	Speichern als PDF Datei.
-	Die PDF Dateien enthält eine Liste mit 4 Spalten.
##### Die Vier Spalten enthalten :
1.	Die erste Spalte enthält die Originaldaten
2.	Die zweite Spalte enthält (Constbacksub + elimwrongchannels)
3.	Die dritte Spalte enthält (subtract_bg_sliding_window)
4.	Die vierte Spalte enthält (Histogramme)
5.	
#### Bildern.pdf :
-	Enthält die gespeicherten PDF Dateien.






