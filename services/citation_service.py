import requests
from typing import List, Dict
import time
import urllib.parse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class CitationService:
    def __init__(self):
        self.semantic_scholar_base = "https://api.semanticscholar.org/graph/v1"
        self.crossref_base = "https://api.crossref.org/works"
        
        # Rate limiting for CrossRef API
        self.last_crossref_call = 0
        self.crossref_delay = 1  # 1 second between calls
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        

    
    def fetch_citations(self, topic: str, limit: int = 5) -> List[Dict]:
        citations = []
        
        # Try CrossRef first (more reliable and comprehensive)
        try:
            citations = self._fetch_crossref(topic, limit)
            if len(citations) >= 3:
                print(f"Found {len(citations)} citations from CrossRef")
                return citations
        except Exception as e:
            print(f"CrossRef API error: {e}")
        
        # Try Semantic Scholar as backup
        try:
            semantic_citations = self._fetch_semantic_scholar(topic, limit)
            citations.extend(semantic_citations)
            if len(citations) >= 3:
                print(f"Found {len(citations)} citations from Semantic Scholar")
                return citations[:limit]
        except Exception as e:
            print(f"Semantic Scholar API error: {e}")
        
        # No fallback - return empty if APIs fail
        print(f"No citations available - API services failed for {topic}")
        return []
    
    def _fetch_semantic_scholar(self, topic: str, limit: int) -> List[Dict]:
        url = f"{self.semantic_scholar_base}/paper/search"
        params = {
            'query': topic,
            'limit': limit,
            'fields': 'title,authors,year,doi,journal,abstract'
        }
        
        response = self.session.get(url, params=params, timeout=8)
        response.raise_for_status()
        
        data = response.json()
        citations = []
        
        for paper in data.get('data', []):
            if paper.get('title') and paper.get('authors'):
                citation = {
                    'title': paper['title'],
                    'authors': [author.get('name', 'Unknown') for author in paper.get('authors', [])[:3]],
                    'year': paper.get('year', 'n.d.'),
                    'doi': paper.get('doi', ''),
                    'journal': paper.get('journal', {}).get('name', 'Unknown Journal') if paper.get('journal') else 'Unknown Journal'
                }
                citations.append(citation)
        
        return citations
    
    def _fetch_crossref(self, topic: str, limit: int) -> List[Dict]:
        url = self.crossref_base
        
        # Enhanced search parameters for better results
        params = {
            'query': topic,
            'rows': min(limit * 2, 20),  # Get more results to filter
            'sort': 'relevance',
            'order': 'desc',
            'filter': 'from-pub-date:2018,until-pub-date:2024',  # Recent papers
            'select': 'title,author,published-print,published-online,DOI,container-title,abstract,type'
        }
        
        # Rate limiting for CrossRef API
        current_time = time.time()
        if current_time - self.last_crossref_call < self.crossref_delay:
            time.sleep(self.crossref_delay - (current_time - self.last_crossref_call))
        
        headers = {
            'User-Agent': 'AI Research Paper Generator (mailto:research@example.com)'
        }
        
        self.last_crossref_call = time.time()
        response = self.session.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        
        data = response.json()
        citations = []
        
        for item in data.get('message', {}).get('items', []):
            # Filter for journal articles only
            if item.get('type') not in ['journal-article', 'proceedings-article']:
                continue
                
            if item.get('title') and item.get('author'):
                authors = []
                for author in item.get('author', [])[:3]:
                    if 'family' in author:
                        given = author.get('given', '').strip()
                        family = author.get('family', '').strip()
                        if given and family:
                            name = f"{given} {family}"
                        elif family:
                            name = family
                        else:
                            continue
                        authors.append(name)
                
                # Get publication year from multiple sources
                year = 'n.d.'
                for date_field in ['published-print', 'published-online']:
                    if date_field in item:
                        date_parts = item[date_field].get('date-parts', [[]])
                        if date_parts and date_parts[0] and len(date_parts[0]) > 0:
                            year = date_parts[0][0]
                            break
                
                # Clean title
                title = item['title'][0] if isinstance(item['title'], list) else item['title']
                title = title.strip()
                
                # Get journal name
                journal = 'Unknown Journal'
                if item.get('container-title'):
                    journal = item['container-title'][0] if isinstance(item['container-title'], list) else item['container-title']
                
                # Only include if we have essential information
                if authors and title and len(title) > 10:
                    citation = {
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'doi': item.get('DOI', ''),
                        'journal': journal,
                        'abstract': item.get('abstract', '')[:200] + '...' if item.get('abstract') else ''
                    }
                    citations.append(citation)
                    
                    if len(citations) >= limit:
                        break
        
        return citations
    
    def search_crossref_by_keywords(self, keywords: List[str], limit: int = 5) -> List[Dict]:
        """Enhanced CrossRef search using specific keywords"""
        # Combine keywords for better search
        query = ' AND '.join([f'"{keyword}"' for keyword in keywords[:3]])
        
        url = self.crossref_base
        params = {
            'query': query,
            'rows': limit,
            'sort': 'relevance',
            'filter': 'from-pub-date:2020,type:journal-article',
            'select': 'title,author,published-print,DOI,container-title,abstract'
        }
        
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_crossref_call < self.crossref_delay:
                time.sleep(self.crossref_delay - (current_time - self.last_crossref_call))
            
            headers = {'User-Agent': 'AI Research Paper Generator (mailto:research@example.com)'}
            self.last_crossref_call = time.time()
            
            response = self.session.get(url, params=params, headers=headers, timeout=8)
            response.raise_for_status()
            
            data = response.json()
            citations = []
            
            for item in data.get('message', {}).get('items', []):
                if item.get('title') and item.get('author'):
                    authors = []
                    for author in item.get('author', [])[:3]:
                        if 'family' in author:
                            given = author.get('given', '').strip()
                            family = author.get('family', '').strip()
                            name = f"{given} {family}".strip() if given else family
                            if name:
                                authors.append(name)
                    
                    year = 'n.d.'
                    if 'published-print' in item:
                        date_parts = item['published-print'].get('date-parts', [[]])
                        if date_parts and date_parts[0]:
                            year = date_parts[0][0]
                    
                    title = item['title'][0] if isinstance(item['title'], list) else item['title']
                    journal = item.get('container-title', ['Unknown Journal'])[0] if item.get('container-title') else 'Unknown Journal'
                    
                    if authors and title:
                        citations.append({
                            'title': title.strip(),
                            'authors': authors,
                            'year': year,
                            'doi': item.get('DOI', ''),
                            'journal': journal
                        })
            
            return citations
            
        except Exception as e:
            print(f"CrossRef keyword search error: {e}")
            return []
    

    
    def format_citation(self, citation: Dict, style: str = 'APA') -> str:
        authors = citation.get('authors', ['Unknown'])
        title = citation.get('title', 'Unknown Title')
        year = citation.get('year', 'n.d.')
        journal = citation.get('journal', 'Unknown Journal')
        doi = citation.get('doi', '')
        
        if style.upper() == 'IEEE':
            # Format authors as "J. Smith, A. Johnson, and B. Wilson"
            if isinstance(authors, str):
                authors = [authors]
            
            formatted_authors = []
            for author in authors[:6]:  # IEEE allows up to 6 authors
                if ',' in author:
                    # Already in "Last, First" format
                    parts = author.split(', ')
                    if len(parts) >= 2:
                        last = parts[0].strip()
                        first = parts[1].strip()
                        formatted_authors.append(f"{first[0]}. {last}" if first else last)
                    else:
                        formatted_authors.append(author.strip())
                else:
                    # "First Last" format
                    parts = author.strip().split()
                    if len(parts) >= 2:
                        first = parts[0]
                        last = ' '.join(parts[1:])
                        formatted_authors.append(f"{first[0]}. {last}")
                    else:
                        formatted_authors.append(author.strip())
            
            if len(authors) > 6:
                author_str = ', '.join(formatted_authors) + ', et al.'
            elif len(formatted_authors) > 1:
                author_str = ', '.join(formatted_authors[:-1]) + ', and ' + formatted_authors[-1]
            else:
                author_str = formatted_authors[0] if formatted_authors else 'Unknown'
            
            # IEEE format: [1] J. Smith and A. Johnson, "Title," Journal Name, vol. X, no. Y, pp. Z-W, Month Year.
            formatted = f'{author_str}, "{title}," {journal}'
            if year != 'n.d.':
                formatted += f', {year}'
            if doi:
                formatted += f', doi: {doi}'
            formatted += '.'
            return formatted
        
        elif style.upper() == 'APA':
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += ', et al.'
            
            formatted = f"{author_str} ({year}). {title}. *{journal}*"
            if doi:
                formatted += f". https://doi.org/{doi}"
            return formatted
        
        elif style.upper() == 'MLA':
            if authors:
                author_str = authors[0]
                if len(authors) > 1:
                    author_str += ', et al.'
            else:
                author_str = 'Unknown'
            
            return f'{author_str}. "{title}." *{journal}*, {year}.'
        
        return f"{', '.join(authors)} ({year}). {title}. {journal}."