import PyPDF2
import requests
from io import BytesIO
from typing import Dict, Optional
import os
import google.generativeai as genai

class PDFImportService:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key and self.gemini_api_key.strip():
            try:
                genai.configure(api_key=self.gemini_api_key.strip())
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Gemini initialization error: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
    
    def import_pdf_from_url(self, pdf_url: str) -> Dict:
        """Import PDF from academic database URL"""
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            pdf_content = self.extract_text_from_pdf(BytesIO(response.content))
            return self.analyze_imported_pdf(pdf_content, pdf_url)
            
        except Exception as e:
            return {'error': f'Failed to import PDF: {str(e)}'}
    
    def import_pdf_from_file(self, pdf_file) -> Dict:
        """Import PDF from uploaded file"""
        try:
            pdf_content = self.extract_text_from_pdf(pdf_file)
            return self.analyze_imported_pdf(pdf_content, 'uploaded_file')
            
        except Exception as e:
            return {'error': f'Failed to process PDF file: {str(e)}'}
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    def analyze_imported_pdf(self, content: str, source: str) -> Dict:
        """Analyze imported PDF content using Gemini"""
        
        if not content or len(content) < 100:
            return {'error': 'PDF content too short or empty'}
        
        # Extract sections using AI
        sections = self.extract_sections_with_ai(content)
        
        # Classify domain
        from services.domain_classifier import DomainClassifier
        domain_classifier = DomainClassifier()
        domain_info = domain_classifier.classify_domain(
            sections.get('abstract', content[:1000]), 
            sections.get('title', 'Imported Paper')
        )
        
        return {
            'success': True,
            'source': source,
            'title': sections.get('title', 'Imported Research Paper'),
            'abstract': sections.get('abstract', ''),
            'introduction': sections.get('introduction', ''),
            'conclusion': sections.get('conclusion', ''),
            'references': sections.get('references', []),
            'full_content': content[:5000],  # First 5000 chars
            'word_count': len(content.split()),
            'domain': domain_info['domain'],
            'domain_confidence': domain_info['confidence'],
            'metadata': {
                'imported_from': source,
                'content_length': len(content),
                'research_domain': domain_info['domain']
            }
        }
    
    def extract_sections_with_ai(self, content: str) -> Dict:
        """Extract paper sections using Gemini AI"""
        
        if not self.gemini_model:
            return self.extract_sections_basic(content)
        
        try:
            prompt = f"""
            Analyze this research paper and extract the following sections:
            
            Content: {content[:3000]}
            
            Extract and return:
            1. Title (exact title of the paper)
            2. Abstract (complete abstract section)
            3. Introduction (first few sentences of introduction)
            4. Conclusion (main conclusion points)
            5. References (list of key references)
            
            Format as:
            TITLE: [title here]
            ABSTRACT: [abstract here]
            INTRODUCTION: [introduction here]
            CONCLUSION: [conclusion here]
            REFERENCES: [references here]
            """
            
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                return self.parse_ai_sections(response.text)
                
        except Exception as e:
            print(f"AI section extraction error: {e}")
        
        return self.extract_sections_basic(content)
    
    def parse_ai_sections(self, ai_response: str) -> Dict:
        """Parse AI response into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if line.startswith('TITLE:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'title'
                current_content = [line.replace('TITLE:', '').strip()]
            elif line.startswith('ABSTRACT:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'abstract'
                current_content = [line.replace('ABSTRACT:', '').strip()]
            elif line.startswith('INTRODUCTION:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'introduction'
                current_content = [line.replace('INTRODUCTION:', '').strip()]
            elif line.startswith('CONCLUSION:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'conclusion'
                current_content = [line.replace('CONCLUSION:', '').strip()]
            elif line.startswith('REFERENCES:'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'references'
                current_content = [line.replace('REFERENCES:', '').strip()]
            elif current_section and line:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def extract_sections_basic(self, content: str) -> Dict:
        """Basic keyword-based section extraction"""
        sections = {}
        
        # Extract title (first meaningful line)
        lines = content.split('\n')
        for line in lines[:10]:
            if len(line.strip()) > 10 and not line.strip().lower().startswith(('abstract', 'introduction')):
                sections['title'] = line.strip()
                break
        
        # Extract abstract
        abstract_start = content.lower().find('abstract')
        if abstract_start != -1:
            abstract_end = content.lower().find('introduction', abstract_start)
            if abstract_end == -1:
                abstract_end = abstract_start + 1000
            sections['abstract'] = content[abstract_start:abstract_end].replace('abstract', '').strip()[:500]
        
        # Extract introduction
        intro_start = content.lower().find('introduction')
        if intro_start != -1:
            sections['introduction'] = content[intro_start:intro_start+500].replace('introduction', '').strip()
        
        # Extract conclusion
        conclusion_start = content.lower().find('conclusion')
        if conclusion_start != -1:
            sections['conclusion'] = content[conclusion_start:conclusion_start+500].replace('conclusion', '').strip()
        
        return sections