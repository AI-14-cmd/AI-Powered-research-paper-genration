from flask import Blueprint, request, jsonify
from blueprints.paper_generator import papers_storage
import uuid
from datetime import datetime

collab_bp = Blueprint('collaboration', __name__)

# In-memory storage for collaboration features
shared_papers = {}
paper_versions = {}
paper_comments = {}

@collab_bp.route('/share/<paper_id>', methods=['POST'])
def share_paper(paper_id):
    try:
        if paper_id not in papers_storage:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Generate share link
        share_id = str(uuid.uuid4())
        shared_papers[share_id] = {
            'paper_id': paper_id,
            'created_at': datetime.utcnow().isoformat(),
            'access_count': 0,
            'permissions': 'read'  # read, comment, edit
        }
        
        share_url = f"/shared/{share_id}"
        
        return jsonify({
            'success': True,
            'share_id': share_id,
            'share_url': share_url,
            'expires_in': '7 days'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/shared/<share_id>', methods=['GET'])
def get_shared_paper(share_id):
    try:
        if share_id not in shared_papers:
            return jsonify({'error': 'Shared paper not found or expired'}), 404
        
        share_info = shared_papers[share_id]
        paper_id = share_info['paper_id']
        
        if paper_id not in papers_storage:
            return jsonify({'error': 'Original paper not found'}), 404
        
        # Increment access count
        shared_papers[share_id]['access_count'] += 1
        
        return jsonify({
            'success': True,
            'paper': papers_storage[paper_id],
            'share_info': share_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/versions/<paper_id>', methods=['GET'])
def get_paper_versions(paper_id):
    try:
        versions = paper_versions.get(paper_id, [])
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'versions': versions,
            'total_versions': len(versions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/versions/<paper_id>', methods=['POST'])
def save_paper_version(paper_id):
    try:
        if paper_id not in papers_storage:
            return jsonify({'error': 'Paper not found'}), 404
        
        data = request.get_json()
        version_note = data.get('note', 'Auto-saved version')
        
        if paper_id not in paper_versions:
            paper_versions[paper_id] = []
        
        version = {
            'version_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'note': version_note,
            'content': papers_storage[paper_id].copy(),
            'version_number': len(paper_versions[paper_id]) + 1
        }
        
        paper_versions[paper_id].append(version)
        
        return jsonify({
            'success': True,
            'version': version,
            'message': 'Version saved successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/comments/<paper_id>', methods=['GET'])
def get_paper_comments(paper_id):
    try:
        comments = paper_comments.get(paper_id, [])
        return jsonify({
            'success': True,
            'paper_id': paper_id,
            'comments': comments,
            'total_comments': len(comments)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/comments/<paper_id>', methods=['POST'])
def add_paper_comment(paper_id):
    try:
        if paper_id not in papers_storage:
            return jsonify({'error': 'Paper not found'}), 404
        
        data = request.get_json()
        comment_text = data.get('comment', '').strip()
        section = data.get('section', 'general')
        author = data.get('author', 'Anonymous')
        
        if not comment_text:
            return jsonify({'error': 'Comment text is required'}), 400
        
        if paper_id not in paper_comments:
            paper_comments[paper_id] = []
        
        comment = {
            'comment_id': str(uuid.uuid4()),
            'author': author,
            'comment': comment_text,
            'section': section,
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False
        }
        
        paper_comments[paper_id].append(comment)
        
        return jsonify({
            'success': True,
            'comment': comment,
            'message': 'Comment added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@collab_bp.route('/export-formats', methods=['GET'])
def get_export_formats():
    return jsonify({
        'success': True,
        'formats': [
            {
                'name': 'PDF',
                'extension': '.pdf',
                'description': 'Portable Document Format',
                'available': True
            },
            {
                'name': 'DOCX',
                'extension': '.docx',
                'description': 'Microsoft Word Document',
                'available': True
            },
            {
                'name': 'LaTeX',
                'extension': '.tex',
                'description': 'LaTeX Source Code',
                'available': True
            },
            {
                'name': 'Markdown',
                'extension': '.md',
                'description': 'Markdown Format',
                'available': True
            },
            {
                'name': 'HTML',
                'extension': '.html',
                'description': 'Web Page Format',
                'available': True
            }
        ]
    })

@collab_bp.route('/export/<paper_id>/<format_type>', methods=['GET'])
def export_paper_format(paper_id, format_type):
    try:
        if paper_id not in papers_storage:
            return jsonify({'error': 'Paper not found'}), 404
        
        paper = papers_storage[paper_id]
        
        if format_type.lower() == 'markdown':
            content = _convert_to_markdown(paper)
            return jsonify({
                'success': True,
                'content': content,
                'filename': f"paper_{paper_id}.md"
            })
        elif format_type.lower() == 'latex':
            content = _convert_to_latex(paper)
            return jsonify({
                'success': True,
                'content': content,
                'filename': f"paper_{paper_id}.tex"
            })
        elif format_type.lower() == 'html':
            content = _convert_to_html(paper)
            return jsonify({
                'success': True,
                'content': content,
                'filename': f"paper_{paper_id}.html"
            })
        elif format_type.lower() == 'docx':
            return jsonify({
                'success': True,
                'content': _convert_to_markdown(paper),
                'filename': f"paper_{paper_id}.docx"
            })
        else:
            return jsonify({'error': 'Format not supported'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _convert_to_markdown(paper):
    md_content = f"# {paper.get('title', 'Research Paper')}\n\n"
    
    if 'abstract' in paper:
        md_content += f"## Abstract\n\n{paper['abstract']}\n\n"
    
    if 'introduction' in paper:
        md_content += f"## Introduction\n\n{paper['introduction']}\n\n"
    
    if 'literature_review' in paper:
        md_content += f"## Literature Review\n\n{paper['literature_review']}\n\n"
    
    if 'conclusion' in paper:
        md_content += f"## Conclusion\n\n{paper['conclusion']}\n\n"
    
    if 'references' in paper:
        md_content += "## References\n\n"
        for i, ref in enumerate(paper['references'], 1):
            md_content += f"{i}. {ref}\n"
    
    return md_content

def _convert_to_latex(paper):
    from services.latex_service import LaTeXService
    latex_service = LaTeXService()
    return latex_service.generate_latex_document(paper, 'article')

def _convert_to_html(paper):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{paper.get('title', 'Research Paper')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #666; border-bottom: 2px solid #eee; }}
        .abstract {{ background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff; }}
    </style>
</head>
<body>
    <h1>{paper.get('title', 'Research Paper')}</h1>
"""
    
    if 'abstract' in paper:
        html_content += f'    <div class="abstract"><h2>Abstract</h2><p>{paper["abstract"]}</p></div>\n'
    
    if 'introduction' in paper:
        html_content += f'    <h2>Introduction</h2><p>{paper["introduction"]}</p>\n'
    
    if 'literature_review' in paper:
        html_content += f'    <h2>Literature Review</h2><p>{paper["literature_review"]}</p>\n'
    
    if 'conclusion' in paper:
        html_content += f'    <h2>Conclusion</h2><p>{paper["conclusion"]}</p>\n'
    
    if 'references' in paper:
        html_content += '    <h2>References</h2><ol>\n'
        for ref in paper['references']:
            html_content += f'        <li>{ref}</li>\n'
        html_content += '    </ol>\n'
    
    html_content += '</body></html>'
    return html_content