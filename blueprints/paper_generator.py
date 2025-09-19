from flask import Blueprint, request, jsonify
from services.llm_service import LLMService
from services.citation_service import CitationService
from models.database import db
import uuid
from datetime import datetime

paper_bp = Blueprint('paper', __name__)
llm_service = LLMService()
citation_service = CitationService()

# In-memory storage for demo reliability
papers_storage = {}

@paper_bp.route('/generate', methods=['POST'])
def generate_paper():
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        keywords = data.get('keywords', [])
        citation_style = data.get('citation_style', 'APA')
        research_level = data.get('research_level', 'intermediate')
        research_field = data.get('research_field', 'Computer Science')
        sections = data.get('sections', ['abstract', 'introduction', 'literature_review', 'conclusion'])
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate paper sections
        paper_content = {}
        
        # Generate title
        paper_content['title'] = llm_service.generate_section(topic, 'title', research_level)
        
        # Generate title first
        paper_content['title'] = llm_service.generate_section(topic, 'title', research_level, keywords, research_field)
        
        # Generate selected sections with full context
        for section in sections:
            if section in ['abstract', 'introduction', 'literature_review', 'conclusion', 'methodology', 'results']:
                paper_content[section] = llm_service.generate_section(topic, section, research_level, keywords, research_field)
        
        # Quick citations (reduced from 5 to 3)
        citations_data = citation_service.fetch_citations(topic, limit=3)
        formatted_citations = [
            citation_service.format_citation(citation, citation_style) 
            for citation in citations_data
        ]
        paper_content['references'] = formatted_citations
        
        # Auto-find real PDFs from academic databases
        from services.auto_pdf_finder import AutoPDFFinder
        pdf_finder = AutoPDFFinder()
        real_papers = pdf_finder.find_real_pdfs(topic, keywords)
        paper_content['real_papers'] = real_papers
        
        # Generate research charts and images
        from services.image_generator import ImageGenerator
        image_gen = ImageGenerator()
        charts = image_gen.generate_research_charts(topic, paper_content)
        paper_content['charts'] = charts
        
        # Quick summary
        paper_content['summary'] = [
            f"Comprehensive analysis of {topic}",
            "Review of current methodologies and approaches", 
            "Identification of key challenges and opportunities",
            "Evidence-based findings and recommendations"
        ]
        
        # Classify research domain
        from services.domain_classifier import DomainClassifier
        domain_classifier = DomainClassifier()
        
        abstract_text = paper_content.get('abstract', '')
        title_text = paper_content.get('title', '')
        domain_info = domain_classifier.classify_domain(abstract_text, title_text)
        
        # Add metadata
        paper_content['metadata'] = {
            'topic': topic,
            'keywords': keywords,
            'citation_style': citation_style,
            'research_level': research_level,
            'sections': sections,
            'generated_at': datetime.utcnow().isoformat(),
            'word_count': sum(len(content.split()) for content in paper_content.values() if isinstance(content, str)),
            'real_papers_count': len(real_papers),
            'research_domain': domain_info['domain'],
            'domain_confidence': domain_info['confidence']
        }
        
        # Generate unique ID
        paper_id = str(uuid.uuid4())
        
        # Save to database (with fallback to memory)
        db_id = db.save_paper({
            'paper_id': paper_id,
            'content': paper_content
        })
        
        # Always save to memory as backup
        papers_storage[paper_id] = paper_content
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': paper_content,
            'message': 'Paper generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate paper: {str(e)}'}), 500

@paper_bp.route('/preview/<paper_id>', methods=['GET'])
def preview_paper(paper_id):
    try:
        # Try memory first, then database
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'paper': paper_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve paper: {str(e)}'}), 500

@paper_bp.route('/list', methods=['GET'])
def list_papers():
    try:
        # Return papers from memory storage
        papers_list = []
        for paper_id, content in papers_storage.items():
            papers_list.append({
                'paper_id': paper_id,
                'title': content.get('title', 'Untitled'),
                'topic': content.get('metadata', {}).get('topic', 'Unknown'),
                'generated_at': content.get('metadata', {}).get('generated_at', ''),
                'word_count': content.get('metadata', {}).get('word_count', 0)
            })
        
        return jsonify({
            'success': True,
            'papers': papers_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list papers: {str(e)}'}), 500

@paper_bp.route('/delete/<paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    try:
        # Remove from memory
        if paper_id in papers_storage:
            del papers_storage[paper_id]
        
        # Try to remove from database
        if db.db:
            try:
                from bson import ObjectId
                db.db.papers.delete_one({'paper_id': paper_id})
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': 'Paper deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete paper: {str(e)}'}), 500