#!/usr/bin/env python3

import json
from services.llm_service import LLMService
from services.image_generator import ImageGenerator
from services.auto_pdf_finder import AutoPDFFinder
from services.domain_classifier import DomainClassifier

def test_complete_paper_generation():
    print("Testing Complete Paper Generation Flow...")
    
    topic = "traffic analyzers"
    keywords = ["machine learning"]
    
    # Test all services
    llm = LLMService()
    img_gen = ImageGenerator()
    pdf_finder = AutoPDFFinder()
    domain_classifier = DomainClassifier()
    
    print("\n=== GENERATING PAPER CONTENT ===")
    
    # Generate paper sections
    paper_content = {}
    paper_content['title'] = llm.generate_section(topic, 'title', 'intermediate', keywords)
    paper_content['abstract'] = llm.generate_section(topic, 'abstract', 'intermediate', keywords)
    
    print(f"Title: {paper_content['title']}")
    print(f"Abstract length: {len(paper_content['abstract'])}")
    
    # Generate charts
    print("\n=== GENERATING CHARTS ===")
    charts = img_gen.generate_research_charts(topic, paper_content)
    paper_content['charts'] = charts
    
    print(f"Generated {len(charts)} charts")
    for chart in charts:
        print(f"- {chart['title']}")
    
    # Find real papers
    print("\n=== FINDING REAL PAPERS ===")
    real_papers = pdf_finder.find_real_pdfs(topic, keywords)
    paper_content['real_papers'] = real_papers
    
    print(f"Found {len(real_papers)} papers")
    for paper in real_papers:
        print(f"- {paper.get('title', 'No title')}")
    
    # Classify domain
    print("\n=== CLASSIFYING DOMAIN ===")
    domain_info = domain_classifier.classify_domain(paper_content['abstract'], paper_content['title'])
    
    print(f"Domain: {domain_info['domain']}")
    print(f"Confidence: {domain_info['confidence']}")
    
    # Create final paper structure (like the API would)
    final_paper = {
        'success': True,
        'paper': paper_content,
        'metadata': {
            'research_domain': domain_info['domain'],
            'domain_confidence': domain_info['confidence']
        }
    }
    
    print("\n=== FINAL VERIFICATION ===")
    print(f"Paper has title: {'title' in paper_content}")
    print(f"Paper has abstract: {'abstract' in paper_content}")
    print(f"Paper has charts: {'charts' in paper_content and len(paper_content['charts']) > 0}")
    print(f"Paper has real_papers: {'real_papers' in paper_content and len(paper_content['real_papers']) > 0}")
    print(f"Charts have image data: {all('image' in chart for chart in paper_content.get('charts', []))}")
    
    if all([
        'title' in paper_content,
        'abstract' in paper_content,
        'charts' in paper_content and len(paper_content['charts']) > 0,
        all('image' in chart for chart in paper_content.get('charts', []))
    ]):
        print("\nSUCCESS: All components ready for display")
        return True
    else:
        print("\nFAILED: Missing components")
        return False

if __name__ == "__main__":
    test_complete_paper_generation()