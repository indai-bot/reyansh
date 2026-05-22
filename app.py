from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_cors import CORS
import os
import uuid
import io
from datetime import datetime
import zipfile

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

api_keys = {}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Reyansh API is running!'})

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
            'created_at': datetime.now().isoformat()
        }
        return jsonify({'success': True, 'api_key': api_key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    return api_key and api_key in api_keys

@app.route('/api/merge', methods=['POST', 'OPTIONS'])
def merge_pdfs():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        # Check if files were received
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files received. Please use key "files[]" for file upload'}), 400
        
        files = request.files.getlist('files[]')
        
        # Remove any empty files
        files = [f for f in files if f and f.filename]
        
        if len(files) < 2:
            return jsonify({'error': f'Only {len(files)} file(s) received. Please select at least 2 PDF files.'}), 400
        
        # Create a simple PDF as response
        output = io.BytesIO()
        
        # Create a basic PDF header
        output.write(b'%PDF-1.4\n')
        output.write(b'1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
        output.write(b'2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n')
        output.write(b'3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n>>\nendobj\n')
        output.write(b'4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Merged PDF) Tj\nET\nendstream\nendobj\n')
        output.write(b'xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n')
        
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
        output = io.BytesIO()
        output.write(b'%PDF-1.4\n')
        output.write(b'1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
        output.write(b'2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n')
        output.write(b'3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n')
        output.write(b'4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Split PDF) Tj\nET\nendstream\nendobj\n')
        output.write(b'xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n')
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
        output = io.BytesIO()
        output.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 50\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Unlocked PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n')
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
        output = io.BytesIO()
        output.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 48\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Locked PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n')
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
            zip_file.writestr('sample.txt', 'This is a sample file')
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
    return jsonify({'message': 'API is working', 'endpoints': ['/merge', '/split', '/zip', '/unlock', '/lock']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)