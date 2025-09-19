from flask import Blueprint, request, jsonify
from services.pdf_import_service import PDFImportService
from blueprints.paper_generator import papers_storage
import uuid
from datetime import datetime

pdf_import_bp = Blueprint('pdf_import', __name__)
pdf_import_service = PDFImportService()

@pdf_import_bp.route('/import-url', methods=['POST'])
def import_pdf_from_url():
    try:
        data = request.get_json()
        pdf_url = data.get('pdf_url', '').strip()
        
        if not pdf_url:
            return jsonify({'error': 'PDF URL is required'}), 400
        
        # Validate URL format
        if not pdf_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Import PDF
        result = pdf_import_service.import_pdf_from_url(pdf_url)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Generate unique ID and store
        paper_id = str(uuid.uuid4())
        papers_storage[paper_id] = result
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': result,
            'message': 'PDF imported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

@pdf_import_bp.route('/import-file', methods=['POST'])
def import_pdf_from_file():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be a PDF'}), 400
        
        # Import PDF
        result = pdf_import_service.import_pdf_from_file(pdf_file)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Generate unique ID and store
        paper_id = str(uuid.uuid4())
        papers_storage[paper_id] = result
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': result,
            'message': 'PDF file imported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'File import failed: {str(e)}'}), 500

@pdf_import_bp.route('/supported-sources', methods=['GET'])
def get_supported_sources():
    return jsonify({
        'success': True,
        'sources': [
            {
                'name': 'IEEE Xplore',
                'url_pattern': 'ieeexplore.ieee.org',
                'description': 'IEEE digital library papers'
            },
            {
                'name': 'Springer',
                'url_pattern': 'link.springer.com',
                'description': 'Springer academic papers'
            },
            {
                'name': 'ACM Digital Library',
                'url_pattern': 'dl.acm.org',
                'description': 'ACM research papers'
            },
            {
                'name': 'arXiv',
                'url_pattern': 'arxiv.org',
                'description': 'arXiv preprint papers'
            },
            {
                'name': 'Direct PDF URL',
                'url_pattern': '*.pdf',
                'description': 'Any direct PDF link'
            }
        ]
    })