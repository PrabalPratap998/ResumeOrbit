"""
Flask API server for Resume Parser
Provides endpoints for parsing resumes via text input or file upload
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename

# Add parser directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'parser'))

from resume_parser import parse_resume
from job_scraper import scrape_jobs

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path):
    """
    Extract text from different file formats.
    Supports .txt, .pdf (basic), .docx (basic)
    """
    file_ext = file_path.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_ext == 'pdf':
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                return text
            except ImportError:
                return "PDF support requires PyPDF2. Install with: pip install PyPDF2"
        
        elif file_ext == 'docx':
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "DOCX support requires python-docx. Install with: pip install python-docx"
        
        else:
            return "Unsupported file format"
    
    except Exception as e:
        return f"Error reading file: {str(e)}"


@app.route('/', methods=['GET'])
def home():
    """Health check and API information."""
    return jsonify({
        'status': 'online',
        'message': 'Resume Parser API',
        'version': '1.0',
        'endpoints': {
            'POST /parse/text': 'Parse resume from text input',
            'POST /parse/file': 'Parse resume from file upload',
            'GET /health': 'Health check'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/parse/text', methods=['POST'])
def parse_text():
    """
    Parse resume from text input.
    
    Expected JSON:
    {
        "resume_text": "Resume content here..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({
                'error': 'Missing resume_text field',
                'message': 'Please provide resume_text in JSON body'
            }), 400
        
        resume_text = data['resume_text'].strip()
        
        if not resume_text:
            return jsonify({
                'error': 'Empty resume',
                'message': 'Resume text cannot be empty'
            }), 400
        
        # Parse the resume
        parsed_data = parse_resume(resume_text)
        
        return jsonify({
            'success': True,
            'data': parsed_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Parsing error',
            'message': str(e)
        }), 500


@app.route('/parse/file', methods=['POST'])
def parse_file():
    """
    Parse resume from file upload.
    
    Supported formats: .txt, .pdf, .docx
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please upload a file'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Supported formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save and process file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        resume_text = extract_text_from_file(file_path)
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass
        
        if not resume_text or resume_text.startswith('Error') or resume_text.startswith('PDF support'):
            return jsonify({
                'error': 'File processing error',
                'message': resume_text
            }), 400
        
        # Parse the resume
        parsed_data = parse_resume(resume_text)
        
        return jsonify({
            'success': True,
            'data': parsed_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': str(e)
        }), 500


@app.route('/scrape/jobs', methods=['POST'])
def scrape_jobs_endpoint():
    """
    Scrape job listings from the web.
    
    Expected JSON:
    {
        "keywords": "Python Developer",
        "location": "New York",
        "pages": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({
                'error': 'Missing keywords',
                'message': 'Please provide job search keywords'
            }), 400
        
        keywords = data['keywords'].strip()
        location = data.get('location', '').strip()
        pages = int(data.get('pages', 1))
        
        if not keywords:
            return jsonify({
                'error': 'Empty keywords',
                'message': 'Keywords cannot be empty'
            }), 400
        
        # Scrape jobs
        jobs = scrape_jobs(keywords, location, pages)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Scraping error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Starting Resume Parser API Server...")
    print("📍 Running on http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
