# QSM Form Automation - Walkthrough

## Übersicht

Python-Skript zum automatischen Ausfüllen des QSM-Antragsformulars mit Daten aus CSV-Export.

## Setup

```bash
pip install -r requirements.txt
playwright install
```

## Verwendung

```bash
python fill_qsm_form.py
```

Das Skript:
1. Lädt CSV-Datei und filtert nur **abgeschickte** Anträge (mit "Datum Abgeschickt")
2. Öffnet Browser und navigiert zum QSM-Formular
3. Füllt alle Felder für jeden Antrag aus
4. **Pausiert** nach jedem Eintrag zur manuellen Überprüfung
5. Du drückst "Resume" im Browser zum Fortfahren

## Wichtige Hinweise

### Datenfilterung

Von 60 CSV-Zeilen werden nur ~22 verarbeitet - das sind die tatsächlich abgeschickten Anträge. Abgebrochene Formulare (ohne Datum) werden automatisch übersprungen.

### Feldmapping

Fuzzy Matching findet Spalten auch bei Sonderzeichen:
- "Antragstitel" findet "Antragstitel\xa0"
- "Name und Email" findet "Name und Email-Adresse der Antragstellerin..."

### Name/Email Parsing

Unterstützt verschiedene Formate:
- `pig@uni-heidelberg.de` → nur Email
- `Max Mustermann, max@email.de` → Name + Email  
- `Max Mustermann max@email.de` → Name + Email

### Feste Werte

- **Bewirtschaftende Einrichtung**: "Geographisches Institut"
- **Studienfachschaft**: "13" (Geographie)
- **Captcha**: "Neckar"

## Konfiguration

Anpassen in [fill_qsm_form.py](file:///h:/Andere%20Computer/Mein%20Laptop/UNI/ToolsFachschaft/fill_qsm_form.py):

```python
FILE_PATH = r"H:\...\results-survey875166.csv"  # CSV-Pfad
STUDIENFACHSCHAFT_DEFAULT = "13"                 # Dropdown-Wert
FIXED_VALUES = {                                  # Feste Felder
    "bewirtschaftende_einrichtung": "Geographisches Institut",
}
```

## Technische Details

- **Playwright**: Browser-Automation
- **Pandas**: CSV-Parsing
- **Fuzzy Matching**: Toleriert Formatierungsfehler in Spaltennamen
- **Datum-Konvertierung**: Unterstützt `YYYY-MM-DD HH:MM:SS` und `DD.MM.YYYY`

## Projektstruktur

```
ToolsFachschaft/
├── Data/
│   └── results-survey875166.csv
├── fill_qsm_form.py
└── requirements.txt
```
