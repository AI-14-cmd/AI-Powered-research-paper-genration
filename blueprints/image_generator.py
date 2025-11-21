from flask import Blueprint, request, jsonify
from services.image_generator import ImageGenerator

image_bp = Blueprint('image_generator', __name__)
image_gen = ImageGenerator()

@image_bp.route('/api/images/generate', methods=['POST'])
def generate_images():
    """Generate charts and images for research paper"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        paper_content = data.get('paper_content', {})
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        charts = image_gen.generate_research_charts(topic, paper_content)
        
        return jsonify({
            'success': True,
            'charts': charts,
            'count': len(charts)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@image_bp.route('/api/images/chart-types', methods=['GET'])
def get_chart_types():
    """Get available chart types based on topic"""
    topic = request.args.get('topic', '').lower()
    
    if 'fmri' in topic or 'brain' in topic:
        chart_types = ['Brain Activation Heatmap', 'Method Comparison']
    elif 'ai' in topic or 'machine learning' in topic:
        chart_types = ['Training Progress']
    else:
        chart_types = ['Performance Analysis', 'Research Trends']
    
    return jsonify({'chart_types': chart_types})