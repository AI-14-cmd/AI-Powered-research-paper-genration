from flask import Flask, render_template
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Now import blueprints (after env vars are loaded)
from blueprints.paper_generator import paper_bp
from blueprints.citation_engine import citation_bp
from blueprints.pdf_export import pdf_bp
from blueprints.plagiarism_check import plagiarism_bp
from blueprints.research_trends import trends_bp
from blueprints.collaboration import collab_bp
from blueprints.ai_assistant import assistant_bp
from blueprints.latex_templates import latex_bp
from blueprints.pdf_import import pdf_import_bp
from blueprints.image_generator import image_bp
from blueprints.ai_paper_generator import ai_paper_bp
from models.database import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hackathon-secret-key-2024'
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/research_papers')

# Simple CORS headers for demo
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(paper_bp, url_prefix='/api/paper')
app.register_blueprint(citation_bp, url_prefix='/api/citations')
app.register_blueprint(pdf_bp, url_prefix='/api/pdf')
app.register_blueprint(plagiarism_bp, url_prefix='/api/plagiarism')
app.register_blueprint(trends_bp, url_prefix='/api/trends')
app.register_blueprint(collab_bp, url_prefix='/api/collaboration')
app.register_blueprint(assistant_bp, url_prefix='/api/assistant')
app.register_blueprint(latex_bp, url_prefix='/api/latex')
app.register_blueprint(pdf_import_bp, url_prefix='/api/import')
app.register_blueprint(image_bp)
app.register_blueprint(ai_paper_bp, url_prefix='/api/ai-paper')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)