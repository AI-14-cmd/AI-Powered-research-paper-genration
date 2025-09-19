from flask import Blueprint, request, jsonify
import random
from datetime import datetime, timedelta

trends_bp = Blueprint('trends', __name__)

class ResearchTrendsService:
    def __init__(self):
        self.trending_topics = {
            'Computer Science': ['Explainable AI', 'Edge Computing', 'Quantum ML', 'AI Ethics'],
            'Healthcare': ['Precision Medicine', 'Digital Health', 'AI Diagnostics', 'Telemedicine'],
            'Business': ['Digital Transformation', 'ESG Investing', 'Remote Work', 'Crypto Finance'],
            'Engineering': ['Green Energy', 'Smart Materials', 'IoT Systems', 'Autonomous Vehicles']
        }
        
        self.paper_templates = {
            'AI/ML': {
                'sections': ['abstract', 'introduction', 'methodology', 'results', 'conclusion'],
                'keywords': ['machine learning', 'neural networks', 'deep learning', 'algorithms']
            },
            'Healthcare': {
                'sections': ['abstract', 'introduction', 'literature_review', 'methodology', 'results', 'discussion', 'conclusion'],
                'keywords': ['clinical trial', 'patient outcomes', 'medical intervention', 'healthcare']
            },
            'Business': {
                'sections': ['abstract', 'introduction', 'literature_review', 'analysis', 'recommendations', 'conclusion'],
                'keywords': ['market analysis', 'business strategy', 'competitive advantage', 'ROI']
            }
        }

trends_service = ResearchTrendsService()

@trends_bp.route('/trending', methods=['GET'])
def get_trending_topics():
    field = request.args.get('field', 'Computer Science')
    
    topics = trends_service.trending_topics.get(field, trends_service.trending_topics['Computer Science'])
    
    # Add trend scores
    trending_data = []
    for topic in topics:
        trending_data.append({
            'topic': topic,
            'trend_score': random.randint(70, 95),
            'papers_count': random.randint(50, 500),
            'growth_rate': f"+{random.randint(10, 45)}%"
        })
    
    return jsonify({
        'success': True,
        'field': field,
        'trending_topics': trending_data,
        'last_updated': datetime.now().isoformat()
    })

@trends_bp.route('/templates', methods=['GET'])
def get_paper_templates():
    return jsonify({
        'success': True,
        'templates': trends_service.paper_templates
    })

@trends_bp.route('/suggestions', methods=['POST'])
def get_topic_suggestions():
    data = request.get_json()
    topic = data.get('topic', '').lower()
    
    suggestions = [
        f"Recent developments in {topic}",
        f"Challenges and opportunities in {topic}",
        f"Future directions for {topic} research",
        f"Comparative analysis of {topic} approaches",
        f"Impact of {topic} on industry applications"
    ]
    
    return jsonify({
        'success': True,
        'suggestions': suggestions[:3]
    })