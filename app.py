from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Store API keys in memory (for demo; use Redis/DB in production)
api_keys = {}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-key', methods=['POST'])
def generate_api_key():
    machine_id = request.json.get('machine_id', str(uuid.uuid4()))
    api_key = f"reyansh_{uuid.uuid4().hex[:16]}"
    api_keys[api_key] = {
        'machine_id': machine_id,
        'created_at': datetime.now().isoformat(),
        'usage_count': 0
    }
    return jsonify({'api_key': api_key, 'machine_id': machine_id})

@app.route('/api/validate-key', methods=['POST'])
def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key and api_key in api_keys:
        api_keys[api_key]['usage_count'] += 1
        return jsonify({'valid': True, 'usage_count': api_keys[api_key]['usage_count']})
    return jsonify({'valid': False}), 401

@app.route('/api/templates', methods=['GET'])
def get_templates():
    base_url = request.host_url.rstrip('/')
    templates = {
        'merge': f'''curl -X POST {base_url}/api/merge \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "files[]=@document1.pdf" \\
  -F "files[]=@document2.pdf"''',
        'split': f'''curl -X POST {base_url}/api/split \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -F "file=@document.pdf" \\
  -F "ranges=1-3,5"''',
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)