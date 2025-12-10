import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import time
import os

FILE_PATH = r"H:\Andere Computer\Mein Laptop\UNI\ToolsFachschaft\Data\results-survey875166.csv"
FORM_URL = "https://www.stura.uni-heidelberg.de/vs-strukturen/referate/qsm/qsm-antragsformular/"

FIELD_SEARCH_TERMS = {
    "kurzbezeichnung": "Antragstitel",
    "beschreibung_massnahme": "Genaue Begründung",
    "leistungspunkte": "Anzahl der Leistugspunkte",
    "dozentischeAnsprechperson": "Name der ausführenden Person (Person, die den Lehrauftrag durchführt)",
    "bewilligter_betrag": "Beantragter Betrag",
    "laufzeit": "In welchem Semester werden die Mittel benötigt",
    "stan_name_email": "Name und Email-Adresse der Antragstellerin",
    "bdatum": "Datum Abgeschickt",
}

FIXED_VALUES = {
    "bewirtschaftende_einrichtung": "Geographisches Institut",
    "budgetverantwortlicher": "Veronika Helm",
    # Studentische Ansprechpartner Felder (Name, Email, Telefon)
    "stan_name": "",  # TODO: Feste Werte eintragen wenn bekannt
    "stan_email": "",  # TODO: Feste Werte eintragen wenn bekannt
    "stan_telefon": "",  # TODO: Feste Werte eintragen wenn bekannt
    "beschlussdatum": "2025-12-03",  
}

STUFE_DEFAULT = "1"
DECKUNGSFAEHIGKEIT_DEFAULT = "ja"
STUDIENFACHSCHAFT_DEFAULT = "13"

def find_column(df, search_term):
    search_lower = search_term.lower()
    for col in df.columns:
        if search_lower in col.lower():
            return col
    return None

def parse_name_email(combined):
    if not combined or pd.isna(combined):
        return "", ""
    
    combined = str(combined).strip()
    
    if combined.count('@') == 1 and ' ' not in combined:
        return "", combined
    
    if ',' in combined:
        parts = combined.split(',')
        name = parts[0].strip()
        email = parts[1].strip() if len(parts) > 1 else ""
        return name, email
    
    parts = combined.split()
    for i, part in enumerate(parts):
        if '@' in part:
            return " ".join(parts[:i]), part
    
    return combined, ""

def load_data():
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {FILE_PATH}")
        return None, {}

    df = pd.read_csv(FILE_PATH, on_bad_lines='skip')
    print(f"Geladen: {len(df)} Zeilen total")
    
    date_col = find_column(df, "Datum Abgeschickt")
    if date_col:
        df = df[df[date_col].notna() & (df[date_col].astype(str).str.strip() != '')]
        print(f"Gefiltert: {len(df)} abgeschickte Antraege")
    
    if len(df) == 0:
        return None, {}
    
    column_mapping = {}
    for field_name, search_term in FIELD_SEARCH_TERMS.items():
        found_col = find_column(df, search_term)
        if found_col:
            column_mapping[field_name] = found_col
    
    return df, column_mapping

def get_value(row, field_name, column_mapping):
    if field_name in FIXED_VALUES:
        return FIXED_VALUES[field_name]
    
    if field_name not in column_mapping:
        return ""
    
    val = row[column_mapping[field_name]]
    return "" if pd.isna(val) else str(val).strip()

def fill_form():
    df, column_mapping = load_data()
    if df is None or len(df) == 0:
        print("No data to process!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        for index, row in df.iterrows():
            print(f"\n{'='*70}")
            print(f"Processing row {index + 1}/{len(df)}")
            print(f"{'='*70}")
            
            page = context.new_page()
            page.goto(FORM_URL)
            page.wait_for_selector('input[name="kurzbezeichnung"]', timeout=10000)
            
            titel = get_value(row, "kurzbezeichnung", column_mapping)
            begr = get_value(row, "beschreibung_massnahme", column_mapping)
            lp = get_value(row, "leistungspunkte", column_mapping)
            if not lp:
                lp = "keine"
            dozent = get_value(row, "dozentischeAnsprechperson", column_mapping)
            ausfuehrende_person = dozent  # Name der ausführenden Person = Dozentische Ansprechperson
            betrag = get_value(row, "bewilligter_betrag", column_mapping)
            laufzeit = get_value(row, "laufzeit", column_mapping)
            date_val = get_value(row, "bdatum", column_mapping)
            
            combined = get_value(row, "stan_name_email", column_mapping)
            parsed_name, parsed_email = parse_name_email(combined)
            
            print(f"\n{titel[:60] if titel else 'LEER'} | {betrag} EUR")
            
            page.fill('input[name="kurzbezeichnung"]', titel)
            page.fill('textarea[name="beschreibung_massnahme"]', begr)
            page.fill('input[name="leistungspunkte"]', lp)
            page.fill('input[name="dozentischeAnsprechperson"]', ausfuehrende_person)
            page.fill('input[name="bewilligter_betrag"]', betrag)
            page.fill('textarea[name="bewirtschaftende_einrichtung"]', FIXED_VALUES["bewirtschaftende_einrichtung"])
            page.fill('textarea[name="budgetverantwortlicher"]', FIXED_VALUES["budgetverantwortlicher"])
            page.fill('input[name="laufzeit"]', laufzeit)
            page.fill('input[name="stan_name"]', FIXED_VALUES["stan_name"])
            page.fill('input[name="stan_email"]', FIXED_VALUES["stan_email"])
            page.fill('input[name="stan_telefon"]', FIXED_VALUES["stan_telefon"])
            
            # Datum Beschlussfassung (bdatum) immer fix setzen
            page.fill('input[name="bdatum"]', FIXED_VALUES["beschlussdatum"])
            
            page.check(f'input[name="stufe"][value="{STUFE_DEFAULT}"]')
            page.check(f'input[name="deckungsfaehigkeit_mittel"][value="{DECKUNGSFAEHIGKEIT_DEFAULT}"]')
            page.select_option('select[name="studienfachschaft"]', value=STUDIENFACHSCHAFT_DEFAULT)
            page.check('input[name="an_qsmkommission"]')
            page.fill('input[name="gotcha"]', "Neckar")
            
            print("Form filled - review and submit manually")
            page.pause()
            page.close()

        browser.close()
        print(f"\nFinished all {len(df)} rows!")

if __name__ == "__main__":
    fill_form()
