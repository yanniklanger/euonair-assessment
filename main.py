#!/usr/bin/env python3
import streamlit as st
import feedparser
import urllib.parse
import requests
from bs4 import BeautifulSoup
import subprocess
import json
import time
import sys
import os
import csv
import io
import PyPDF2
import datetime
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import requests.exceptions

st.title("arXiv Search App mit DOI-Webscraping")
st.write("Gib deine Suchterme ein und wähle, ob diese mit AND oder OR verknüpft werden sollen.")

# Debug: Aktuelles Arbeitsverzeichnis anzeigen
cwd = os.getcwd()
st.write("**Aktuelles Arbeitsverzeichnis:**", cwd)
if not os.path.exists(os.path.join(cwd, "AI_Analysis.py")):
    st.error("**Fehler:** Die Datei 'AI_Analysis.py' wurde im aktuellen Arbeitsverzeichnis nicht gefunden!")
if not os.path.exists(os.path.join(cwd, "LLM_Analysis.py")):
    st.error("**Fehler:** Die Datei 'LLM_Analysis.py' wurde im aktuellen Arbeitsverzeichnis nicht gefunden!")
if not os.path.exists(os.path.join(cwd, "apikey.py")):
    st.error("**Fehler:** Die Datei 'apikey.py' wurde im aktuellen Arbeitsverzeichnis nicht gefunden!")

# Eingabefelder und Optionen
term1 = st.text_input("Suchterm 1", "generative artificial intelligence")
term2 = st.text_input("Suchterm 2", "education")
operator = st.selectbox("Operator auswählen", ["AND", "OR"])
max_results = st.slider("Max results", min_value=1, max_value=50, value=10)
year_range = st.slider("Filter by publication year", min_value=1990, max_value=2025, value=(2000, 2025))

