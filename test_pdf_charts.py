#!/usr/bin/env python3

from services.pdf_service import PDFService
from services.image_generator import ImageGenerator

def test_pdf_with_charts():
    print("Testing PDF generation with charts...")
    
    # Generate sample charts
    image_gen = ImageGenerator()
    charts = image_gen.generate_research_charts("AI in Healthcare", {})
    
    # Sample paper data with charts
    paper_data = {
        'title': 'AI Applications in Healthcare: A Comprehensive Study',
        'abstract': 'This study examines the applications of artificial intelligence in healthcare...',
        'introduction': 'Healthcare is being transformed by AI technologies...',
        'results': 'Our analysis shows significant improvements in diagnostic accuracy...',
        'conclusion': 'AI shows great promise for improving healthcare outcomes...',
        'charts': charts,
        'references': ['Smith, J. (2023). AI in Medicine. Journal of Healthcare.']
    }
    
    # Generate PDF
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_pdf(paper_data)
    
    # Save to file for testing
    with open('test_paper_with_charts.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print(f"OK PDF generated with {len(charts)} charts")
    print("Saved as: test_paper_with_charts.pdf")

if __name__ == "__main__":
    test_pdf_with_charts()