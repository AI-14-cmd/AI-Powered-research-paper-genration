import re
from typing import Dict, List
import random

class QualityAnalyzer:
    def __init__(self):
        self.readability_levels = {
            'Elementary': (0, 30),
            'Middle School': (30, 50),
            'High School': (50, 60),
            'College': (60, 70),
            'Graduate': (70, 100)
        }
    
    def analyze_paper_quality(self, paper_content: Dict) -> Dict:
        # Calculate various quality metrics
        full_text = self._extract_text(paper_content)
        
        metrics = {
            'citation_quality': self._calculate_citation_quality(paper_content.get('citations_data', [])),
            'readability_score': self._calculate_readability(full_text),
            'structure_score': self._analyze_structure(paper_content),
            'originality_index': self._estimate_originality(full_text),
            'academic_tone_score': self._analyze_academic_tone(full_text),
            'word_count': len(full_text.split()),
            'estimated_pages': max(1, len(full_text.split()) // 250),
            'reading_time': f"{max(1, len(full_text.split()) // 200)} minutes"
        }
        
        # Overall quality score
        metrics['overall_quality'] = self._calculate_overall_score(metrics)
        
        return metrics
    
    def _extract_text(self, paper_content: Dict) -> str:
        text_sections = []
        for key, value in paper_content.items():
            if isinstance(value, str) and key not in ['metadata', 'citations_data']:
                text_sections.append(value)
        return ' '.join(text_sections)
    
    def _calculate_citation_quality(self, citations: List) -> int:
        if not citations:
            return 0
        
        score = 0
        for citation in citations:
            # Recent papers get higher scores
            year = citation.get('year', 2020)
            if isinstance(year, int) and year >= 2020:
                score += 20
            elif isinstance(year, int) and year >= 2015:
                score += 15
            else:
                score += 10
            
            # Papers with DOI get bonus
            if citation.get('doi'):
                score += 15
            
            # Journal papers get bonus
            if citation.get('journal'):
                score += 10
        
        return min(score // len(citations), 100)
    
    def _calculate_readability(self, text: str) -> Dict:
        # Simple readability estimation
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0:
            return {'score': 50, 'level': 'College'}
        
        avg_sentence_length = words / sentences
        complex_words = len([w for w in text.split() if len(w) > 6])
        
        # Simple readability formula
        score = max(0, 100 - (avg_sentence_length * 1.5) - (complex_words / words * 100))
        
        level = 'College'
        for level_name, (min_score, max_score) in self.readability_levels.items():
            if min_score <= score < max_score:
                level = level_name
                break
        
        return {'score': round(score, 1), 'level': level}
    
    def _analyze_structure(self, paper_content: Dict) -> int:
        score = 0
        required_sections = ['title', 'abstract', 'introduction', 'conclusion']
        
        for section in required_sections:
            if section in paper_content and paper_content[section]:
                score += 25
        
        # Bonus for additional sections
        bonus_sections = ['literature_review', 'methodology', 'results']
        for section in bonus_sections:
            if section in paper_content and paper_content[section]:
                score += 5
        
        # Bonus for references
        if paper_content.get('references'):
            score += 10
        
        return min(score, 100)
    
    def _estimate_originality(self, text: str) -> int:
        # Simple originality estimation based on text characteristics
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        
        if total_words == 0:
            return 50
        
        vocabulary_diversity = (unique_words / total_words) * 100
        
        # Simulate originality score
        base_score = min(vocabulary_diversity * 1.2, 90)
        return round(base_score + random.randint(-5, 10))
    
    def _analyze_academic_tone(self, text: str) -> int:
        academic_indicators = [
            'research', 'study', 'analysis', 'findings', 'methodology',
            'literature', 'evidence', 'significant', 'furthermore',
            'however', 'therefore', 'consequently', 'moreover'
        ]
        
        text_lower = text.lower()
        academic_count = sum(1 for word in academic_indicators if word in text_lower)
        total_words = len(text.split())
        
        if total_words == 0:
            return 50
        
        academic_ratio = (academic_count / total_words) * 100
        return min(round(academic_ratio * 10), 100)
    
    def _calculate_overall_score(self, metrics: Dict) -> int:
        weights = {
            'citation_quality': 0.25,
            'structure_score': 0.25,
            'originality_index': 0.20,
            'academic_tone_score': 0.15,
            'readability_score': 0.15
        }
        
        total_score = 0
        for metric, weight in weights.items():
            if metric in metrics:
                if metric == 'readability_score':
                    score = metrics[metric]['score']
                else:
                    score = metrics[metric]
                total_score += score * weight
        
        return round(total_score)

    def generate_recommendations(self, metrics: Dict) -> List[str]:
        recommendations = []
        
        if metrics['citation_quality'] < 70:
            recommendations.append("Add more recent citations (2020+) to improve citation quality")
        
        if metrics['structure_score'] < 80:
            recommendations.append("Consider adding methodology or results sections for better structure")
        
        if metrics['academic_tone_score'] < 60:
            recommendations.append("Use more academic language and formal terminology")
        
        if metrics['originality_index'] < 70:
            recommendations.append("Enhance originality by adding unique insights and analysis")
        
        if metrics['word_count'] < 500:
            recommendations.append("Expand content to meet academic paper length standards")
        
        return recommendations[:3]  # Return top 3 recommendations