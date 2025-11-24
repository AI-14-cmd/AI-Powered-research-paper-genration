# 🎓 AI-Powered Research Paper Generator

A comprehensive Flask-based application that generates structured academic research papers with real citations, plagiarism checking, and professional PDF export capabilities.

## 🚀 Features

### Core Features
- **AI-Powered Paper Generation**: Creates structured academic papers using LLM technology
- **Real Citation Engine**: Fetches authentic citations from Semantic Scholar and CrossRef APIs
- **Multiple Citation Styles**: Supports APA, MLA, and IEEE formatting
- **Professional PDF Export**: Generates publication-ready PDF documents
- **Plagiarism Detection**: Built-in plagiarism checking with detailed reports

### Bonus Features
- **Multiple Research Levels**: Beginner, Intermediate, and Advanced paper complexity
- **Section Customization**: Choose which sections to include in your paper
- **Key Insights Summary**: Automatically generated bullet-point summaries
- **Responsive Web Interface**: Modern, mobile-friendly design
- **Database Storage**: MongoDB integration with in-memory fallback

## 🏗️ Architecture

### Modular Flask Blueprint Structure
```
├── app.py                 # Main Flask application
├── blueprints/           # Modular route handlers
│   ├── paper_generator.py    # Paper generation endpoints
│   ├── citation_engine.py    # Citation search and formatting
│   ├── pdf_export.py         # PDF generation and download
│   └── plagiarism_check.py   # Plagiarism detection
├── services/             # Business logic layer
│   ├── llm_service.py        # LLM integration and fallbacks
│   ├── citation_service.py   # Citation APIs and formatting
│   ├── plagiarism_service.py # Plagiarism checking logic
│   └── pdf_service.py        # PDF generation with ReportLab
├── models/               # Data layer
│   ├── database.py           # MongoDB connection and operations
│   └── paper_model.py        # Paper data models
├── templates/            # Frontend templates
└── static/              # CSS, JS, and assets
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (optional - has in-memory fallback)
- OpenAI API key (optional - has fallback content)

### Quick Start
1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd AI-research-paper-generator
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Application**
   - Open browser to `http://localhost:5000`
   - Start generating research papers!

## 📖 Usage Guide

### Generating a Research Paper
1. **Enter Topic**: Input your research topic (e.g., "AI in Healthcare")
2. **Configure Settings**:
   - Choose research level (Beginner/Intermediate/Advanced)
   - Select citation style (APA/MLA/IEEE)
   - Pick paper sections to include
3. **Generate**: Click "Generate Research Paper"
4. **Review**: View the structured paper with real citations
5. **Export**: Download as professional PDF

### API Endpoints

#### Paper Generation
```bash
POST /api/paper/generate
{
  "topic": "AI in Healthcare",
  "keywords": ["machine learning", "diagnosis"],
  "citation_style": "APA",
  "research_level": "intermediate",
  "sections": ["abstract", "introduction", "literature_review", "conclusion"]
}
```

#### Citation Search
```bash
POST /api/citations/search
{
  "query": "artificial intelligence healthcare",
  "limit": 5,
  "style": "APA"
}
```

#### Plagiarism Check
```bash
POST /api/plagiarism/check-paper/{paper_id}
```

#### PDF Export
```bash
GET /api/pdf/export/{paper_id}
```

## 🎯 Hackathon Strengths

### For TCS Judges
- **Enterprise-Ready Architecture**: Modular, scalable Flask blueprint design
- **Real Academic Integration**: Uses authentic research databases, not synthetic content
- **Reliability**: Works offline with intelligent fallback systems
- **Professional Output**: Generates properly formatted academic papers
- **Cost Efficiency**: No mandatory AI API dependencies

### Technical Highlights
- **Robust Error Handling**: Graceful fallbacks for all external dependencies
- **Database Flexibility**: MongoDB with in-memory backup for demo reliability
- **API-First Design**: RESTful endpoints for easy integration
- **Responsive Frontend**: Modern Bootstrap 5 interface
- **Production Ready**: Environment configuration and deployment ready

## 🔧 Configuration

### Environment Variables
```bash
# Required for full functionality
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/research_papers

# Optional API keys
SEMANTIC_SCHOLAR_API_KEY=your_key_here
COPYLEAKS_API_KEY=your_key_here
```

### Fallback Systems
- **No OpenAI/Gemini API**: Uses curated academic content templates
- **No MongoDB**: Automatic fallback to in-memory storage
- **No Citation APIs**: Uses pre-loaded academic references
- **No Plagiarism APIs**: Simulated checking for demo purposes

## 📊 Demo Script

### For Hackathon Presentation
1. **Problem Statement**: "Research paper writing is time-consuming and citation management is complex"
2. **Solution Demo**:
   - Enter topic: "Applications of AI in Healthcare"
   - Show real-time generation with progress indicators
   - Display structured paper with authentic citations
   - Demonstrate plagiarism checking
   - Export professional PDF
3. **Impact**: "Saves researchers hours of work while ensuring academic integrity"

### Sample Topics for Demo
- "AI in Healthcare"
- "Climate Change Solutions"
- "Blockchain in Finance"
- "Renewable Energy Technologies"

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t research-paper-generator .
docker run -p 5000:5000 research-paper-generator
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Hackathon Project

Built for TCS Hackathon 2024 - Demonstrating practical AI applications in academic research and productivity enhancement.

---

