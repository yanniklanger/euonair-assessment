#!/usr/bin/env python3
import sys
import requests
import io
import PyPDF2
import nltk
import json
import re

# Stellt sicher, dass der Punkt-Satz-Tokenizer verfügbar ist
nltk.download('punkt', quiet=True)

def extract_text_from_pdf(pdf_url):
    #Extrahiert den Text aus einem PDF von der angegebenen URL.
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(pdf_url, headers=headers)
        if response.status_code != 200:
            return None
        file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        return None

def restrict_to_introduction(text):
    # Schneidet den Text so zu, dass nur der Bereich ab dem ersten Vorkommen von "Introduction" bis zum ersten Auftreten eines Kapitels, das "Methodology" oder "Results" heißt, betrachtet wird.
    # Falls keine dieser Überschriften gefunden wird, wird der gesamte Text ab "Introduction" zurückgegeben.
    lower_text = text.lower()
    intro_match = re.search(r'introduction', lower_text)
    if intro_match:
        start = intro_match.start()
    else:
        start = 0
    subtext = text[start:]
    # Sucht nach der nächsten Überschrift: "methodology" oder "results"
    chapter_match = re.search(r'\n\s*(methodology|results)\b', subtext, re.IGNORECASE)
    if chapter_match:
        end = chapter_match.start()
        return subtext[:end]
    else:
        return subtext

def extract_research_question(text):
    # Extrahiert einen Satz, der Hinweise auf die Fragestellung enthält: Beinhaltet ein Fragezeichen oder eines der Schlüsselwörter "research question", "RQ" oder "forschungsfrage".
    text = restrict_to_introduction(text)
    sentences = nltk.sent_tokenize(text)
    keywords = ["research question", "rq", "forschungsfrage"]
    
    # Zuerst: Suche nach einem Satz mit einem Fragezeichen
    for sentence in sentences:
        if "?" in sentence and len(sentence.split()) > 5:
            return sentence.strip()
    
    # Falls kein Fragezeichen gefunden wird, suche nach den Schlüsselwörtern
    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in keywords) and len(sentence.split()) > 5:
            return sentence.strip()
    
    return None

def extract_objective(text):
    # Extrahiert einen Satz, der Hinweise auf Zielsetzung enthält. Schlüsselwörter: "objective", "goal", "aim", "zielsetzung" oder "ziel"
    text = restrict_to_introduction(text)
    sentences = nltk.sent_tokenize(text)
    keywords = ["objective", "goal", "aim", "zielsetzung", "ziel"]
    
    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in keywords) and len(sentence.split()) > 5:
            return sentence.strip()
    return None

def extract_contribution(text):
    # Extrahiert einen Satz, der Hinweise auf den wissenschaftlichen Beitrag enthält. Schlüsselwörter:  "contribution", "beitrag" oder "innovation".
    text = restrict_to_introduction(text)
    sentences = nltk.sent_tokenize(text)
    keywords = ["contribution", "beitrag", "innovation"]
    
    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in keywords) and len(sentence.split()) > 5:
            return sentence.strip()
    return None

def extract_fields(text):
    # Extrahiert die gewünschten Felder aus dem eingeschränkten Text
    fields = {}
    rq = extract_research_question(text)
    fields["research_question"] = rq if rq else ""
    
    obj = extract_objective(text)
    fields["objective"] = obj if obj else ""
    
    contrib = extract_contribution(text)
    fields["contribution"] = contrib if contrib else ""
    
    return fields

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No input provided"}))
        sys.exit(1)
    
    input_value = sys.argv[1]
    
    # Falls der Input mit "http" beginnt, als PDF-URL interpretieren, sonst als direkter Text (z.B. Abstract)
    if input_value.startswith("http"):
        text = extract_text_from_pdf(input_value)
        if not text:
            print(json.dumps({"error": "Text extraction from PDF failed"}))
            sys.exit(1)
    else:
        text = input_value

    fields = extract_fields(text)
    print(json.dumps(fields, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
