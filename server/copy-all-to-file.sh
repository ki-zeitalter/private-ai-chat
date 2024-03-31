#!/bin/bash

# Leere die Ausgabedatei zuerst
> output.txt

# Durchsuche alle Python-Dateien, ignoriere .venv Verzeichnis
for file in $(find . -path './.venv' -prune -o -name "*.py" -print)
do
    # Schreibe den Dateinamen in die Ausgabedatei
    echo "------------------- $file ----------------" >> output.txt

    # Schreibe den Inhalt der Datei in die Ausgabedatei
    cat $file >> output.txt
done