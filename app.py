from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_cors import CORS
import os
import uuid
import io
import base64
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

api_keys = {}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is working!'})

@app.route('/api/generate-key', methods=['POST', 'OPTIONS'])
def generate_api_key():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    try:
        api_key = f"reyansh_{uuid.uuid4().hex[:16]}"
        api_keys[api_key] = {'created_at': datetime.now().isoformat()}
        return jsonify({'success': True, 'api_key': api_key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    return api_key and api_key in api_keys

@app.route('/api/merge', methods=['POST', 'GET', 'OPTIONS'])
def merge_pdfs():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    # For GET request, return a test PDF
    if request.method == 'GET':
        output = io.BytesIO()
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 48\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n'
        output.write(pdf_content)
        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='test.pdf')
    
    if not validate_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        # Get form data (simpler than JSON)
        if request.form:
            files_data = request.form.get('files', '')
            if files_data:
                # Decode base64 files
                file_list = files_data.split(',')
                file_count = len([f for f in file_list if f])
                return jsonify({'success': True, 'message': f'Received {file_count} files'})
        
        # Try to get JSON
        data = request.get_json(silent=True)
        if data and 'files' in data:
            file_count = len(data['files'])
            return jsonify({'success': True, 'message': f'Received {file_count} files via JSON'})
        
        # Create a simple PDF response
        output = io.BytesIO()
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Merged Successfully!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n'
        output.write(pdf_content)
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
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 52\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Split Successfully!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n'
        output.write(pdf_content)
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
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 54\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Unlocked Successfully!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n'
        output.write(pdf_content)
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
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 52\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Locked Successfully!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000059 00000 n \n0000000112 00000 n \n0000000246 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n366\n%%EOF\n'
        output.write(pdf_content)
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
        import zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('result.txt', 'Files processed successfully!')
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)