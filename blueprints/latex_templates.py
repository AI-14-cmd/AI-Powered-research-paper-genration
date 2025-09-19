from flask import Blueprint, request, jsonify
from services.latex_service import LaTeXService
from blueprints.paper_generator import papers_storage
from models.database import db

latex_bp = Blueprint('latex', __name__)
latex_service = LaTeXService()

@latex_bp.route('/templates', methods=['GET'])
def get_latex_templates():
    """Get available LaTeX templates"""
    return jsonify({
        'success': True,
        'templates': [
            {
                'id': 'article',
                'name': 'Standard Article',
                'description': 'Basic academic article template',
                'suitable_for': ['Research papers', 'Journal articles', 'Conference papers']
            },
            {
                'id': 'ieee',
                'name': 'IEEE Conference',
                'description': 'IEEE conference paper format',
                'suitable_for': ['IEEE conferences', 'Technical papers', 'Engineering research']
            },
            {
                'id': 'acm',
                'name': 'ACM Article',
                'description': 'ACM publication format',
                'suitable_for': ['ACM conferences', 'Computer science papers', 'Software research']
            },
            {
                'id': 'report',
                'name': 'Technical Report',
                'description': 'Detailed technical report format',
                'suitable_for': ['Technical reports', 'Research reports', 'Project documentation']
            }
        ]
    })

@latex_bp.route('/generate/<paper_id>/<template_type>', methods=['GET'])
def generate_latex_template(paper_id, template_type):
    """Generate LaTeX code for a specific paper and template"""
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Generate LaTeX based on template type
        if template_type == 'ieee':
            latex_content = latex_service.generate_ieee_template(paper_content)
        elif template_type == 'acm':
            latex_content = latex_service.generate_acm_template(paper_content)
        elif template_type in ['article', 'report']:
            latex_content = latex_service.generate_latex_document(paper_content, template_type)
        else:
            return jsonify({'error': 'Invalid template type'}), 400
        
        return jsonify({
            'success': True,
            'latex_content': latex_content,
            'template_type': template_type,
            'filename': f"paper_{paper_id}_{template_type}.tex"
        })
        
    except Exception as e:
        return jsonify({'error': f'LaTeX generation failed: {str(e)}'}), 500

@latex_bp.route('/preview/<paper_id>/<template_type>', methods=['GET'])
def preview_latex_template(paper_id, template_type):
    """Preview LaTeX template structure without full content"""
    try:
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Generate preview information
        preview_info = {
            'template_type': template_type,
            'document_class': latex_service.document_classes.get(template_type, 'article'),
            'sections_included': [],
            'packages_used': latex_service.packages,
            'estimated_pages': max(1, paper_content.get('metadata', {}).get('word_count', 1000) // 250)
        }
        
        # Check which sections will be included
        for section in ['abstract', 'introduction', 'literature_review', 'methodology', 'results', 'conclusion']:
            if section in paper_content:
                preview_info['sections_included'].append(section.replace('_', ' ').title())
        
        if paper_content.get('references'):
            preview_info['sections_included'].append('Bibliography')
        
        if paper_content.get('summary'):
            preview_info['sections_included'].append('Key Insights')
        
        return jsonify({
            'success': True,
            'preview': preview_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500

@latex_bp.route('/compile-info', methods=['GET'])
def get_compile_info():
    """Get information about compiling LaTeX documents"""
    return jsonify({
        'success': True,
        'compile_info': {
            'recommended_compiler': 'pdflatex',
            'alternative_compilers': ['xelatex', 'lualatex'],
            'required_packages': latex_service.packages,
            'compilation_steps': [
                '1. Run pdflatex on the .tex file',
                '2. If using citations, run bibtex',
                '3. Run pdflatex again (twice for cross-references)',
                '4. Check the generated PDF'
            ],
            'common_issues': [
                {
                    'issue': 'Missing packages',
                    'solution': 'Install required LaTeX packages using your TeX distribution'
                },
                {
                    'issue': 'Special characters not displaying',
                    'solution': 'Ensure UTF-8 encoding and proper font packages'
                },
                {
                    'issue': 'Bibliography not showing',
                    'solution': 'Run bibtex after first pdflatex compilation'
                }
            ]
        }
    })

@latex_bp.route('/custom-template', methods=['POST'])
def create_custom_template():
    """Create a custom LaTeX template based on user preferences"""
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        preferences = data.get('preferences', {})
        
        if not paper_id:
            return jsonify({'error': 'Paper ID is required'}), 400
        
        # Get paper from storage
        paper_content = papers_storage.get(paper_id)
        
        if not paper_content:
            paper_doc = db.get_paper(paper_id)
            if paper_doc:
                paper_content = paper_doc.get('content')
        
        if not paper_content:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Apply custom preferences
        template_type = preferences.get('document_class', 'article')
        include_toc = preferences.get('include_table_of_contents', False)
        font_size = preferences.get('font_size', '12pt')
        paper_size = preferences.get('paper_size', 'a4paper')
        
        # Generate custom LaTeX
        latex_content = latex_service.generate_latex_document(paper_content, template_type)
        
        # Apply customizations (basic implementation)
        if not include_toc:
            latex_content = latex_content.replace('\\tableofcontents\n\\newpage\n\n', '')
        
        return jsonify({
            'success': True,
            'latex_content': latex_content,
            'preferences_applied': preferences,
            'filename': f"custom_paper_{paper_id}.tex"
        })
        
    except Exception as e:
        return jsonify({'error': f'Custom template creation failed: {str(e)}'}), 500