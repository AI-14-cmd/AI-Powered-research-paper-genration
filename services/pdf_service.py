from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from typing import Dict, List
import os

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        # Custom styles for academic papers
        self.styles.add(ParagraphStyle(
            name='PaperTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='PaperBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Citation',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, paper_data: Dict, filename: str = None) -> BytesIO:
        buffer = BytesIO()
        citation_style = paper_data.get('metadata', {}).get('citation_style', 'APA')
        
        if filename:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
        
        story = []
        
        # Add citation style header
        story.append(Paragraph(f"Formatted in {citation_style} Style", self.styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Title formatting based on citation style
        if 'title' in paper_data:
            title_style = self._get_title_style(citation_style)
            title = Paragraph(paper_data['title'], title_style)
            story.append(title)
            story.append(Spacer(1, 20))
        
        # Abstract
        if 'abstract' in paper_data:
            story.append(Paragraph("Abstract", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['abstract'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Introduction
        if 'introduction' in paper_data:
            story.append(Paragraph("1. Introduction", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['introduction'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Literature Review
        if 'literature_review' in paper_data:
            story.append(Paragraph("2. Literature Review", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['literature_review'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Methodology (if present)
        if 'methodology' in paper_data:
            story.append(Paragraph("3. Methodology", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['methodology'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Results (if present)
        if 'results' in paper_data:
            story.append(Paragraph("4. Results", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['results'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Conclusion
        if 'conclusion' in paper_data:
            story.append(Paragraph("5. Conclusion", self.styles['SectionHeader']))
            story.append(Paragraph(paper_data['conclusion'], self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # Summary (if present)
        if 'summary' in paper_data and paper_data['summary']:
            story.append(Paragraph("Key Insights", self.styles['SectionHeader']))
            for point in paper_data['summary']:
                story.append(Paragraph(f"• {point}", self.styles['PaperBody']))
            story.append(Spacer(1, 15))
        
        # References formatted by citation style
        if 'references' in paper_data and paper_data['references']:
            ref_header = self._get_reference_header(citation_style)
            story.append(Paragraph(ref_header, self.styles['SectionHeader']))
            
            for i, ref in enumerate(paper_data['references'], 1):
                formatted_ref = self._format_reference_by_style(ref, i, citation_style)
                story.append(Paragraph(formatted_ref, self.styles['Citation']))
        
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
            story.append(Paragraph("Document Information", self.styles['SectionHeader']))
            if 'plagiarism_score' in metadata:
                score_color = metadata.get('color', 'black')
                story.append(Paragraph(
                    f"Plagiarism Score: {metadata['plagiarism_score']}% ({metadata.get('status', 'Unknown')})",
                    self.styles['PaperBody']
                ))
            if 'word_count' in metadata:
                story.append(Paragraph(f"Word Count: {metadata['word_count']}", self.styles['PaperBody']))
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