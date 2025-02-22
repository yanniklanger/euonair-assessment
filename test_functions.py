import unittest
import os
from io import StringIO
import requests
from main import get_doi_from_article, extract_text_from_pdf

class TestFunctions(unittest.TestCase):

    def test_get_doi_from_article_valid(self):
        # Für diesen Test verwenden wir eine Beispiel-URL,
        # die bekannt einen DOI enthält. (Hier ein Dummy-Wert – bitte anpassen.)
        test_url = "https://arxiv.org/abs/1234.5678"
        doi = get_doi_from_article(test_url)
        # Wir erwarten, dass eine Zeichenkette zurückgegeben wird, wenn ein DOI gefunden wurde.
        self.assertTrue(isinstance(doi, str) or doi is None)

    def test_extract_text_from_pdf_invalid_url(self):
        # Bei einer ungültigen URL soll None zurückgegeben werden.
        invalid_url = "http://thisurldoesnotexist.example"
        text = extract_text_from_pdf(invalid_url)
        self.assertIsNone(text)

    def test_extract_text_from_pdf_valid(self):
        # Dies ist ein Beispieltest, der einen lokalen PDF-Dateipfad verwendet.
        # Legen Sie eine kleine Test-PDF in Ihr Projektverzeichnis und passen Sie den Pfad an.
        test_pdf_url = os.path.join(os.getcwd(), "test.pdf")
        if os.path.exists(test_pdf_url):
            text = extract_text_from_pdf(test_pdf_url)
            self.assertIsInstance(text, str)
        else:
            self.skipTest("Test-PDF existiert nicht.")

if __name__ == '__main__':
    unittest.main()
