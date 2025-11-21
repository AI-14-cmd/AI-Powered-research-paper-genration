from flask import Blueprint, request, jsonify, send_file
from services.pdf_service import PDFService
from services.latex_service import LaTeXService
from blueprints.paper_generator import papers_storage
from models.database import db
import os
import tempfile
from datetime import datetime

pdf_bp = Blueprint('pdf', __name__)
pdf_service = PDFService()
latex_service = LaTeXService()

@pdf_bp.route('/export', methods=['POST'])
def export_pdf():
    try:
        data = request.get_json()
        paper_data = data.get('paper')
        filename = data.get('filename', f'research_paper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        include_metadata = data.get('include_metadata', False)
        
        if not paper_data:
            return jsonify({'error': 'Paper data is required'}), 400
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        # Generate PDF with charts
        if include_metadata and 'plagiarism_check' in paper_data:
            pdf_buffer = pdf_service.create_with_metadata(paper_data, paper_data['plagiarism_check'])
            with open(temp_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
        else:
            pdf_buffer = pdf_service.generate_pdf(paper_data)
            with open(temp_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
        
        # Return file
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

@pdf_bp.route('/export/<paper_id>', methods=['GET'])
def export_paper_pdf(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Generate filename
        title = paper_content.get('title', 'Research Paper')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title[:50]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        # Generate PDF with charts
        pdf_buffer = pdf_service.generate_pdf(paper_content)
        with open(temp_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

@pdf_bp.route('/preview/<paper_id>', methods=['GET'])
def preview_pdf_info(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Calculate PDF info
        sections = []
        total_words = 0
        
        for section, content in paper_content.items():
            if isinstance(content, str) and section not in ['metadata', 'citations_data']:
                word_count = len(content.split())
                total_words += word_count
                sections.append({
                    'section': section.replace('_', ' ').title(),
                    'word_count': word_count,
                    'char_count': len(content)
                })
        
        # Estimate pages (roughly 250 words per page)
        estimated_pages = max(1, round(total_words / 250))
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'title': paper_content.get('title', 'Untitled'),
            'total_words': total_words,
            'estimated_pages': estimated_pages,
            'sections': sections,
            'references_count': len(paper_content.get('references', [])),
            'has_summary': bool(paper_content.get('summary')),
            'metadata': paper_content.get('metadata', {}),
            'citation_style': paper_content.get('metadata', {}).get('citation_style', 'APA')
        })
        
    except Exception as e:
        return jsonify({'error': f'PDF preview failed: {str(e)}'}), 500

@pdf_bp.route('/latex/<paper_id>', methods=['GET'])
def export_latex(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Generate LaTeX content
        latex_content = latex_service.generate_latex_document(paper_content)
        
        # Generate filename
        title = paper_content.get('title', 'Research Paper')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title[:50]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': f'LaTeX export failed: {str(e)}'}), 500

@pdf_bp.route('/download-files/<paper_id>', methods=['GET'])
def download_all_files(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Create ZIP file with all formats
        import zipfile
        from io import BytesIO
        
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add main paper as PDF
            pdf_buffer = pdf_service.generate_pdf(paper_content)
            zip_file.writestr('research_paper.pdf', pdf_buffer.getvalue())
            
            # Add LaTeX file
            latex_content = latex_service.generate_latex_document(paper_content)
            zip_file.writestr('research_paper.tex', latex_content)
            
            # Add additional files if available
            if 'additional_files' in paper_content:
                files = paper_content['additional_files']
                
                if 'bibliography' in files:
                    zip_file.writestr('bibliography.md', files['bibliography'])
                
                if 'research_notes' in files:
                    zip_file.writestr('research_notes.md', files['research_notes'])
                
                if 'abstract_only' in files:
                    zip_file.writestr('abstract.txt', files['abstract_only'])
                
                # Add real papers list
                if 'real_papers' in paper_content:
                    import json
                    papers_json = json.dumps(paper_content['real_papers'], indent=2)
                    zip_file.writestr('real_papers.json', papers_json)
        
        zip_buffer.seek(0)
        
        # Generate filename
        title = paper_content.get('title', 'Research Paper')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title[:30]}_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        return send_file(
            BytesIO(zip_buffer.getvalue()),
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'File download failed: {str(e)}'}), 500

@pdf_bp.route('/formats', methods=['GET'])
def get_export_formats():
    return jsonify({
        'success': True,
        'formats': [
            {
                'name': 'PDF',
                'extension': '.pdf',
                'mime_type': 'application/pdf',
                'description': 'Portable Document Format - Best for sharing and printing'
            },
            {
                'name': 'LaTeX',
                'extension': '.tex',
                'mime_type': 'text/plain',
                'description': 'LaTeX source code - Best for academic publishing'
            },
            {
                'name': 'Complete Package',
                'extension': '.zip',
                'mime_type': 'application/zip',
                'description': 'All files including real papers, notes, and bibliography'
            }
        ],
        'default': 'PDF'
    })