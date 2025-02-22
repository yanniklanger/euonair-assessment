#!/usr/bin/env python3
import sys
import requests
import io
import PyPDF2
import json
import os
import nltk

# Verwende den neuen Import von langchain-openai
try:
    from langchain_openai import OpenAI
except ImportError:
    raise ImportError("Bitte installiere langchain-openai: pip install langchain-openai")

# Neue Imports laut Deprecation-Warnungen:
try:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_community.llms import OpenAI as CommunityOpenAI
except ImportError:
    raise ImportError("Bitte installiere langchain-community: pip install -U langchain-community")

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

nltk.download('punkt', quiet=True)

# Lade den OpenAI API Key entweder aus apikey.py oder aus der Umgebungsvariable
try:
    from apikey import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY ist nicht gesetzt. Bitte in apikey.py angeben oder als Umgebungsvariable setzen.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def extract_text_from_pdf(pdf_url):
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
    """
    Führt eine RAG-Analyse durch:
    1. Teilt den Text in Chunks.
    2. Erzeugt Embeddings für die Chunks.
    3. Baut einen Vektor-Store (FAISS).
    4. Erstellt eine RetrievalQA-Kette, die gezielt nach den relevanten Informationen fragt.
    """
    # Schritt 1: Text in Chunks aufteilen
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    
    # Schritt 2: Embeddings erzeugen
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small")
    
    # Schritt 3: Vektor-Store mit FAISS erstellen
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    # Schritt 4: Retrieval-Kette erstellen
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Verwende CommunityOpenAI (aus langchain-community) für den LLM-Teil
    llm = CommunityOpenAI(temperature=0, max_tokens=500, openai_api_key=OPENAI_API_KEY, model_name="gpt-4o")
    
    # Definiere deinen benutzerdefinierten Prompt und verwende "context" als Input-Variable
    prompt_template = """
Bitte extrahiere aus dem folgenden wissenschaftlichen Text:
1. Die Forschungsfrage (falls vorhanden)
2. Die Zielsetzung
3. Den wissenschaftlichen Beitrag

Falls das Paper keine explizite Forschungsfrage nennt, lass sie aus. Erfinde keine Forschungsfrage.

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
    
    # Erstellt die RetrievalQA-Kette und übergibt den custom Prompt via chain_type_kwargs
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    
    # Dummy-Frage, da das Prompt den gesamten Text verarbeitet.
    query = "Extrahiere die relevanten Informationen."
    result = qa_chain.run(query)
    
    # Entfernt unerwünschten Präfix (z. B. "score.") vor der ersten geschweiften Klammer:
    start = result.find('{')
    if start != -1:
        result_text_clean = result[start:]
    else:
        result_text_clean = result

    try:
        output = json.loads(result_text_clean)
    except Exception as e:
        output = {"error": f"Das Ergebnis konnte nicht als JSON geparst werden: {result}"}
    return output

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Kein Input übergeben"}))
        sys.exit(1)
    
    input_value = sys.argv[1]
    
    # Falls der Input mit "http" beginnt, als PDF-URL interpretieren
    if input_value.startswith("http"):
        text = extract_text_from_pdf(input_value)
        if not text:
            print(json.dumps({"error": "Text-Extraktion aus PDF fehlgeschlagen"}))
            sys.exit(1)
    else:
        text = input_value
    
    analysis = rag_analysis(text)
    print(json.dumps(analysis))

if __name__ == "__main__":
    main()
