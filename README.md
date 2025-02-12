# EUonAIR-Assessment

# Programmieraufgabe: KI-gestützte Literaturrecherche und -analyse

Herzlich willkommen zu dieser Programmieraufgabe! 

Ziel ist es, Ihre Fähigkeiten in Python sowie im effektiven Einsatz von KI-Technologien zu demonstrieren. Im Fokus steht dabei die automatisierte Literaturrecherche und Analyse wissenschaftlicher Publikationen, inklusive der strukturierten Datenextraktion und einer anschließenden KI-gestützten Textanalyse.

## 1. Aufgabenbeschreibung

### 1.1 Literaturrecherche

#### Literaturdatenbank

- Wählen Sie eine wissenschaftliche Literaturdatenbank Ihrer Wahl, z. B.:
    - Semantic Scholar
    - Google Scholar
    - arXiv
    - OpenReview
    - ACM Digital Library
    - Science Direct (Open Access)

- **Wichtig:**
    - Verwenden Sie ausschließlich Schnittstellen (APIs) oder Zugriffe, die öffentlich und lizenzkonform sind. 
    - Achten Sie auf mögliche Rate Limits und Nutzungsbedingungen (Terms of Service, TOS)

#### Suchfunktion
- Ermöglichen Sie mindestens die logische Verknüpfung von Suchbegriffen per ```ÀND``` (Pflicht) und optional ```OR``` und ```NOT```.
  *Beispiel: ```"generative artificial intelligence" AND "education".```*
- Erlauben Sie eine zeitliche Eingrenzung der Publikationen, z. B. von 2020 bis 2024 oder der letzten N Jahre.
- (Optional) Filtern Sie nach Open-Access-Publikationen, sofern dies die ausgewählte Datenbank erlaubt.

#### Vermeidung von Scraping-Verstößen
- Scraping ohne explizite Zustimmung oder abseits öffentlich verfügbarer APIs ist zu vermeiden.
- Keine Volltexte von kostenpflichtigen Inhalten herunterladen oder verarbeiten (Urheberrechts- und Lizenzthemen).


### 1.2 Extraktion von bibliometrischen Informationen

#### Metadaten 

- Extrahieren Sie nach Möglichkeit folgende Felder aus den Suchergebnissen:
    - Titel der Publikation
    - Autoren
    - Erscheinungsjahr
    - DOI
    - URL
    - Abstract (falls verfügbar)
    - (Optional) Zitationsanzahl oder weitere interessante Kennzahlen
  
#### Fehlerbehandlung

- Falls bestimmte Daten (z. B. Abstracts oder DOI) nicht verfügbar sind, soll Ihr Code damit robust umgehen können (z. B. Eintrag mit "N/A" oder Auslassen dieses Felds).

#### Strukturierte Speicherung

- Speichern Sie die Ergebnisse in einem maschinenlesbaren Format (z. B. CSV, JSON, Pandas DataFrame, relationale Datenbank).
- Achten Sie auf eindeutige Dateibenennungen und ggf. eine verzeichnisbasierte Struktur (z. B. in einem Ordner ```*data/*```).

### 1.3 KI-gestützte Analyse

#### Ziel
- Identifizieren Sie in den (zugänglichen) Volltexten oder mindestens in den Abstracts:
    - Forschungsfrage(n) (Research Question)
    - Zielsetzung (Objective)
    - Wissenschaftlicher Beitrag (Contribution)

#### Erlaubte KI-Methoden
- Open-Source-Modelle (z. B. Hugging Face Transformers)
- Regelbasierte Ansätze (Regex, spaCy, NLTK, etc.)
- Kommerzielle APIs (z. B. OpenAI), unter der Bedingung, dass Sie keine API-Keys fest im Code hinterlegen (Umgang via Umgebungsvariablen oder separater Konfigurationsdatei).

#### Dokumentation
- Dokumentieren Sie Ihren Ansatz nachvollziehbar:
    - Welche Bibliotheken oder Modelle haben Sie verwendet? 
    - Wie erkennen Sie typische Formulierungen für Forschungsfrage, Zielsetzung und Beitrag?

#### Einschränkung auf lizenzfreie Inhalte
- Achten Sie darauf, nur lizenzkonforme bzw. frei verfügbare Inhalte (z. B. Open Access) für die Textanalyse zu verwenden.
- Laden Sie keine paywall-geschützten Volltexte herunter, um daraus automatisiert Daten zu extrahieren.


### 1.4 Ergebnisaufbereitung

1. Strukturiertes Ergebnis (Hauptdeliverable)
- Ziel: Erstellen Sie eine Sammlung von Publikationsobjekten, in der jede Publikation mit ihren extrahierten Informationen (Autoren, Titel, Jahr, DOI/URL, Abstract, KI-Analyse-Ergebnisse etc.) klar abgebildet wird.
- Mögliche Formate:
    - CSV-Datei(en)
    - JSON-Objekte in einer Liste
    - Pandas DataFrame (z. B. per to_csv oder to_json exportierbar)
    - Ein Eintrag pro Publikation in einer Datenbank (z. B. SQLite)
    - Stellen Sie sicher, dass jeder Eintrag eindeutig zugeordnet werden kann (z. B. über DOI, Titel etc.).

2. Zusätzliche Metadaten und Berichte
- Um Ihr Ergebnis nachvollziehbar und reproduzierbar zu machen, ergänzen Sie die genutzten Suchparameter, mögliche Filter (z. B. Zeiträume, AND/OR-Verknüpfungen) und ggf. statistische Übersichten (z. B. Anzahl gefundener Publikationen pro Jahr, häufigste Schlagworte).
- Diese Informationen können Sie z. B. in einem separaten Report (Markdown, PDF o. Ä.) bündeln oder auch direkt in einer zusätzlichen CSV/JSON-Datei speichern.

