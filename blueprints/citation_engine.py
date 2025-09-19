from flask import Blueprint, request, jsonify
from services.citation_service import CitationService

citation_bp = Blueprint('citations', __name__)
citation_service = CitationService()

@citation_bp.route('/search', methods=['POST'])
def search_citations():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 5)
        style = data.get('style', 'APA')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Fetch citations
        citations_data = citation_service.fetch_citations(query, limit)
        
        # Format citations
        formatted_citations = []
        for citation in citations_data:
            formatted = citation_service.format_citation(citation, style)
            formatted_citations.append({
                'raw_data': citation,
                'formatted': formatted,
                'style': style
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'citations': formatted_citations,
            'count': len(formatted_citations)
        })
        
    except Exception as e:
        return jsonify({'error': f'Citation search failed: {str(e)}'}), 500

@citation_bp.route('/format', methods=['POST'])
def format_citation():
    try:
        data = request.get_json()
        citation_data = data.get('citation')
        style = data.get('style', 'APA')
        
        if not citation_data:
            return jsonify({'error': 'Citation data is required'}), 400
        
        formatted = citation_service.format_citation(citation_data, style)
        
        return jsonify({
            'success': True,
            'formatted_citation': formatted,
            'style': style
        })
        
    except Exception as e:
        return jsonify({'error': f'Citation formatting failed: {str(e)}'}), 500

@citation_bp.route('/styles', methods=['GET'])
def get_citation_styles():
    return jsonify({
        'success': True,
        'styles': ['APA', 'MLA', 'IEEE'],
        'default': 'APA'
    })

@citation_bp.route('/validate', methods=['POST'])
def validate_citation():
    try:
        data = request.get_json()
        citation = data.get('citation', '')
        
        if not citation:
            return jsonify({'error': 'Citation text is required'}), 400
        
        # Basic validation checks
        validation_results = {
            'has_authors': bool(any(char.isupper() for char in citation)),
            'has_year': bool(any(char.isdigit() for char in citation)),
            'has_title': len(citation.split()) > 3,
            'proper_length': 20 <= len(citation) <= 500,
            'has_doi': 'doi' in citation.lower() or '10.' in citation
        }
        
        score = sum(validation_results.values()) / len(validation_results) * 100
        
        return jsonify({
            'success': True,
            'validation_score': round(score, 1),
            'checks': validation_results,
            'is_valid': score >= 60
        })
        
    except Exception as e:
        return jsonify({'error': f'Citation validation failed: {str(e)}'}), 500