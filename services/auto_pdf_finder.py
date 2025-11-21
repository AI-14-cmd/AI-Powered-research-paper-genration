import requests
import google.generativeai as genai
import os
from typing import List, Dict

class AutoPDFFinder:
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
    
    def find_real_pdfs(self, topic: str, keywords: List[str] = None) -> List[Dict]:
        """Find real academic papers using multiple APIs"""
        papers = []
        
        # Try arXiv API first
        try:
            arxiv_papers = self._search_arxiv(topic, keywords)
            papers.extend(arxiv_papers)
        except Exception as e:
            print(f"arXiv API error: {e}")
        
        # Try Semantic Scholar API
        try:
            semantic_papers = self._search_semantic_scholar(topic)
            papers.extend(semantic_papers)
        except Exception as e:
            print(f"Semantic Scholar API error: {e}")
        
        if not papers:
            print(f"No real papers found for {topic} - API services unavailable")
            return []
        return papers[:5]
    
    def _parse_pdf_response(self, response_text: str) -> List[Dict]:
        """Parse Gemini response into paper objects"""
        papers = []
        current_paper = {}
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('PAPER '):
                if current_paper:
                    papers.append(current_paper)
                current_paper = {}
            elif line.startswith('Title:'):
                current_paper['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Authors:'):
                current_paper['authors'] = line.replace('Authors:', '').strip()
            elif line.startswith('Journal:'):
                journal_info = line.replace('Journal:', '').strip()
                if '(' in journal_info and ')' in journal_info:
                    journal = journal_info.split('(')[0].strip()
                    year = journal_info.split('(')[1].split(')')[0].strip()
                    current_paper['journal'] = journal
                    current_paper['year'] = year
                else:
                    current_paper['journal'] = journal_info
                    current_paper['year'] = '2023'
            elif line.startswith('DOI:'):
                current_paper['doi'] = line.replace('DOI:', '').strip()
            elif line.startswith('Abstract:'):
                current_paper['abstract'] = line.replace('Abstract:', '').strip()
            elif line.startswith('PDF:'):
                pdf_url = line.replace('PDF:', '').strip()
                if pdf_url.startswith('http') and pdf_url.endswith('.pdf'):
                    current_paper['pdf_url'] = pdf_url
        
        if current_paper:
            papers.append(current_paper)
        
        return papers[:5]
    
    def _search_arxiv(self, topic: str, keywords: List[str] = None) -> List[Dict]:
        """Search arXiv for real papers"""
        import urllib.parse
        
        query = topic
        if keywords:
            query = f"{topic} {' '.join(keywords[:2])}"
        
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=3"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        papers = []
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            authors = [author.find('{http://www.w3.org/2005/Atom}name').text 
                      for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            published = entry.find('{http://www.w3.org/2005/Atom}published').text[:4]
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()[:200]
            pdf_url = entry.find('{http://www.w3.org/2005/Atom}id').text.replace('abs', 'pdf') + '.pdf'
            
            papers.append({
                'title': title,
                'authors': ', '.join(authors[:3]),
                'journal': 'arXiv preprint',
                'year': published,
                'doi': f"arXiv:{entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]}",
                'abstract': summary,
                'pdf_url': pdf_url
            })
        
        return papers
    
    def _search_semantic_scholar(self, topic: str) -> List[Dict]:
        """Search Semantic Scholar for real papers"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            'query': topic,
            'limit': 3,
            'fields': 'title,authors,year,journal,abstract,openAccessPdf'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        papers = []
        for paper in data.get('data', []):
            if paper.get('title') and paper.get('authors'):
                pdf_url = None
                if paper.get('openAccessPdf'):
                    pdf_url = paper['openAccessPdf'].get('url')
                
                papers.append({
                    'title': paper['title'],
                    'authors': ', '.join([author.get('name', 'Unknown') for author in paper.get('authors', [])[:3]]),
                    'journal': paper.get('journal', {}).get('name', 'Unknown Journal') if paper.get('journal') else 'Unknown Journal',
                    'year': str(paper.get('year', 'n.d.')),
                    'doi': paper.get('paperId', ''),
                    'abstract': paper.get('abstract', 'Abstract not available')[:200],
                    'pdf_url': pdf_url or 'Not publicly available'
                })
        
        return papers
    
