# Reyansh - File Processing Suite

A complete file processing web application with PDF merge, split, zip, lock/unlock capabilities.

## Features
- ✅ Merge multiple PDFs
- ✅ Split PDF with custom page ranges
- ✅ Zip files and folders
- ✅ Unlock password-protected PDFs
- ✅ Lock PDFs with encryption
- ✅ Machine ID based folder isolation
- ✅ API key generation & request templates

## Deploy on Render

1. Push this repository to GitHub
2. Go to [Render.com](https://render.com)
3. Create New Web Service
4. Connect your GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
6. Click Deploy

## Local Development

```bash
pip install -r requirements.txt
python app.py