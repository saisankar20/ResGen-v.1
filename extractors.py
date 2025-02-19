from pdfminer.high_level import extract_text
from docx import Document
import re

def extract_text_from_pdf(file_path):
    return extract_text(file_path)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
