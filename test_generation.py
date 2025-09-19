#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.llm_service import LLMService

def test_generation():
    print("Testing LLM Service...")
    
    llm = LLMService()
    
    # Test title generation
    print("\n=== TESTING TITLE GENERATION ===")
    title = llm.generate_section('traffic analyzers', 'title', 'intermediate', ['machine learning'])
    print(f"Generated title: {title}")
    print(f"Title length: {len(title)}")
    
    # Test abstract generation  
    print("\n=== TESTING ABSTRACT GENERATION ===")
    abstract = llm.generate_section('traffic analyzers', 'abstract', 'intermediate', ['machine learning'])
    print(f"Generated abstract: {abstract[:300]}...")
    print(f"Abstract length: {len(abstract)}")
    
    # Check if content is accurate (not fallback)
    if "ERROR:" in title or "ERROR:" in abstract:
        print("\nX ACCURACY ISSUE: Gemini errors detected")
    elif len(title) > 200 or "Option 1" in title:
        print("\nX ACCURACY ISSUE: Title too long or contains options")
    elif len(abstract) < 200:
        print("\nX ACCURACY ISSUE: Abstract too short")
    else:
        print("\nOK ACCURACY CHECK: Content appears to be properly generated")

if __name__ == "__main__":
    test_generation()