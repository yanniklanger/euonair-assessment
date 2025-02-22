# EUonAIR-Assessment: KI-gestützte Literaturrecherche und -analyse

Dieses Projekt demonstriert eine automatisierte Pipeline zur Literaturrecherche und -analyse wissenschaftlicher Publikationen. Die Lösung kombiniert klassische (regelbasierte) Methoden und moderne LLM-gestützte Ansätze, um bibliometrische Daten und inhaltliche Informationen (wie Forschungsfrage, Zielsetzung und wissenschaftlicher Beitrag) aus Abstracts und vollständigen Open-Access-Artikeln zu extrahieren.

---

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Projektstruktur](#projektstruktur)
- [Installation](#installation)
- [Nutzung und Beispielaufruf](#nutzung-und-beispielaufruf)
- [KI-Methoden und Extraktionslogik](#ki-methoden-und-extraktionslogik)
- [Kosten der kommerziellen APIs](#kosten-der-kommerziellen-apis)
- [Testing](#testing)
- [Reproduzierbarkeit und Erweiterungsmöglichkeiten](#reproduzierbarkeit-und-erweiterungsmöglichkeiten)
- [Kontakt](#kontakt)

---

## Überblick

Das Projekt umfasst:

- **Literaturrecherche:**  
  Abfrage der arXiv-API, um Publikationen basierend auf Suchbegriffen (mit logischen Operatoren wie AND/OR) und Zeitfiltern abzurufen.

- **Extraktion bibliometrischer Informationen:**  
  Aus den arXiv-Ergebnissen werden Titel, Autoren, Veröffentlichungsjahr, DOI, URL und Abstract extrahiert. Fehlende Daten werden robust behandelt.

- **KI-gestützte Analyse:**  
  Zwei Ansätze werden kombiniert:
  1. **Regelbasierte Analyse (AI_Analysis.py):**  
     Mithilfe von NLTK, Regex und heuristischen Regeln wird der relevante Text (vom Beginn der "Introduction" bis zum nächsten Kapitel wie "Methodology" oder "Results") analysiert, um die Forschungsfrage, Zielsetzung und den wissenschaftlichen Beitrag zu extrahieren.
  2. **LLM-gestützte Analyse (LLM_Analysis.py):**  
     Über LangChain, Embedding-Techniken und FAISS wird der Text in kleinere Chunks unterteilt, semantisch analysiert und die gewünschten Informationen extrahiert.

- **Ergebnisaufbereitung:**  
  Die Ergebnisse werden in CSV-Dateien exportiert. Es gibt zwei Varianten:
  - **Ohne KI-Ergebnisse:** Nur Basisdaten der Publikationen.
  - **Mit KI-Ergebnissen:** Zusätzlich zu den Basisdaten werden Ergebnisse der KI-Analysen (regelbasiert und LLM-gestützt) in separaten Spalten ausgegeben.
  Beide CSV-Dateien werden zusammen mit einer Metadaten-Datei (mit den Suchparametern, Filterkriterien und statistischen Informationen) im Unterordner `Data` gespeichert – pro Exportvorgang wird ein neuer Dateiname (mit Timestamp) generiert.

---

## Projektstruktur

- **main.py:**  
  Die Hauptanwendung, die:
  - Die arXiv-Suche über eine Streamlit-Oberfläche steuert.
  - Die Suchergebnisse anzeigt.
  - Manuelle sowie automatische Analysen (über Subprozesse) startet.
  - Ergebnisse und ergänzende Metadaten als CSV-Dateien im `Data`-Ordner speichert.

- **AI_Analysis.py:**  
  Enthält einen regelbasierten Ansatz zur Extraktion der Forschungsfrage, Zielsetzung und des wissenschaftlichen Beitrags aus dem Text (PDF oder Abstract).  
  Der Text wird dabei auf den relevanten Einleitungsteil (von "Introduction" bis zum nächsten Kapitel) beschränkt.

- **LLM_Analysis.py:**  
  Nutzt KI-Methoden (via LangChain, Embeddings und FAISS), um dieselben Felder semantisch zu extrahieren.  
  Ein benutzerdefinierter Prompt steuert die Extraktion, und das Ergebnis wird als JSON zurückgeliefert.

- **apikey.py:**  
  Eine separate Datei, in der der OpenAI API-Key hinterlegt wird. Diese Datei sollte aufgrund der Sensibilität des Schlüssels nicht ins Repository aufgenommen werden.

- **Data/**  
  Ein Unterordner, in dem alle exportierten CSV-Dateien (Ergebnisse und Metadaten) abgelegt werden. Jede Exportaktion erzeugt neue Dateien mit einem Timestamp im Dateinamen.

- **test_functions.py:**  
  Enthält Basis-Tests (mit `unittest`), die zentrale Funktionen wie die DOI-Extraktion und PDF-Text-Extraktion überprüfen.

---

## Installation

1. **Python-Version:**  
   Das Projekt benötigt Python 3.8 oder höher.

### Abhängigkeiten installieren:

`pip install -r requirements.txt`
- Die requirements.txt enthält alle notwendigen Pakete.

### API-Key einrichten:
- Legen Sie eine Datei apikey.py im Hauptverzeichnis an, nach folgendem Muster:
`OPENAI_API_KEY = "Ihr_OpenAI_API_Key"`
- Alternativ können Sie die Umgebungsvariable OPENAI_API_KEY setzen.

## Nutzung und Beispielaufruf
**Starten der Anwendung:**
- Führen Sie im Projektverzeichnis den folgenden Befehl aus:
`streamlit run main.py`
- Dadurch wird die Streamlit-Oberfläche in Ihrem Browser geöffnet.

**Literaturrecherche:**
- Geben Sie Ihre Suchparameter (Suchterm 1, Suchterm 2, Operator, Max Results, Jahrbereich) in die Oberfläche ein und klicken Sie auf Search. Die arXiv-Ergebnisse werden dann angezeigt.

**Analyse:**
- Für jeden Eintrag können Sie manuell per Button die regelbasierte KI-Analyse (über AI_Analysis.py) oder die LLM-gestützte Analyse (über LLM_Analysis.py) starten.
- Alternativ können Sie über den Export-Button fehlende Analysen automatisch starten lassen.

**Export:**
- Exportiere Ergebnisse (Ohne KI Ergebnisse): Exportiert die Basisdaten der Publikationen in eine CSV-Datei sowie eine separate Metadaten-CSV.
- Exportiere Ergebnisse (Mit KI Ergebnisse): Startet alle fehlenden Analysen und exportiert dann die vollständigen Ergebnisse (Basisdaten + KI-Ergebnisse) zusammen mit den Metadaten in zwei CSV-Dateien.
- Die Dateien werden im Data-Ordner gespeichert, und jede Exportaktion erzeugt neue Dateien mit Timestamp im Dateinamen.

**Beispielaufruf:**
- Installation der Abhängigkeiten:
`pip install -r requirements.txt`

- Starten der Anwendung:
`streamlit run main.py`

- Ausführen der Tests:
`python -m unittest discover`

## KI-Methoden und Extraktionslogik
### Regelbasierte Analyse (AI_Analysis.py)
**Textvorverarbeitung:**
- Der Text (entweder aus einem PDF oder Abstract) wird mit Hilfe von NLTK in Sätze zerlegt.
**Einschränkung auf relevanten Bereich:**
- Mittels Regex wird der Text auf den Abschnitt von "Introduction" bis zum nächsten Kapitel (z. B. "Methodology" oder "Results") begrenzt.
**Extraktion:**
Es werden die ersten Sätze ermittelt, die:
- Bei der Forschungsfrage ein Fragezeichen oder bestimmte Schlüsselwörter enthalten.
- Bei der Zielsetzung Schlüsselwörter wie "objective", "goal" etc. beinhalten.
- Beim wissenschaftlichen Beitrag nach Begriffen wie "contribution", "beitrag", "innovation" gesucht wird.
**Output:**
- Die Ergebnisse werden als JSON mit den Schlüsseln research_question, objective und contribution zurückgegeben.
### LLM-gestützte Analyse (LLM_Analysis.py)
**Text-Splitting:**
- Der Text wird in kleinere Chunks (ca. 1000 Zeichen) unterteilt, um das Token-Limit zu umgehen.
**Embeddings und Vektor-Store:**
- Für jeden Chunk werden Embeddings mithilfe des OpenAI-Embedding-Modells (hier explizit konfiguriert als text-embedding-3-small) erzeugt und in einem FAISS-Vektor-Store abgelegt.
**Retrieval und LLM:**
- Ein Retriever holt die relevantesten Chunks aus dem Vektor-Store. Diese werden über einen benutzerdefinierten Prompt an das LLM (gpt-4o) übergeben.
**Output:**
- Das LLM liefert die extrahierten Informationen als JSON zurück, analog zur regelbasierten Analyse.

## Kosten der kommerziellen APIs
- Für die OpenAI-Dienste werden folgende Kosten angenommen:

***Embeddings:***
- ca. 62.500 Seiten pro Dollar
***LLM (Price per 1M tokens):***
- Input: $2.50
- Cached Input: $1.25
- Output: $10.00

## Testing
Die Testdatei `test_functions.py` dient dazu, die grundlegende Funktionalität einiger zentraler Funktionen des Projekts zu verifizieren. Dabei werden folgende Aspekte geprüft:

- **DOI-Extraktion:**  
  Es wird überprüft, ob aus einer Beispiel-URL ein korrekter DOI (beginnend mit „https://doi.org/“) extrahiert wird oder – falls kein DOI vorhanden ist – `None` zurückgegeben wird.

- **PDF-Text-Extraktion (ungültige URL):**  
  Der Test stellt sicher, dass bei einer ungültigen URL (z. B. einer nicht existierenden Domain) die Funktion zur PDF-Text-Extraktion ordnungsgemäß `None` zurückliefert, anstatt eine Exception auszulösen.

- **PDF-Text-Extraktion (gültige PDF):**  
  Falls eine Test-PDF im Projektverzeichnis vorhanden ist, wird getestet, ob der Text korrekt als nicht-leerer String extrahiert wird.

Die Tests werden über das Modul `unittest` ausgeführt und helfen, sicherzustellen, dass die wichtigsten Komponenten wie DOI-Extraktion und PDF-Text-Extraktion erwartungsgemäß funktionieren, bevor das gesamte System in der Streamlit-Anwendung genutzt wird.

Ausführung der Tests:
`python -m unittest discover`
Dadurch werden alle Tests erkannt und ausgeführt.

## Reproduzierbarkeit und Erweiterungsmöglichkeiten
### Modularität:
Alle Funktionen und Schritte sind klar in separate Dateien unterteilt (main.py, AI_Analysis.py, LLM_Analysis.py). Dies erleichtert die Wartung und Erweiterung (z. B. um weitere Analysefelder oder Visualisierungen).

### Dokumentation der Suchparameter und Metadaten:
Alle eingegebenen Suchparameter sowie statistische Übersichten (z. B. Anzahl der gefundenen Publikationen, Anzahl Fulltext-Available) werden in einer separaten Metadaten-CSV gespeichert. Dies erhöht die Nachvollziehbarkeit und Reproduzierbarkeit der Ergebnisse.

### Erweiterungen:
Das System lässt sich leicht erweitern – z. B. um:

- Zitationsanalysen und interaktive Visualisierungen.
- Automatisierte Trend- und Clusteranalyse.

## Kontakt
Bei Fragen oder Problemen wenden Sie sich bitte an:
yannik.langer@hs-heilbronn.de

