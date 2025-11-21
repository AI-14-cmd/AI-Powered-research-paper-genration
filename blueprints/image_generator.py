from flask import Blueprint, request, jsonify

image_bp = Blueprint('image_generator', __name__)
# image_gen = ImageGenerator() # DISABLED FOR VERCEL DEPLOYMENT

@image_bp.route('/api/images/generate', methods=['POST'])
def generate_images():
    """Generate charts and images for research paper - DISABLED FOR Vercel Deployment"""
    return jsonify({
        'success': True,
        'charts': [],
        'count': 0
    })

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