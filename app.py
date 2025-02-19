from flask import Flask, request, jsonify
import os
import re
from pdfminer.high_level import extract_text
from docx import Document
from rake_nltk import Rake
import nltk

# Download necessary NLTK resources
nltk.download('stopwords')
nltk.download('punkt_tab')

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords_rake(text):
    """
    Use RAKE (Rapid Automatic Keyword Extraction) to extract keywords.
    """
    r = Rake()  # RAKE uses NLTK's stopwords by default
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    return keywords

# ---------------------------
# API Endpoint
# ---------------------------

@app.route('/process_resume', methods=['POST'])
def process_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print("File saved at:", file_path)

        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.filename.lower().endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        print("Raw text extracted:", text[:100])  # Debug: first 100 characters
        processed_text = preprocess_text(text)
        print("Processed text:", processed_text[:100])  # Debug: first 100 characters

        keywords = extract_keywords_rake(processed_text)
        print("Extracted keywords:", keywords)

        return jsonify({
            'extracted_text': processed_text,
            'keywords': keywords
        }), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({'error': str(e)}), 500

# ---------------------------
# Main Entry Point
# ---------------------------

if __name__ == '__main__':
    app.run(debug=True)