3. Empfehlung
- Durch die Trennung zwischen dem Hauptdeliverable (Publikationsdatensammlung) und den ergänzenden Reports (Metadaten zur Suche und Analyse) gewährleisten Sie eine klare Struktur und eine einfache Weiterverarbeitung.



## 2. Technische Anforderungen
- Programmiersprache: 
    - Python 3.8 oder höher
- Python-Bibliotheken: 
    - frei wählbar (z. B. requests, BeautifulSoup, pandas, spacy, transformers, openai, etc.)
- Modularer Code:
    - Nutzen Sie Funktionen oder Klassen, um die Schritte Recherche, Extraktion und Analyse klar zu trennen.
    - Verwenden Sie Type Hints (optional, aber empfehlenswert) und sinnvolle Code-Kommentare.
- Logging & Fehlerbehandlung:
    - Loggen Sie wichtige Prozessschritte (z. B. erfolgreiches Abfragen der Datenbank).
    - Behandeln Sie Timeouts, Rate-Limits und andere typische Fehlerfälle.
- Requirements/Dependency Management: 
    - Stellen Sie eine requirements.txt, Pipfile oder pyproject.toml bereit.
- Versionskontrolle:
    - Nutzen Sie Git und entwickeln Sie in einem eigenen Branch.
    - Begehen Sie keine sensiblen Daten wie API-Keys ins Repository.


## 3. Vorgehensweise & Abgabe

- Forken Sie dieses (oder ein bereitgestelltes) GitHub-Repository.
- Erstellen Sie einen eigenen Branch, in dem Sie Ihre Lösung implementieren.
- Implementieren Sie folgende Schritte:
    - Literaturrecherche (API-Zugriff / öffentlich zugängliche Schnittstelle)
    - Extraktion & Aufbereitung der Metadaten
    - KI-gestützte Analyse (Forschungsfrage, Zielsetzung, Beitrag)
- Ergebnisformat (z. B. CSV, JSON, Markdown-Report) 
- Dokumentation
    - Halten Sie Ihre Vorgehensweise in einer README.md fest (Installationsanleitung, Beispiele, technische Hinweise).
    - (Optional) Erstellen Sie eine Kurzfassung (PDF/Markdown) mit Details zur KI-Methodik und möglichen Erweiterungen.
- Testing
    - Ergänzen Sie Basis-Tests (z. B. einzelne Funktionen, Logging, Beispielaufrufe), um die Funktionsfähigkeit zu demonstrieren.
- Abgabe
    - Committen Sie Ihre fertige Lösung in Ihrem Branch und geben Sie uns Zugriff auf Ihr Repo.
    - (Optional) Stellen Sie einen Pull Request für eine direkte Code-Review im Hauptrepo.

## 4. Beispielfragen zur Orientierung

- Wie stellen Sie sicher, dass Sie nur lizenzkonforme Daten abrufen und keine Nutzungsbedingungen verletzen?
- Welche API- oder Webzugriffsmethoden setzen Sie ein und wie gehen Sie mit Rate Limits um?
- Wie identifizieren Sie mithilfe von KI oder regelbasierten Methoden die Forschungsfrage, Zielsetzung und Beitrag eines Abstracts?
- Welche Fehlerquellen erwarten Sie (z. B. fehlende Abstracts, fehlerhafte Metadaten) und wie fangen Sie diese ab?
- Wie könnte das System in Zukunft erweitert werden (z. B. Bezug auf Volltexte, semantische Suche, Zitationsanalyse etc.)?


## 5. Bewertungskriterien

- Funktionalität (40%)
    - Erfüllung aller genannten Anforderungen (Recherche, Datenextraktion, KI-Analyse)
    - Robustheit (Umgang mit Rate Limits, fehlenden Daten etc.)
    - Qualität der KI-Integration

- Code-Qualität (30%)
    - Struktur und Lesbarkeit (Module, Funktionen, Kommentare, Type Hints)
    - Fehlerbehandlung und Logging
    - Testabdeckung (zumindest grundlegende Tests)

- Dokumentation (20%)
    - Vollständigkeit (README, Installationsanleitung, Beispielaufruf)
    - Nachvollziehbarkeit (Erklärung von KI-Methoden, Reproduzierbarkeit)

- Innovation (10%)
    - Kreative Ansätze oder zusätzliche Features (z. B. Stichwortstatistiken, visuelle Aufbereitung)
    - Effizienz der Implementierung (Performanz, klare Datenstruktur)


### 6. Einschränkungen und Hinweise

- Keine geschützten APIs oder lizenzrechtlich bedenkliche Inhalte verwenden.
- Kein Download von kostenpflichtigen Volltexten (Dokumenten hinter Paywalls).
- API-Keys (falls nötig) nicht im Code committen – nutzen Sie z. B. Umgebungsvariablen oder lokale Konfigurationsdateien, die nicht Teil des Repos sind.
- Dokumentieren Sie ggf. Kosten für kommerzielle APIs (OpenAI usw.), falls Sie diese einsetzen.
- Eine Test-Ausführung mit kleinem Datensatz (z. B. 3–5 Publikationen) reicht aus, um den Ablauf zu demonstrieren.


### 7. Abgabetermin und Kontakt

- Abgabefrist: 20.02.2025
- Einreichung: GitHub-/Download-Link oder GitHub-Pull-Request
- Kontakt für Rückfragen: carsten.lanquillon@hs-heilbronn.de

Viel Erfolg bei der Bearbeitung!

Wir freuen uns auf Ihre kreative und saubere Umsetzung der Aufgabe. Bei Fragen oder Problemen stehen wir Ihnen innerhalb des vorgegebenen Rahmens gerne zur Verfügung.

