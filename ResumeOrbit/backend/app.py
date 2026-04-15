import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser.resume_parser_new import parse_resume
from job_scraper_new import scrape_jobs

try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

try:
    import docx
except Exception:  # pragma: no cover
    docx = None


app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def _read_pdf(path: str) -> str:
    if PdfReader is None:
        raise RuntimeError('PDF support is not available. Install PyPDF2.')

    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or '')
    return '\n'.join(text_parts).strip()


def _read_docx(path: str) -> str:
    if docx is None:
        raise RuntimeError('DOCX support is not available. Install python-docx.')

    document = docx.Document(path)
    return '\n'.join([p.text for p in document.paragraphs if p.text]).strip()


def extract_text_from_file(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in {'.txt'}:
        return _read_txt(file_path)
    if ext in {'.pdf'}:
        return _read_pdf(file_path)
    if ext in {'.docx'}:
        return _read_docx(file_path)

    raise RuntimeError(f'Unsupported file type: {ext}')


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'service': 'ResumeOrbit Python API',
        'endpoints': {
            'parse_text': '/parse/text',
            'parse_file': '/parse/file',
            'scrape_jobs': '/scrape/jobs'
        }
    }), 200


@app.route('/parse/text', methods=['POST'])
def parse_text_endpoint():
    try:
        data = request.get_json(silent=True) or {}
        resume_text = (data.get('resume_text') or '').strip()

        if not resume_text:
            return jsonify({
                'success': False,
                'error': 'Missing resume_text',
                'message': 'Please provide resume_text'
            }), 400

        parsed_data = parse_resume(resume_text)

        return jsonify({
            'success': True,
            'data': parsed_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Processing error',
            'message': str(e)
        }), 500


@app.route('/parse/file', methods=['POST'])
def parse_file_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Missing file',
                'message': 'No file uploaded'
            }), 400

        uploaded_file = request.files['file']
        if not uploaded_file or not uploaded_file.filename:
            return jsonify({
                'success': False,
                'error': 'Missing filename',
                'message': 'Uploaded file has no filename'
            }), 400

        _, ext = os.path.splitext(uploaded_file.filename)
        ext = ext.lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        uploaded_file.save(file_path)

        try:
            resume_text = extract_text_from_file(file_path)
        finally:
            try:
                os.remove(file_path)
            except Exception:
                pass

        if not resume_text:
            return jsonify({
                'success': False,
                'error': 'File processing error',
                'message': 'Could not extract text from file'
            }), 400

        parsed_data = parse_resume(resume_text)

        return jsonify({
            'success': True,
            'data': parsed_data,
            'raw_text': resume_text
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Processing error',
            'message': str(e)
        }), 500


@app.route('/scrape/jobs', methods=['POST'])
def scrape_jobs_endpoint():
    try:
        data = request.get_json(silent=True) or {}

        if 'keywords' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing keywords',
                'message': 'Please provide job search keywords'
            }), 400

        keywords = str(data.get('keywords', '')).strip()
        location = str(data.get('location', '')).strip()
        pages = int(data.get('pages', 1) or 1)

        if not keywords:
            return jsonify({
                'success': False,
                'error': 'Empty keywords',
                'message': 'Keywords cannot be empty'
            }), 400

        jobs = scrape_jobs(keywords, location, pages)

        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Scraping error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print('🚀 Starting ResumeOrbit Python API Server...')
    print('📍 Running on http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
