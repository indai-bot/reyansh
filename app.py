from flask import Flask, send_from_directory, jsonify, request, Response
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
import io

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Store API keys (in production, use database)
api_keys = {}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return build_cors_response()
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'message': 'Reyansh API is running!'})

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
            'machine_id': machine_id,
            'message': 'API Key generated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/validate-key', methods=['POST', 'OPTIONS'])
def validate_api_key():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    api_key = request.headers.get('X-API-Key')
    if api_key and api_key in api_keys:
        api_keys[api_key]['usage_count'] += 1
        return jsonify({'valid': True, 'usage_count': api_keys[api_key]['usage_count']})
    return jsonify({'valid': False}), 401

@app.route('/api/templates', methods=['GET', 'OPTIONS'])
def get_templates():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    base_url = request.host_url.rstrip('/')
    templates = {
        'merge': f'''curl -X POST {base_url}/api/merge \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "files[]=@document1.pdf" \\
  -F "files[]=@document2.pdf"''',
        'split': f'''curl -X POST {base_url}/api/split \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@document.pdf" \\
  -F "ranges=1-3,5,7-9"''',
        'zip': f'''curl -X POST {base_url}/api/zip \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "files[]=@file1.txt" \\
  -F "files[]=@file2.jpg"''',
        'unlock': f'''curl -X POST {base_url}/api/unlock \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@secured.pdf" \\
  -F "password=mypassword"''',
        'lock': f'''curl -X POST {base_url}/api/lock \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@document.pdf" \\
  -F "password=newpassword"'''
    }
    return jsonify(templates)

@app.route('/api/merge', methods=['POST', 'OPTIONS'])
def merge_pdfs():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Validate API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        files = request.files.getlist('files[]')
        if len(files) < 2:
            return jsonify({'error': 'Please select at least 2 PDF files'}), 400
        
        # Here you would implement actual PDF merging
        # For now, return success message
        return jsonify({
            'success': True,
            'message': f'Merge request received for {len(files)} files',
            'files': [f.filename for f in files]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/split', methods=['POST', 'OPTIONS'])
def split_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Validate API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        file = request.files.get('file')
        ranges = request.form.get('ranges', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not ranges:
            return jsonify({'error': 'Please provide page ranges'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Split request received for {file.filename} with ranges: {ranges}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zip', methods=['POST', 'OPTIONS'])
def zip_files():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Validate API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        files = request.files.getlist('files[]')
        return jsonify({
            'success': True,
            'message': f'Zip request received for {len(files)} files'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/unlock', methods=['POST', 'OPTIONS'])
def unlock_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Validate API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Unlock request received for {file.filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lock', methods=['POST', 'OPTIONS'])
def lock_pdf():
    if request.method == 'OPTIONS':
        return build_cors_response()
    
    # Validate API key
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    try:
        file = request.files.get('file')
        password = request.form.get('password', '')
        
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Lock request received for {file.filename} with password'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def build_cors_response():
    """Build CORS response for OPTIONS requests"""
    response = Response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)