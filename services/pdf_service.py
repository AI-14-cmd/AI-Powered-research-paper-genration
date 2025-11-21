from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from typing import Dict, List
import os
import base64
import tempfile

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        # IEEE-style custom styles
        self.styles.add(ParagraphStyle(
            name='IEEETitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Times-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='IEEEAuthors',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Times-Roman'
        ))
        
        self.styles.add(ParagraphStyle(
            name='IEEESection',
            parent=self.styles['Heading1'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=12,
            fontName='Times-Bold',
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='IEEEBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='IEEEReference',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            leftIndent=15,
            fontName='Times-Roman'
        ))
        
        self.styles.add(ParagraphStyle(
            name='IEEESubSection',
            parent=self.styles['Heading2'],
            fontSize=9,
            spaceAfter=4,
            spaceBefore=8,
            fontName='Times-Bold',
            alignment=TA_LEFT
        ))
    
    def generate_pdf(self, paper_data: Dict, filename: str = None) -> BytesIO:
        buffer = BytesIO()
        
        if filename:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
        
        story = []
        
        # IEEE Paper Title (Centered, Bold, Times New Roman, 24pt)
        if 'title' in paper_data:
            story.append(Paragraph(paper_data['title'], self.styles['IEEETitle']))
        
        # Authors & Affiliations
        authors_text = "John Smith¹, Jane Doe², Michael Johnson¹<br/>"
        authors_text += "¹Department of Computer Science, University of Technology<br/>"
        authors_text += "²Institute of Advanced Research, Tech University<br/>"
        authors_text += "john.smith@university.edu, jane.doe@techuni.edu, michael.johnson@university.edu"
        story.append(Paragraph(authors_text, self.styles['IEEEAuthors']))
        story.append(Spacer(1, 20))
        
        # Abstract (No section number for abstract)
        if 'abstract' in paper_data:
            story.append(Paragraph("<b>Abstract</b>—" + paper_data['abstract'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # 3. Index Terms / Keywords
        story.append(Paragraph("3. Index Terms / Keywords", self.styles['IEEESection']))
        keywords = paper_data.get('metadata', {}).get('keywords', ['artificial intelligence', 'machine learning', 'research methodology'])
        if isinstance(keywords, list):
            keywords_text = ', '.join(keywords)
        else:
            keywords_text = str(keywords)
        story.append(Paragraph(f"<i>{keywords_text}</i>", self.styles['IEEEBody']))
        story.append(Spacer(1, 15))
        
        # 4. Abbreviations / Acronyms
        story.append(Paragraph("4. Abbreviations / Acronyms", self.styles['IEEESection']))
        abbreviations = self._extract_abbreviations(paper_data)
        if abbreviations:
            for abbr, expansion in abbreviations.items():
                story.append(Paragraph(f"<b>{abbr}:</b> {expansion}", self.styles['IEEEBody']))
        else:
            story.append(Paragraph("[No abbreviations found in text]", self.styles['IEEEBody']))
        story.append(Spacer(1, 15))
        
        # I. INTRODUCTION
        if 'introduction' in paper_data:
            story.append(Paragraph("I. INTRODUCTION", self.styles['IEEESection']))
            story.append(Paragraph(paper_data['introduction'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # 6. Research Questions / Objectives
        story.append(Paragraph("6. Research Questions / Objectives", self.styles['IEEESection']))
        objectives = self._extract_objectives(paper_data)
        for obj in objectives:
            story.append(Paragraph(f"• {obj}", self.styles['IEEEBody']))
        story.append(Spacer(1, 15))
        
        # 7. Sections & Subsections
        story.append(Paragraph("7. Sections & Subsections", self.styles['IEEESection']))
        
        # II. RELATED WORK
        if 'literature_review' in paper_data:
            story.append(Paragraph("II. RELATED WORK", self.styles['IEEESection']))
            story.append(Paragraph(paper_data['literature_review'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # III. METHODOLOGY
        if 'methodology' in paper_data:
            story.append(Paragraph("III. METHODOLOGY", self.styles['IEEESection']))
            story.append(Paragraph(paper_data['methodology'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # IV. RESULTS
        if 'results' in paper_data:
            story.append(Paragraph("IV. RESULTS", self.styles['IEEESection']))
            story.append(Paragraph(paper_data['results'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # Add Charts and Figures
        if 'charts' in paper_data and paper_data['charts']:
            story.append(Paragraph("7.4 Figures and Analysis", self.styles['IEEESubSection']))
            for i, chart in enumerate(paper_data['charts'], 1):
                # Add chart image
                chart_img = self._add_chart_to_pdf(chart['image'])
                if chart_img:
                    story.append(chart_img)
                    story.append(Spacer(1, 10))
                else:
                    story.append(Paragraph("[Figure not provided]", self.styles['IEEEReference']))
                
                # Add caption in IEEE format
                caption_text = f"Fig. {i}. {chart.get('caption', chart.get('title', 'Research Chart'))}"
                story.append(Paragraph(caption_text, self.styles['IEEEReference']))
                story.append(Spacer(1, 15))
        
        # V. CONCLUSION
        if 'conclusion' in paper_data:
            story.append(Paragraph("V. CONCLUSION", self.styles['IEEESection']))
            story.append(Paragraph(paper_data['conclusion'], self.styles['IEEEBody']))
            story.append(Spacer(1, 12))
        
        # REFERENCES
        story.append(Paragraph("REFERENCES", self.styles['IEEESection']))
        
        # References list in IEEE format
        if 'references' in paper_data and paper_data['references']:
            for i, ref in enumerate(paper_data['references'], 1):
                formatted_ref = f"[{i}] {ref}"
                story.append(Paragraph(formatted_ref, self.styles['IEEEReference']))
        else:
            # Sample IEEE references
            sample_refs = [
                "[1] J. Smith and A. Johnson, \"Machine Learning Applications in Healthcare,\" IEEE Trans. Biomed. Eng., vol. 68, no. 3, pp. 123-135, Mar. 2021.",
                "[2] M. Brown et al., \"Deep Learning for Medical Diagnosis,\" in Proc. IEEE Conf. Computer Vision, 2022, pp. 45-52."
            ]
            for ref in sample_refs:
                story.append(Paragraph(ref, self.styles['IEEEReference']))
        
        # Build PDF
        doc.build(story)
        
        if filename:
            return filename
        else:
            buffer.seek(0)
            return buffer
    
    def create_with_metadata(self, paper_data: Dict, metadata: Dict = None) -> BytesIO:
        """Create PDF with additional metadata like plagiarism score"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Add metadata header if provided
        if metadata:
            story.append(Paragraph("Document Information", self.styles['IEEESection']))
            if 'plagiarism_score' in metadata:
                score_color = metadata.get('color', 'black')
                story.append(Paragraph(
                    f"Plagiarism Score: {metadata['plagiarism_score']}% ({metadata.get('status', 'Unknown')})",
                    self.styles['IEEEBody']
                ))
            if 'word_count' in metadata:
                story.append(Paragraph(f"Word Count: {metadata['word_count']}", self.styles['IEEEBody']))
            story.append(Spacer(1, 20))
        
        # Generate main content
        main_buffer = self.generate_pdf(paper_data)
        
        # For simplicity, return the main PDF
        # In production, you might want to merge PDFs or add headers/footers
        return self.generate_pdf(paper_data)
    
    def _get_title_style(self, citation_style: str):
        """Get title formatting based on citation style"""
        if citation_style.upper() == 'APA':
            return self.styles['PaperTitle']  # Centered, bold
        elif citation_style.upper() == 'MLA':
            # MLA: Left-aligned, no bold
            return ParagraphStyle(
                name='MLATitle',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_LEFT,
                fontName='Helvetica'
            )
        elif citation_style.upper() == 'IEEE':
            return self.styles['PaperTitle']  # Centered, bold
        return self.styles['PaperTitle']
    
    def _get_reference_header(self, citation_style: str) -> str:
        """Get reference section header based on citation style"""
        if citation_style.upper() == 'APA':
            return "References"
        elif citation_style.upper() == 'MLA':
            return "Works Cited"
        elif citation_style.upper() == 'IEEE':
            return "References"
        return "References"
    
    def _format_reference_by_style(self, reference: str, index: int, citation_style: str) -> str:
        """Format reference according to citation style"""
        if citation_style.upper() == 'APA':
            # APA: No numbers, hanging indent
            return reference
        elif citation_style.upper() == 'MLA':
            # MLA: No numbers, hanging indent
            return reference
        elif citation_style.upper() == 'IEEE':
            # IEEE: Numbered in brackets
            return f"[{index}] {reference}"
        return f"[{index}] {reference}"
    
    def _add_chart_to_pdf(self, base64_image: str) -> Image:
        """Convert base64 image to ReportLab Image object"""
        try:
            # Remove data URL prefix if present
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            
            # Use BytesIO instead of temporary file
            image_buffer = BytesIO(image_data)
            
            # Create ReportLab Image from BytesIO
            img = Image(image_buffer, width=5*inch, height=3*inch)
            
            return img
        except Exception as e:
            print(f"Error adding chart to PDF: {e}")
            return None
    
    def _extract_abbreviations(self, paper_data: Dict) -> Dict[str, str]:
        """Extract abbreviations from paper text"""
        abbreviations = {
            'AI': 'Artificial Intelligence',
            'ML': 'Machine Learning',
            'DL': 'Deep Learning',
            'CNN': 'Convolutional Neural Network',
            'RNN': 'Recurrent Neural Network',
            'IoT': 'Internet of Things',
            'API': 'Application Programming Interface',
            'GPU': 'Graphics Processing Unit',
            'CPU': 'Central Processing Unit',
            'NLP': 'Natural Language Processing'
        }
        
        # Extract text from all sections
        full_text = ''
        for section in ['abstract', 'introduction', 'literature_review', 'methodology', 'results', 'conclusion']:
            if section in paper_data:
                full_text += paper_data[section] + ' '
        
        # Find abbreviations that appear in the text
        found_abbreviations = {}
        for abbr, expansion in abbreviations.items():
            if abbr in full_text:
                found_abbreviations[abbr] = expansion
        
        return found_abbreviations
    
    def _extract_objectives(self, paper_data: Dict) -> List[str]:
        """Extract research objectives from paper content"""
        objectives = [
            'Analyze current methodologies and identify research gaps',
            'Develop enhanced frameworks for improved performance',
            'Conduct empirical validation through comprehensive testing',
            'Provide practical solutions for real-world implementation',
            'Establish foundation for future research directions'
        ]
        
        # Try to extract from introduction if available
        if 'introduction' in paper_data:
            intro_text = paper_data['introduction'].lower()
            if 'objective' in intro_text or 'aim' in intro_text:
                # Custom objectives based on content
                topic = paper_data.get('title', '').lower()
                if 'ai' in topic or 'artificial intelligence' in topic:
                    objectives = [
                        'Investigate AI applications in the specified domain',
                        'Evaluate performance metrics of AI-based solutions',
                        'Compare traditional methods with AI approaches',
                        'Assess practical implementation challenges'
                    ]
        
        return objectives