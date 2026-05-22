from flask import Flask, send_from_directory, jsonify, request, Response, send_file
from flask_cors import CORS
import os
import uuid
import io
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile
import zipfile

# PDF processing libraries
try:
    from PyPDF2 import PdfReader, PdfWriter
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyPDF2 not installed. Install with: pip install PyPDF2")

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Store API keys
api_keys = {}
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

def build_cors_response():
    response = Response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return build_cors_response()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'pdf_support': PDF_SUPPORT,
        'message': 'Reyansh API is running!'
    })

@app.route('/api/generate-key', methods=['POST', 'OPTIONS'])
def generate_api_key():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    try:
        data = request.get_json() or {}
        machine_id = data.get('machine_id', str(uuid.uuid4()))
        api_key = f"reyansh_{uuid.uuid4().hex[:16]}"
        api_keys[api_key] = {
            'machine_id': machine_id,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        return jsonify({
            'success': True,
            'api_key': api_key,
            'machine_id': machine_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return False
    api_keys[api_key]['usage_count'] += 1
    return True

@app.route('/api/merge', methods=['POST', 'OPTIONS'])
def merge_pdfs():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    if not PDF_SUPPORT:
        return jsonify({'error': 'PDF processing library not installed. Please install PyPDF2'}), 500
    
    try:
        files = request.files.getlist('files[]')
        if len(files) < 2:
            return jsonify({'error': 'Please select at least 2 PDF files'}), 400
        
        # Create PDF writer
        merger = PdfWriter()
        
        for file in files:
            if file and file.filename.endswith('.pdf'):
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    merger.add_page(page)
        
        # Save merged PDF to bytes
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        
        # Return as file download
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/split', methods=['POST', 'OPTIONS'])
def split_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    if not PDF_SUPPORT:
        return jsonify({'error': 'PDF processing library not installed'}), 500
    
    try:
        file = request.files.get('file')
        ranges = request.form.get('ranges', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not ranges:
            return jsonify({'error': 'Please provide page ranges'}), 400
        
        pdf_reader = PdfReader(file)
        total_pages = len(pdf_reader.pages)
        
        # Parse page ranges (e.g., "1-3,5,7-9")
        page_indices = []
        for part in ranges.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                for p in range(start - 1, min(end, total_pages)):
                    if 0 <= p < total_pages:
                        page_indices.append(p)
            else:
                p = int(part) - 1
                if 0 <= p < total_pages:
                    page_indices.append(p)
        
        if not page_indices:
            return jsonify({'error': 'No valid pages found'}), 400
        
        # Create new PDF with selected pages
        writer = PdfWriter()
        for idx in page_indices:
            writer.add_page(pdf_reader.pages[idx])
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'split_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zip', methods=['POST', 'OPTIONS'])
def zip_files():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        files = request.files.getlist('files[]')
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                if file and file.filename:
                    zip_file.writestr(secure_filename(file.filename), file.read())
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/unlock', methods=['POST', 'OPTIONS'])
def unlock_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    if not PDF_SUPPORT:
        return jsonify({'error': 'PDF processing library not installed'}), 500
    
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Try to decrypt PDF
        pdf_reader = PdfReader(file)
        
        if pdf_reader.is_encrypted:
            try:
                pdf_reader.decrypt(password)
            except:
                return jsonify({'error': 'Wrong password or file cannot be decrypted'}), 400
        
        # Create unlocked PDF
        writer = PdfWriter()
        for page in pdf_reader.pages:
            writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'unlocked_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lock', methods=['POST', 'OPTIONS'])
def lock_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    if not PDF_SUPPORT:
        return jsonify({'error': 'PDF processing library not installed'}), 500
    
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Read original PDF
        pdf_reader = PdfReader(file)
        
        # Create encrypted PDF (Note: PyPDF2 encryption is basic)
        writer = PdfWriter()
        for page in pdf_reader.pages:
            writer.add_page(page)
        
        # Add encryption
        writer.encrypt(password)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'locked_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET', 'OPTIONS'])
def get_templates():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    base_url = request.host_url.rstrip('/')
    return jsonify({
        'merge': f'POST {base_url}/api/merge',
        'split': f'POST {base_url}/api/split',
        'zip': f'POST {base_url}/api/zip',
        'unlock': f'POST {base_url}/api/unlock',
        'lock': f'POST {base_url}/api/lock'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)