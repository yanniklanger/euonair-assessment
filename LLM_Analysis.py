#!/usr/bin/env python3
import sys
import requests
import io
import PyPDF2
import json
import os
import re
import nltk

# Importiere die notwendigen Module für OpenAI und FAISS
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
except ImportError:
    raise ImportError("Bitte installiere langchain-openai: pip install langchain-openai")

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Lade NLTK-Paket für die Textverarbeitung
nltk.download('punkt', quiet=True)

# Lade den OpenAI API-Key aus der Datei oder der Umgebungsvariable
try:
    from apikey import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY ist nicht gesetzt. Bitte in apikey.py angeben oder als Umgebungsvariable setzen.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def extract_text_from_pdf(pdf_url):
    """Lädt eine PDF-Datei von der angegebenen URL herunter und extrahiert den Text."""
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

def rag_analysis(text):
    """Führt eine Retrieval-Augmented Generation (RAG) Analyse durch und gibt die Ergebnisse im JSON-Format zurück."""
    # Text in kleinere Chunks teilen
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    # Embeddings generieren und FAISS-Vektorstore erstellen
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")
    vectorstore = FAISS.from_texts(chunks, embeddings)

    # Erstelle einen Retriever, um relevante Textabschnitte zu finden
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # OpenAI-LLM initialisieren
    llm = ChatOpenAI(temperature=0, max_tokens=500, api_key=OPENAI_API_KEY, model="gpt-4o")

    # Prompt für die Extraktion der Forschungsfrage, Zielsetzung und Beitrag
    prompt_template = """
Bitte extrahiere aus dem folgenden wissenschaftlichen Text:
1. Die Forschungsfrage
2. Die Zielsetzung
3. Den wissenschaftlichen Beitrag

Gib die Antwort in folgendem JSON-Format zurück:
{{
  "research_question": "<Forschungsfrage>",
  "objective": "<Zielsetzung>",
  "contribution": "<wissenschaftlicher Beitrag>"
}}

Text:
{context}
"""
    prompt = PromptTemplate(input_variables=["context"], template=prompt_template)

    # RetrievalQA-Kette initialisieren
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )

    # Die Analyse mit einer Abfrage durchführen
    query = "Extrahiere die relevanten Informationen."
    result = qa_chain.invoke(query)

    # Verarbeitung des Ergebnisses
    if isinstance(result, dict) and 'result' in result:
        result = result['result']

    if isinstance(result, str):
        result_text_clean = re.sub(r"json|```json|```", "", result).strip()
    else:
        result_text_clean = str(result)

    # JSON-Daten aus dem Text extrahieren
    start = result_text_clean.find('{')
    if start != -1:
        result_text_clean = result_text_clean[start:]

    try:
        # JSON-Parsing durchführen und None-Werte durch leere Strings ersetzen
        output = json.loads(result_text_clean)
        output = {k: (v if v is not None else "") for k, v in output.items()}
    except Exception as e:
        # Fehlerbehandlung bei Parsing-Problemen
        output = {"error": f"Das Ergebnis konnte nicht als JSON geparst werden: {result_text_clean}"}

    return output

def main():
    """Hauptfunktion: Akzeptiert entweder eine PDF-URL oder einen Text und führt die Analyse durch."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Kein Input übergeben"}))
        sys.exit(1)

    input_value = sys.argv[1]

    # PDF-Text extrahieren oder Eingabetext direkt verwenden
    if input_value.startswith("http"):
        text = extract_text_from_pdf(input_value)
        if not text:
            print(json.dumps({"error": "Text-Extraktion aus PDF fehlgeschlagen"}))
            sys.exit(1)
    else:
        text = input_value

    # Analyse durchführen und Ergebnisse ausgeben
    analysis = rag_analysis(text)
    print(json.dumps(analysis))

if __name__ == "__main__":
    main()
