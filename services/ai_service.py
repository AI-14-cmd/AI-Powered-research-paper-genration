import google.generativeai as genai
import openai
from config import Config

class AIService:
    def __init__(self):
        # Initialize OpenAI first
        if Config.OPENAI_API_KEY:
            try:
                openai.api_key = Config.OPENAI_API_KEY
                print("AI Service initialized with OpenAI API")
            except Exception as e:
                print(f"OpenAI configuration error: {e}")
        
        # Initialize Gemini as backup
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                print("Gemini API configured as backup")
            except Exception as e:
                print(f"Gemini configuration error: {e}")
    
    def generate_paper_content(self, topic, paper_type, length, outline=None):
        """Generate paper content using Gemini"""
        
        length_words = {
            'short': '800-1200 words',
            'medium': '1500-2500 words',
            'long': '3000-5000 words',
            'extended': '5000+ words'
        }
        
        paper_prompts = {
            'research': "Write a comprehensive research paper",
            'review': "Write a detailed literature review",
            'essay': "Write an academic essay",
            'thesis': "Write a thesis chapter",
            'report': "Write a technical report"
        }
        
        prompt = f"""
        {paper_prompts.get(paper_type, 'Write a research paper')} on the topic: {topic}
        
        Requirements:
        - Length: {length_words.get(length, '1500-2500 words')}
        - Include proper academic structure with introduction, body, and conclusion
        - Use formal academic writing style
        - Include placeholder citations in the format [Author, Year]
        - Ensure logical flow and coherent arguments
        - Include specific examples and evidence where relevant
        
        Structure the paper with clear headings and subheadings.
        Make it comprehensive, well-researched, and academically rigorous.
        """
        
        # Use Gemini with new API key
        if Config.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(prompt)
                print(f"Generated with Gemini: {len(response.text)} chars")
                return response.text
            except Exception as e:
                print(f"Gemini error: {e}")
                return f"Error with Gemini API: {str(e)}"
        
        return "Error: No Gemini API key configured."
    
    def generate_outline(self, topic, paper_type):
        """Generate paper outline"""
        prompt = f"""
        Create a detailed outline for a {paper_type} on the topic: {topic}
        
        Include:
        - Main sections and subsections
        - Key points to cover in each section
        - Logical flow of arguments
        - Suggested research areas
        
        Format as a structured outline with Roman numerals, letters, and numbers.
        """
        
        # Try OpenAI first
        if Config.OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert academic writer who creates detailed paper outlines."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Fallback to Gemini
        if Config.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "exceeded"]):
                    return f"⚠️ API quota exceeded. Please wait {self._extract_retry_time(str(e))} or try again later."
                return f"Error with Gemini API: {str(e)}"
        
        return "Error: No API keys configured. Please add OpenAI or Gemini API key."
    
    def generate_with_gemini(self, prompt, model_name="models/gemini-1.5-flash"):
        """Generate content using Google Gemini API"""
        # Try OpenAI first
        if Config.OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert academic writer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=3000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Fallback to Gemini
        if Config.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ["quota", "429", "rate limit", "exceeded"]):
                    return f"⚠️ Gemini API quota exceeded. Please wait {self._extract_retry_time(str(e))} or try again later."
                return f"Error with Gemini API: {str(e)}"
        
        return "Error: No API keys configured. Please add OpenAI or Gemini API key."
    
    def enhance_paper_from_source(self, topic, source_content, paper_type="research"):
        """Generate enhanced paper content using source material"""
        prompt = f"""
        Create a comprehensive {paper_type} paper on "{topic}" using the following source material as reference:
        
        Source Content:
        {source_content}
        
        Requirements:
        - Expand on the concepts from the source material
        - Add proper academic structure and flow
        - Include critical analysis and synthesis
        - Maintain academic writing standards
        - Add placeholder citations where appropriate
        - Ensure originality while building on the source ideas
        """
        
        return self.generate_with_gemini(prompt)
    
    def _extract_retry_time(self, error_message: str) -> str:
        """Extract retry time from error message"""
        try:
            if 'retry in' in error_message:
                # Extract seconds from error message
                import re
                match = re.search(r'retry in (\d+\.?\d*)s', error_message)
                if match:
                    seconds = float(match.group(1))
                    if seconds > 60:
                        minutes = int(seconds // 60)
                        return f"{minutes} minutes"
                    else:
                        return f"{int(seconds)} seconds"
            return "a few minutes"
        except:
            return "a few minutes"