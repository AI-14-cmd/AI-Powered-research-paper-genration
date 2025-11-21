from flask import Blueprint, request, jsonify
from services.ai_service import AIService
import uuid
from datetime import datetime

ai_paper_bp = Blueprint('ai_paper', __name__)
ai_service = AIService()

@ai_paper_bp.route('/generate-full-paper', methods=['POST'])
def generate_full_paper():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        paper_type = data.get('paper_type', 'research')
        length = data.get('length', 'medium')
        outline = data.get('outline', None)
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate full paper content
        paper_content = ai_service.generate_paper_content(topic, paper_type, length, outline)
        
        # Generate paper ID
        paper_id = str(uuid.uuid4())
        
        # Create paper object
        paper = {
            'paper_id': paper_id,
            'topic': topic,
            'paper_type': paper_type,
            'length': length,
            'content': paper_content,
            'generated_at': datetime.utcnow().isoformat(),
            'word_count': len(paper_content.split()) if paper_content else 0
        }
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': paper,
            'message': 'Full paper generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate paper: {str(e)}'}), 500

@ai_paper_bp.route('/generate-outline', methods=['POST'])
def generate_outline():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        paper_type = data.get('paper_type', 'research')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate outline
        outline = ai_service.generate_outline(topic, paper_type)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'paper_type': paper_type,
            'outline': outline
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate outline: {str(e)}'}), 500

@ai_paper_bp.route('/enhance-from-source', methods=['POST'])
def enhance_from_source():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        source_content = data.get('source_content', '').strip()
        paper_type = data.get('paper_type', 'research')
        
        if not topic or not source_content:
            return jsonify({'error': 'Topic and source content are required'}), 400
        
        # Generate enhanced paper
        enhanced_paper = ai_service.enhance_paper_from_source(topic, source_content, paper_type)
        
        # Generate paper ID
        paper_id = str(uuid.uuid4())
        
        # Create paper object
        paper = {
            'paper_id': paper_id,
            'topic': topic,
            'paper_type': paper_type,
            'content': enhanced_paper,
            'source_enhanced': True,
            'generated_at': datetime.utcnow().isoformat(),
            'word_count': len(enhanced_paper.split()) if enhanced_paper else 0
        }
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': paper,
            'message': 'Enhanced paper generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to enhance paper: {str(e)}'}), 500

@ai_paper_bp.route('/custom-generate', methods=['POST'])
def custom_generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        model_name = data.get('model', 'models/gemini-1.5-flash')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate content with custom prompt
        content = ai_service.generate_with_gemini(prompt, model_name)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'content': content,
            'model_used': model_name
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate content: {str(e)}'}), 500