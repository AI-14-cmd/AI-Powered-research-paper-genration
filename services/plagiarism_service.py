import requests
import hashlib
import random
from typing import Dict

class PlagiarismService:
    def __init__(self):
        self.api_endpoints = {
            'copyleaks': 'https://api.copyleaks.com/v3/education/submit/file',
            'turnitin': 'https://api.turnitin.com/v1/submissions'
        }
    
    def check_plagiarism(self, text: str) -> Dict:
        # For hackathon demo - simulate plagiarism check
        # In production, integrate with actual plagiarism APIs
        
        try:
            # Simulate API call delay
            import time
            time.sleep(1)
            
            # Calculate basic metrics
            word_count = len(text.split())
            char_count = len(text)
            
            # Simulate plagiarism score based on text characteristics
            text_hash = hashlib.md5(text.encode()).hexdigest()
            hash_sum = sum(int(c, 16) for c in text_hash[:8])
            
            # Generate realistic plagiarism score (usually low for generated content)
            base_score = (hash_sum % 15) + random.randint(0, 10)  # 0-25%
            
            # Adjust based on text length (longer texts might have higher scores)
            if word_count > 500:
                base_score += random.randint(0, 5)
            
            plagiarism_score = min(base_score, 30)  # Cap at 30%
            
            # Determine status
            if plagiarism_score < 10:
                status = "Low Risk"
                color = "green"
            elif plagiarism_score < 20:
                status = "Medium Risk"
                color = "orange"
            else:
                status = "High Risk"
                color = "red"
            
            # Generate mock sources if score is high enough
            sources = []
            if plagiarism_score > 15:
                sources = [
                    {
                        'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8234567/',
                        'title': 'Similar Research Paper on Related Topic',
                        'similarity': f"{random.randint(5, 15)}%"
                    },
                    {
                        'url': 'https://arxiv.org/abs/2301.12345',
                        'title': 'Academic Paper with Similar Content',
                        'similarity': f"{random.randint(3, 8)}%"
                    }
                ]
            
            return {
                'plagiarism_score': plagiarism_score,
                'status': status,
                'color': color,
                'word_count': word_count,
                'char_count': char_count,
                'sources': sources,
                'checked_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'api_used': 'Demo Plagiarism Checker'
            }
            
        except Exception as e:
            print(f"Plagiarism check error: {e}")
            return {
                'plagiarism_score': 0,
                'status': 'Check Failed',
                'color': 'gray',
                'word_count': len(text.split()),
                'char_count': len(text),
                'sources': [],
                'error': str(e)
            }
    
    def _real_plagiarism_check(self, text: str, api_key: str = None) -> Dict:
        """
        Template for real plagiarism API integration
        Uncomment and modify for production use
        """
        # if not api_key:
        #     raise ValueError("API key required for plagiarism check")
        
        # headers = {
        #     'Authorization': f'Bearer {api_key}',
        #     'Content-Type': 'application/json'
        # }
        
        # payload = {
        #     'text': text,
        #     'language': 'en',
        #     'sandbox': True  # For testing
        # }
        
        # response = requests.post(
        #     self.api_endpoints['copyleaks'],
        #     headers=headers,
        #     json=payload,
        #     timeout=30
        # )
        
        # return response.json()
        
        pass