def get_doi_from_article(article_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(article_url, headers=headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        doi_link = soup.find("a", href=lambda href: href and "doi.org" in href.lower())
        if doi_link:
            doi_url = doi_link.get("href").strip()
            if doi_url.lower().startswith("http://"):
                doi_url = "https://" + doi_url[7:]
            elif not doi_url.lower().startswith("http"):
                doi_url = "https://doi.org/" + doi_url
            return doi_url
    except Exception:
        return None
    return None

@retry(wait=wait_exponential(multiplier=1, min=4, max=10),
       stop=stop_after_attempt(5),
       retry=retry_if_exception_type(requests.exceptions.RequestException))
def query_arxiv(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(f"Status Code: {response.status_code}")
    return response.text

@retry(wait=wait_exponential(multiplier=1, min=4, max=10),
       stop=stop_after_attempt(5),
       retry=retry_if_exception_type(requests.exceptions.RequestException))
def _extract_text_from_pdf(pdf_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(pdf_url, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(f"Status Code: {response.status_code}")
    file = io.BytesIO(response.content)
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_pdf(pdf_url):
    try:
        return _extract_text_from_pdf(pdf_url)
    except Exception:
        return None

# Suchergebnisse in st.session_state speichern
if st.button("Search"):
    if term1 or term2:
        if term1 and term2:
            search_query = f'"{term1}" {operator} "{term2}"'
        else:
            search_query = f'"{term1}"'
    else:
        st.error("Bitte gib mindestens einen Suchterm ein.")
        st.stop()
    
    st.session_state["search_params"] = {
        "term1": term1,
        "term2": term2,
        "operator": operator,
        "max_results": max_results,
        "year_range": year_range
    }
    
    encoded_search = urllib.parse.quote(search_query)
    api_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_search}&start=0&max_results={max_results}"
    st.write("Abfrage-URL:", api_url)
    
    try:
        xml_data = query_arxiv(api_url)
    except Exception as e:
        st.error(f"Fehler bei der arXiv-Abfrage: {str(e)}")
        st.stop()
    
    feed = feedparser.parse(xml_data)
    st.write(f"Gefundene Ergebnisse: {len(feed.entries)}")
    
    results = []
    for entry in feed.entries:
        try:
            year = int(entry.published[:4])
        except Exception:
            year = None
        if year and year_range[0] <= year <= year_range[1]:
            results.append(entry)
    
    st.write(f"Ergebnisse nach Jahr-Filter: {len(results)}")
    st.session_state['results'] = results

# Funktion: Zählt, wie viele Einträge einen PDF-Link haben
def count_full_text_available(results):
    count = 0
    for entry in results:
        pdf_link = next((link.href for link in entry.links if link.get("type") == "application/pdf"), None)
        if pdf_link:
            count += 1
    return count

# Funktion: Startet fehlende KI/LLM Analysen für alle Ergebnisse
def update_all_analyses():
    results = st.session_state.get('results', [])
    for i, entry in enumerate(results):
        pdf_link = next((link.href for link in entry.links if link.get("type") == "application/pdf"), None)
        if pdf_link:
            input_for_analysis = pdf_link
        else:
            input_for_analysis = entry.summary

        # KI Analyse (AI_Analysis.py)
        analysis_key = f"analysis_result_{i}"
        if not st.session_state.get(analysis_key):
            try:
                result = subprocess.run(
                    [sys.executable, "AI_Analysis.py", input_for_analysis],
                    capture_output=True, text=True, check=True
                )
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output = {"error": "JSON Dekodierungsfehler (KI)"}
                st.session_state[analysis_key] = output
            except Exception as e:
                st.session_state[analysis_key] = {"error": str(e)}
        
        # LLM Analyse (LLM_Analysis.py)
        llm_analysis_key = f"llm_analysis_result_{i}"
        if not st.session_state.get(llm_analysis_key):
            try:
                result = subprocess.run(
                    [sys.executable, "LLM_Analysis.py", input_for_analysis],
                    capture_output=True, text=True, check=True
                )
                try:
                    llm_output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    llm_output = {"error": "LLM JSON Dekodierungsfehler"}
                st.session_state[llm_analysis_key] = llm_output
            except Exception as e:
                st.session_state[llm_analysis_key] = {"error": str(e)}

# Anzeige der Ergebnisse
if 'results' in st.session_state:
    results = st.session_state['results']
    for i, entry in enumerate(results):
        st.markdown(f"### {entry.title.replace(chr(10), ' ').strip()}")
        st.write("**Autor:**", entry.get('author', 'N/A'))
        st.write("**Veröffentlicht:**", entry.get('published', 'N/A'))
        st.write("**Zusammenfassung:**", entry.get('summary', 'N/A'))
        st.write(f"[Link zum Artikel]({entry.link})")
        
        doi_scraped = get_doi_from_article(entry.link)
        if doi_scraped:
            st.markdown("**DOI:** [{}]({})".format(doi_scraped, doi_scraped))
        else:
            st.write("**DOI:** N/A")
        
        # Input für die Analyse: PDF-Link falls vorhanden, sonst Abstract
        pdf_link = next((link.href for link in entry.links if link.get("type") == "application/pdf"), None)
        if pdf_link:
            input_for_analysis = pdf_link
            st.markdown("**Full Text:** [Download PDF]({})".format(pdf_link))
            spinner_message = "pdf verfügbar - pdf wird analysiert"
        else:
            input_for_analysis = entry.summary
            st.write("**Kein PDF vorhanden, Abstract wird analysiert.**")
            spinner_message = "pdf nicht verfügbar - abstract wird analysiert"
        
        # KI Analyse-Button: Startet AI_Analysis.py für diesen Eintrag
        analysis_key = f"analysis_result_{i}"
        if analysis_key not in st.session_state:
            st.session_state[analysis_key] = None
        
        if st.button("KI Analyse", key=f"ai_{i}"):
            st.write("**Debug:** KI Analyse-Button für Eintrag", i, "wurde gedrückt.")
            with st.spinner(spinner_message):
                try:
                    result = subprocess.run(
                        [sys.executable, "AI_Analysis.py", input_for_analysis],
                        capture_output=True, text=True, check=True
                    )
                    st.write("**Subprocess Output (KI):**", result.stdout)
                    st.write("**Subprocess Return Code (KI):**", result.returncode)
                    try:
                        output = json.loads(result.stdout)
                    except json.JSONDecodeError as e:
                        st.error("JSON Dekodierungsfehler (KI): " + str(e))
                        output = {"error": "JSON Dekodierungsfehler (KI)"}
                    st.session_state[analysis_key] = output
                except subprocess.CalledProcessError as e:
                    st.error("Fehler beim Ausführen von AI_Analysis.py (KI):")
                    st.error(e.stderr)
                except Exception as ex:
                    st.error("Ein unerwarteter Fehler bei der KI Analyse:")
                    st.error(str(ex))
        
        # Ausgabe der KI Analyse-Ergebnisse:
        if st.session_state[analysis_key]:
            output = st.session_state[analysis_key]
            ai_rq = output.get("research_question", "").strip()
            ai_obj = output.get("objective", "").strip()
            ai_contr = output.get("contribution", "").strip()
            if ai_rq or ai_obj or ai_contr:
                st.write("**KI Analyse Ergebnisse:**")
                if ai_rq:
                    st.write("Forschungsfrage:", ai_rq)
                else:
                    st.write("Keine Forschungsfrage identifiziert.")
                if ai_obj:
                    st.write("Zielsetzung:", ai_obj)
                else:
                    st.write("Keine Zielsetzung identifiziert.")
                if ai_contr:
                    st.write("Wissenschaftlicher Beitrag:", ai_contr)
                else:
                    st.write("Kein wissenschaftlicher Beitrag identifiziert.")
            else:
                st.write("Es konnten keine Ergebnisse von KI Analysen identifiziert werden.")
        
        # LLM Analyse-Button: Startet LLM_Analysis.py für diesen Eintrag
        llm_analysis_key = f"llm_analysis_result_{i}"
        if llm_analysis_key not in st.session_state:
            st.session_state[llm_analysis_key] = None
        
        if st.button("LLM Analyse", key=f"llm_{i}"):
            st.write("**Debug:** LLM Analyse-Button für Eintrag", i, "wurde gedrückt.")
            with st.spinner(spinner_message):
                try:
                    result = subprocess.run(
                        [sys.executable, "LLM_Analysis.py", input_for_analysis],
                        capture_output=True, text=True, check=True
                    )
                    st.write("**Subprocess Output (LLM):**", result.stdout)
                    st.write("**Subprocess Return Code (LLM):**", result.returncode)
                    try:
                        llm_output = json.loads(result.stdout)
                    except json.JSONDecodeError as e:
                        st.error("LLM JSON Dekodierungsfehler: " + str(e))
                        llm_output = {"error": "LLM JSON Dekodierungsfehler"}
                    st.session_state[llm_analysis_key] = llm_output
                except subprocess.CalledProcessError as e:
                    st.error("Fehler beim Ausführen von LLM_Analysis.py:")
                    st.error(e.stderr)
                except Exception as ex:
                    st.error("Ein unerwarteter Fehler bei der LLM Analyse:")
                    st.error(str(ex))
        
        # Ausgabe der LLM Analyse-Ergebnisse:
        if st.session_state[llm_analysis_key]:
            llm_output = st.session_state[llm_analysis_key]
            llm_rq = llm_output.get("research_question", "").strip()
            llm_obj = llm_output.get("objective", "").strip()
            llm_contr = llm_output.get("contribution", "").strip()
            if llm_rq or llm_obj or llm_contr:
                st.write("**LLM Analyse Ergebnisse:**")
                st.write("Forschungsfrage:", llm_rq)
                st.write("Zielsetzung:", llm_obj)
                st.write("Wissenschaftlicher Beitrag:", llm_contr)
            elif "error" in llm_output:
                st.error(llm_output["error"])
            else:
                st.write("Es konnten keine Ergebnisse von LLM Analysen identifiziert werden.")
        
        st.markdown("---")
        time.sleep(0.5)

# Export-Funktion: CSV-Datei im Data-Ordner abspeichern
def generate_csv(with_ai=False):
    if 'results' not in st.session_state:
        return ""
    rows = []
    if with_ai:
        header = [
            "Title", "Author", "Published", "Summary", "Article Link", "DOI",
            "AI Research Question", "AI Objective", "AI Contribution",
            "LLM Research Question", "LLM Objective", "LLM Contribution"
        ]
    else:
        header = ["Title", "Author", "Published", "Summary", "Article Link", "DOI"]
    rows.append(header)
    
    results = st.session_state['results']
    for i, entry in enumerate(results):
        title = entry.title.replace('\n', ' ')
        author = entry.get('author', 'N/A')
        published = entry.get('published', 'N/A')
        summary = entry.get('summary', 'N/A')
        link = entry.link
        doi = get_doi_from_article(entry.link)
        base_row = [title, author, published, summary, link, doi if doi else ""]
        
        if with_ai:
            ai_key = f"analysis_result_{i}"
            if ai_key in st.session_state and st.session_state[ai_key]:
                ai_res = st.session_state[ai_key]
                ai_rq = ai_res.get("research_question", "")
                ai_obj = ai_res.get("objective", "")
                ai_contr = ai_res.get("contribution", "")
            else:
                ai_rq = ai_obj = ai_contr = ""
            llm_key = f"llm_analysis_result_{i}"
            if llm_key in st.session_state and st.session_state[llm_key]:
                llm_res = st.session_state[llm_key]
                llm_rq = llm_res.get("research_question", "")
                llm_obj = llm_res.get("objective", "")
                llm_contr = llm_res.get("contribution", "")
            else:
                llm_rq = llm_obj = llm_contr = ""
            row = base_row + [ai_rq, ai_obj, ai_contr, llm_rq, llm_obj, llm_contr]
        else:
            row = base_row
        rows.append(row)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return output.getvalue()

def generate_metadata():
    """
    Erstellt eine CSV-Datei mit zusätzlichen Metadaten zur Suche und Analyse:
    - Suchparameter (Suchterm1, Suchterm2, Operator, Max Results, Year Range)
    - Anzahl gefundener Publikationen
    - Anzahl der Publikationen mit verfügbarem Fulltext (PDF)
    - Timestamp
    """
    params = st.session_state.get("search_params", {})
    results = st.session_state.get("results", [])
    total_results = len(results)
    fulltext_count = count_full_text_available(results)
    header = ["Search Term 1", "Search Term 2", "Operator", "Max Results", "Year Range",
              "Total Results", "Fulltext Available Count", "Timestamp"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        params.get("term1", ""),
        params.get("term2", ""),
        params.get("operator", ""),
        params.get("max_results", ""),
        params.get("year_range", ""),
        total_results,
        fulltext_count,
        timestamp
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerow(row)
    return output.getvalue()

# Export ohne KI Ergebnisse
if st.button("Exportiere Ergebnisse (Ohne KI Ergebnisse)"):
    csv_without_ai = generate_csv(with_ai=False)
    metadata = generate_metadata()
    data_folder = os.path.join(os.getcwd(), "Data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path_csv = os.path.join(data_folder, f"ergebnisse_ohne_ki_{timestamp}.csv")
    file_path_meta = os.path.join(data_folder, f"metadata_ohne_ki_{timestamp}.csv")
    with open(file_path_csv, "w", encoding="utf-8") as f:
        f.write(csv_without_ai)
    with open(file_path_meta, "w", encoding="utf-8") as f:
        f.write(metadata)
    st.success(f"CSV-Dateien (Ohne KI) wurden im Data-Ordner unter {file_path_csv} und {file_path_meta} abgespeichert.")

# Export mit KI Ergebnisse
if st.button("Exportiere Ergebnisse (Mit KI Ergebnisse)"):
    with st.spinner("Starte alle fehlenden KI Analysen..."):
        update_all_analyses()
    csv_with_ai = generate_csv(with_ai=True)
    metadata = generate_metadata()
    data_folder = os.path.join(os.getcwd(), "Data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path_csv = os.path.join(data_folder, f"ergebnisse_mit_ki_{timestamp}.csv")
    file_path_meta = os.path.join(data_folder, f"metadata_mit_ki_{timestamp}.csv")
    with open(file_path_csv, "w", encoding="utf-8") as f:
        f.write(csv_with_ai)
    with open(file_path_meta, "w", encoding="utf-8") as f:
        f.write(metadata)
    st.success(f"CSV-Dateien (Mit KI) wurden im Data-Ordner unter {file_path_csv} und {file_path_meta} abgespeichert.")
