#!/usr/bin/env python3

from services.image_generator import ImageGenerator

def test_chart_generation():
    print("Testing Chart Generation for Traffic Analyzers...")
    
    img_gen = ImageGenerator()
    
    # Test chart generation for traffic analyzers topic
    paper_content = {
        'title': 'Machine Learning for Enhanced Traffic Analyzer Performance',
        'abstract': 'This research investigates machine learning applications in traffic analysis...'
    }
    
    print("\n=== GENERATING CHARTS ===")
    charts = img_gen.generate_research_charts('traffic analyzers', paper_content)
    
    print(f"Generated {len(charts)} charts:")
    for i, chart in enumerate(charts, 1):
        print(f"{i}. {chart['title']}")
        print(f"   Caption: {chart['caption'][:100]}...")
        print(f"   Image data length: {len(chart['image'])} chars")
        print()
    
    if charts:
        print("✅ CHARTS GENERATED SUCCESSFULLY")
        # Save first chart as example
        if charts[0]['image'].startswith('data:image/png;base64,'):
            print("✅ Chart contains valid base64 image data")
        else:
            print("❌ Chart image data format issue")
    else:
        print("❌ NO CHARTS GENERATED")

if __name__ == "__main__":
    test_chart_generation()