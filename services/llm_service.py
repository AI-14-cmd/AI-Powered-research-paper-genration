import openai
import google.generativeai as genai
import os
from typing import Dict, List
from dotenv import load_dotenv

# Configure Gemini API globally
load_dotenv()
genai.configure(api_key='AIzaSyCZq5xnAeug9WX5FrdB8dgV-8eOgevEta4')

class LLMService:
    def __init__(self):
        # Ensure environment variables are loaded
        load_dotenv()
        
        # Initialize OpenAI as fallback
        self.openai_key = os.getenv('OPENAI_API_KEY', 'sk-test-key-placeholder')
        if self.openai_key and self.openai_key != 'sk-test-key-placeholder':
            try:
                openai.api_key = self.openai_key
                print(f"OpenAI configured as fallback: {self.openai_key[:10]}...")
            except Exception as e:
                print(f"OpenAI configuration error: {e}")
                self.openai_key = None
        
        # Initialize Gemini with API key
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCZq5xnAeug9WX5FrdB8dgV-8eOgevEta4')
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"Gemini initialized: {self.gemini_api_key[:10]}...")
        except Exception as e:
            print(f"Gemini initialization failed: {e}")
            self.gemini_model = None
        
        # Preferred LLM (gemini, openai, or fallback)
        self.preferred_llm = os.getenv('PREFERRED_LLM', 'gemini').lower()
        # Remove static fallback content - use dynamic generation instead
    
    def generate_section(self, topic: str, section: str, research_level: str = 'intermediate', keywords: list = None, research_field: str = None) -> str:
        word_count = {'beginner': 150, 'intermediate': 200, 'advanced': 300}[research_level]
        
        # Enhanced prompts with topic, keywords, and research field context
        keyword_context = f" focusing on {', '.join(keywords)}" if keywords else ""
        field_context = f" in the field of {research_field}" if research_field else ""
        
        prompts = {
            'title': f"Generate ONE concise IEEE conference paper title about '{topic}'{keyword_context}{field_context}. Return ONLY the title text, nothing else. Maximum 12 words, no options or explanations.",
            'abstract': f"Write a {word_count}-word IEEE-style abstract for '{topic}'{keyword_context}. Structure: (1) Problem statement, (2) Approach/methodology, (3) Key results with specific metrics, (4) Conclusions. Use numbered citations [1], [2]. End with 'Keywords:' followed by 5-7 relevant keywords.",
            'introduction': f"Write Section 1. INTRODUCTION ({word_count} words) for '{topic}'{keyword_context}. Include numbered subsections (1.1, 1.2). Use IEEE citations [1], [2]. Cover: problem background, research gap, objectives, contributions. Reference figures as Fig. 1, tables as Table I.",
            'literature_review': f"Write Section 2. RELATED WORK ({word_count} words) for '{topic}'{keyword_context}. Use numbered subsections (2.1, 2.2). Include IEEE citations [1]-[5]. Discuss recent work (2020-2024), compare approaches, identify gaps.",
            'methodology': f"Write Section 3. METHODOLOGY ({word_count} words) for '{topic}'{keyword_context}. Use subsections (3.1, 3.2). Include equations if relevant. Reference Fig. 2, Table II. Describe experimental setup, algorithms, evaluation metrics.",
            'results': f"Write Section 4. RESULTS ({word_count} words) for '{topic}'{keyword_context}. Use subsections (4.1, 4.2). Present quantitative results, reference Fig. 3, Table III. Include performance metrics, comparisons with baselines.",
            'discussion': f"Write Section 4. DISCUSSION ({word_count} words) for '{topic}'{keyword_context}. Use subsections (4.1, 4.2). Analyze results, compare with related work, discuss implications, limitations.",
            'conclusion': f"Write Section 5. CONCLUSION ({word_count} words) for '{topic}'{keyword_context}. Summarize contributions, key findings, limitations, future work. No subsections needed."
        }
        
        prompt = prompts.get(section, f"Write about {section} for {topic}")
        
        # Try Gemini API first
        try:
            genai.configure(api_key='AIzaSyCZq5xnAeug9WX5FrdB8dgV-8eOgevEta4')
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            if response and response.text and len(response.text.strip()) > 20:
                print(f"Generated {len(response.text)} chars for {section} with Gemini")
                return response.text.strip()
                
        except Exception as e:
            print(f"Gemini failed for {section}: {e}")
        
        # Try OpenAI as fallback
        if self.openai_key:
            try:
                import openai
                openai.api_key = self.openai_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert academic writer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                content = response.choices[0].message.content
                if content and len(content.strip()) > 20:
                    print(f"Generated {len(content)} chars for {section} with OpenAI")
                    return content.strip()
            except Exception as e:
                print(f"OpenAI also failed for {section}: {e}")
        
        # Generate basic content as last resort
        print(f"Using basic content generator for {section}")
        return self._generate_basic_content(topic, section, research_level, keywords, research_field)
    

    
    def _generate_with_gemini(self, prompt: str) -> str:
        try:
            response = self.gemini_model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def _generate_with_openai(self, prompt: str, word_count: int) -> str:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=word_count + 100,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def find_real_papers(self, topic: str, keywords: List[str] = None) -> List[Dict]:
        """Use Gemini to find real academic papers related to the topic"""
        prompt = f"""
        Find 3-5 real, published academic papers about "{topic}". 
        {f"Focus on keywords: {', '.join(keywords)}" if keywords else ""}
        
        For each paper, provide ONLY real, verifiable information:
        - Exact published title
        - Real author names
        - Actual journal/conference name
        - Real publication year (2018-2024)
        - Real DOI if known
        - Actual research summary (2-3 sentences)
        
        Return as simple text list, one paper per paragraph:
        Title: [exact title]
        Authors: [real authors]
        Journal: [real journal] ([year])
        DOI: [real DOI or "Not available"]
        Summary: [actual research summary]
        """
        
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return self._parse_papers_response(response.text, topic)
            except Exception as e:
                error_str = str(e).lower()
                print(f"Gemini paper search error: {e}")
                if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "exceeded"]):
                    print("⚠️  API quota exceeded - using curated paper database")
                    self.gemini_model = None
        
        return self._get_fallback_papers(topic)
    
    def _parse_papers_response(self, response_text: str, topic: str) -> List[Dict]:
        """Parse Gemini response into paper objects"""
        papers = []
        current_paper = {}
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('Title:'):
                if current_paper:
                    papers.append(current_paper)
                current_paper = {'title': line.replace('Title:', '').strip()}
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
            elif line.startswith('Summary:'):
                current_paper['abstract'] = line.replace('Summary:', '').strip()
        
        if current_paper:
            papers.append(current_paper)
        
        return papers[:5] if papers else []
    
    def _get_fallback_papers(self, topic: str) -> List[Dict]:
        """No fallback papers - return empty list"""
        return []
    
    def _generate_basic_content(self, topic: str, section: str, research_level: str = 'intermediate', keywords: list = None, research_field: str = None) -> str:
        """Generate basic content when APIs fail"""
        keyword_text = f" focusing on {', '.join(keywords)}" if keywords else ""
        field_text = f" in {research_field}" if research_field else ""
        
        if section == 'title':
            return f"{topic}: A Comprehensive Study{field_text}"
            
        elif section == 'abstract':
            return f"This study examines {topic.lower()}{field_text}{keyword_text}. The research addresses current challenges and proposes innovative solutions. Through systematic analysis and evaluation, this work contributes to the understanding of {topic.lower()} applications. The findings demonstrate significant potential for practical implementation and future research directions. Keywords: {', '.join(keywords) if keywords else 'research, analysis, methodology'}."
            
        elif section == 'introduction':
            return f"The field of {topic.lower()}{field_text} has gained significant attention in recent years{keyword_text}. This research addresses key challenges and opportunities in the domain. The study aims to provide comprehensive analysis and practical insights. Current approaches face limitations that this work seeks to address through innovative methodologies and systematic evaluation."
            
        elif section == 'literature_review':
            return f"Recent literature in {topic.lower()}{field_text} reveals diverse approaches and methodologies{keyword_text}. Researchers have explored various techniques and frameworks to address domain-specific challenges. Current studies demonstrate both achievements and limitations in existing approaches. This review identifies key research gaps and opportunities for future investigation."
            
        elif section == 'methodology':
            return f"This research employs a systematic approach to investigate {topic.lower()}{field_text}{keyword_text}. The methodology includes comprehensive data collection, analysis techniques, and evaluation frameworks. Experimental design ensures reliable and reproducible results. Validation procedures confirm the effectiveness of proposed approaches."
            
        elif section == 'results':
            return f"The experimental evaluation of {topic.lower()} approaches demonstrates significant improvements{keyword_text}. Performance metrics show enhanced effectiveness compared to baseline methods. Statistical analysis confirms the reliability of findings. Results indicate practical applicability and potential for real-world implementation."
            
        elif section == 'conclusion':
            return f"This study provides valuable insights into {topic.lower()}{field_text}{keyword_text}. The research contributes to theoretical understanding and practical applications. Key findings demonstrate the effectiveness of proposed approaches. Future work should explore additional applications and refinements of the methodology."
            
        else:
            return f"This section discusses {section} in the context of {topic.lower()}{field_text}{keyword_text}. The analysis provides important insights and contributes to the overall understanding of the research domain."
    
    def generate_bibliography_file(self, papers: List[Dict], citation_style: str) -> str:
        """Generate a separate bibliography file"""
        if citation_style.upper() == 'APA':
            content = "# References (APA Style)\n\n"
            for paper in papers:
                content += f"{paper['authors']} ({paper['year']}). {paper['title']}. *{paper['journal']}*. {paper.get('doi', '')}\n\n"
        elif citation_style.upper() == 'MLA':
            content = "# Works Cited (MLA Style)\n\n"
            for paper in papers:
                content += f"{paper['authors']}. \"{paper['title']}.\" *{paper['journal']}*, {paper['year']}, {paper.get('doi', '')}.\n\n"
        else:  # IEEE
            content = "# References (IEEE Style)\n\n"
            for i, paper in enumerate(papers, 1):
                content += f"[{i}] {paper['authors']}, \"{paper['title']},\" *{paper['journal']}*, {paper['year']}.\n\n"
        
        return content
    
    def generate_research_notes(self, topic: str, papers: List[Dict]) -> str:
        """Generate research notes file"""
        content = f"# Research Notes: {topic}\n\n"
        content += f"## Key Papers Found\n\n"
        
        for i, paper in enumerate(papers, 1):
            content += f"### {i}. {paper['title']}\n"
            content += f"**Authors:** {paper['authors']}\n"
            content += f"**Journal:** {paper['journal']} ({paper['year']})\n"
            content += f"**Summary:** {paper['abstract']}\n\n"
        
        content += "## Research Questions\n\n"
        content += "- What are the current challenges in this field?\n"
        content += "- What methodologies are commonly used?\n"
        content += "- What are the future research directions?\n\n"
        
        return content
    
    def generate_summary(self, paper_content: Dict[str, str]) -> List[str]:
        full_text = ' '.join([content for content in paper_content.values() if isinstance(content, str)])
        prompt = f"Generate 5 key bullet points summarizing this research paper: {full_text[:1000]}"
        
        # Try Gemini first
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                summary = response.text.strip()
                return [point.strip('• -') for point in summary.split('\n') if point.strip()]
            except Exception as e:
                error_str = str(e).lower()
                print(f"Gemini summary error: {e}")
                if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "exceeded"]):
                    print("⚠️  API quota exceeded - using offline summary generation")
                    self.gemini_model = None
        
        # Try OpenAI
        if openai.api_key:
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=200,
                    temperature=0.5
                )
                summary = response.choices[0].text.strip()
                return [point.strip('• -') for point in summary.split('\n') if point.strip()]
            except Exception as e:
                print(f"OpenAI summary error: {e}")
        
        # Return empty list if APIs fail
        return []