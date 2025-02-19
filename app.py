from flask import Flask, request, jsonify
import os
import re
import spacy
from pdfminer.high_level import extract_text
from docx import Document

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# ---------------------------
# Utility Functions
# ---------------------------

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using pdfminer.six.
    """
    text = extract_text(file_path)
    return text

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file using python-docx.
    """
    doc = Document(file_path)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

def preprocess_text(text):
    """
    Preprocess the extracted text by removing extra whitespace.
    """
    # Replace multiple spaces and newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords_spacy(text):
    """
    Use spaCy to extract keywords based on noun chunks and named entities.
    """
    doc = nlp(text)
    # Extract noun chunks as potential keywords
    keywords = {chunk.text.lower() for chunk in doc.noun_chunks}
    # Also add named entities
    for ent in doc.ents:
        keywords.add(ent.text.lower())
    return list(keywords)

# ---------------------------
# API Endpoints
# ---------------------------

@app.route('/process_resume', methods=['POST'])
def process_resume():
    """
    API endpoint to upload a resume, extract text, preprocess it, 
    and return extracted keywords.
    """
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the uploaded file to the configured folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Determine file type and extract text accordingly
    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file.filename.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    # Preprocess the extracted text
    processed_text = preprocess_text(text)
    # Extract keywords using spaCy
    keywords = extract_keywords_spacy(processed_text)

    # Return the results as JSON
    return jsonify({
        'extracted_text': processed_text,
        'keywords': keywords
    }), 200

# ---------------------------
# Main
# ---------------------------

if __name__ == '__main__':
    app.run(debug=True)
