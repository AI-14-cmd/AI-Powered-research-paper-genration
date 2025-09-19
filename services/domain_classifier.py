import google.generativeai as genai
import os
from typing import Dict

class DomainClassifier:
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
        
        # IEEE/Springer domain categories
        self.domain_categories = [
            "Computer Science", "Electrical Engineering", "Biomedical Engineering",
            "Mechanical Engineering", "Civil Engineering", "Chemical Engineering",
            "Materials Science", "Physics", "Mathematics", "Biology",
            "Medicine", "Neuroscience", "Psychology", "Economics",
            "Business", "Management", "Social Sciences", "Environmental Science",
            "Energy Systems", "Telecommunications", "Robotics", "Artificial Intelligence"
        ]
    
    def classify_domain(self, text: str, title: str = "") -> Dict:
        """Classify research paper into academic domain following IEEE/Springer/APA/MLA style"""
        
        prompt = f"""
        I am working with research papers and want to identify their domain in the same way digital libraries or citation styles (IEEE, Springer, APA, MLA, etc.) classify them.
        
        Title: {title}
        Abstract/Content: {text[:1000]}
        
        Your task is to:
        1. Analyze the content
        2. Classify it into the most appropriate single research domain (just one name)
        3. Present the domain as [Domain: ___]
        
        Make sure the domain label follows the style of how IEEE, Springer, APA, or MLA would categorize research work.
        
        Choose from these standard academic domains:
        {', '.join(self.domain_categories)}
        
        Respond ONLY with: [Domain: YourDomainName]
        """
        
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                if response and response.text:
                    response_text = response.text.strip()
                    # Extract domain from [Domain: ...] format
                    if '[Domain:' in response_text and ']' in response_text:
                        domain = response_text.split('[Domain:')[1].split(']')[0].strip()
                        if domain in self.domain_categories:
                            return {
                                'domain': domain,
                                'confidence': 'high',
                                'method': 'ai_classification',
                                'formatted_output': f'[Domain: {domain}]'
                            }
            except Exception as e:
                print(f"Domain classification error: {e}")
        
        # Fallback keyword-based classification
        return self._keyword_classification(text, title)
    
    def _keyword_classification(self, text: str, title: str = "") -> Dict:
        """Fallback keyword-based domain classification"""
        content = (title + " " + text).lower()
        
        domain_keywords = {
            "Computer Science": ["algorithm", "software", "programming", "computing", "data structure"],
            "Artificial Intelligence": ["ai", "machine learning", "neural network", "deep learning", "nlp"],
            "Biomedical Engineering": ["biomedical", "medical device", "healthcare", "clinical"],
            "Neuroscience": ["brain", "neural", "fmri", "eeg", "neuron", "cognitive"],
            "Electrical Engineering": ["circuit", "signal", "electronics", "power", "voltage"],
            "Mechanical Engineering": ["mechanical", "thermal", "fluid", "dynamics", "manufacturing"],
            "Physics": ["quantum", "particle", "wave", "energy", "physics"],
            "Mathematics": ["theorem", "proof", "mathematical", "equation", "statistics"],
            "Medicine": ["patient", "treatment", "diagnosis", "clinical", "medical"],
            "Biology": ["cell", "gene", "protein", "organism", "biological"]
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                scores[domain] = score
        
        if scores:
            best_domain = max(scores, key=scores.get)
            return {
                'domain': best_domain,
                'confidence': 'medium',
                'method': 'keyword_matching',
                'formatted_output': f'[Domain: {best_domain}]'
            }
        
        return {
            'domain': 'Computer Science',
            'confidence': 'low',
            'method': 'default',
            'formatted_output': '[Domain: Computer Science]'
        }