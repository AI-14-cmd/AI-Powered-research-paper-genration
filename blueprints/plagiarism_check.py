from flask import Blueprint, request, jsonify
from services.plagiarism_service import PlagiarismService
from blueprints.paper_generator import papers_storage
from models.database import db

plagiarism_bp = Blueprint('plagiarism', __name__)
plagiarism_service = PlagiarismService()

@plagiarism_bp.route('/check', methods=['POST'])
def check_plagiarism():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required for plagiarism check'}), 400
        
        if len(text) < 50:
            return jsonify({'error': 'Text too short for meaningful plagiarism check (minimum 50 characters)'}), 400
        
        # Perform plagiarism check
        result = plagiarism_service.check_plagiarism(text)
        
        return jsonify({
            'success': True,
            'plagiarism_check': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Plagiarism check failed: {str(e)}'}), 500

@plagiarism_bp.route('/check-paper/<paper_id>', methods=['POST'])
def check_paper_plagiarism(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Combine all text sections
        text_sections = []
        for section, content in paper_content.items():
            if isinstance(content, str) and section not in ['metadata', 'citations_data', 'references']:
                text_sections.append(content)
        
        full_text = ' '.join(text_sections)
        
        if len(full_text) < 50:
            return jsonify({'error': 'Paper content too short for plagiarism check'}), 400
        
        # Perform plagiarism check
        result = plagiarism_service.check_plagiarism(full_text)
        
        # Store result in paper
        paper_content['plagiarism_check'] = result
        papers_storage[paper_id] = paper_content
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'plagiarism_check': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Paper plagiarism check failed: {str(e)}'}), 500

@plagiarism_bp.route('/batch-check', methods=['POST'])
def batch_plagiarism_check():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Array of texts is required'}), 400
        
        results = []
        for i, text in enumerate(texts):
            if isinstance(text, str) and len(text.strip()) >= 50:
                result = plagiarism_service.check_plagiarism(text.strip())
                results.append({
                    'index': i,
                    'text_preview': text[:100] + '...' if len(text) > 100 else text,
                    'plagiarism_check': result
                })
            else:
                results.append({
                    'index': i,
                    'error': 'Text too short or invalid format'
                })
        
        return jsonify({
            'success': True,
            'batch_results': results,
            'total_checked': len([r for r in results if 'plagiarism_check' in r])
        })
        
    except Exception as e:
        return jsonify({'error': f'Batch plagiarism check failed: {str(e)}'}), 500

@plagiarism_bp.route('/history/<paper_id>', methods=['GET'])
def get_plagiarism_history(paper_id):
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        plagiarism_data = paper_content.get('plagiarism_check')
        
        if not plagiarism_data:
            return jsonify({
                'success': True,
                'paper_id': paper_id,
                'has_check': False,
                'message': 'No plagiarism check performed yet'
            })
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'has_check': True,
            'plagiarism_check': plagiarism_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get plagiarism history: {str(e)}'}), 500

@plagiarism_bp.route('/settings', methods=['GET'])
def get_plagiarism_settings():
    return jsonify({
        'success': True,
        'settings': {
            'min_text_length': 50,
            'max_text_length': 10000,
            'supported_languages': ['en'],
            'check_types': ['similarity', 'paraphrasing', 'citation_issues'],
            'thresholds': {
                'low_risk': 10,
                'medium_risk': 20,
                'high_risk': 30
            }
        }
    })