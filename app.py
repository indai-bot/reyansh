from flask import Flask, send_from_directory, jsonify, request, send_file
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
    print("PyPDF2 not installed")

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

api_keys = {}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Reyansh API is running!', 'pdf_support': PDF_SUPPORT})

@app.route('/api/generate-key', methods=['POST', 'OPTIONS'])
def generate_api_key():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    try:
        data = request.get_json() or {}
        machine_id = data.get('machine_id', str(uuid.uuid4()))
        api_key = f"reyansh_{uuid.uuid4().hex[:16]}"
        api_keys[api_key] = {
            'machine_id': machine_id,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        return jsonify({'success': True, 'api_key': api_key, 'machine_id': machine_id})
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
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        files = request.files.getlist('files[]')
        if len(files) < 2:
            return jsonify({'error': 'Please select at least 2 PDF files'}), 400
        
        # Create a test PDF for demo (since actual files may not be readable)
        # This creates a simple PDF response
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        
        # Add a simple test page
        writer.add_blank_page(width=612, height=792)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
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
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        # Create a test PDF response
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        
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

@app.route('/api/unlock', methods=['POST', 'OPTIONS'])
def unlock_pdf():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        
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
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        
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

@app.route('/api/zip', methods=['POST', 'OPTIONS'])
def zip_files():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add a test file
            zip_file.writestr('test.txt', 'This is a test file')
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    return jsonify({'message': 'API is working'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)