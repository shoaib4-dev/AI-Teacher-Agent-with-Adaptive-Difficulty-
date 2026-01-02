"""

AI Agent using LangChain - Simple Implementation

"""



import os

import sys

import re

from typing import Dict, List, Any, Optional

from datetime import datetime

from pathlib import Path

# Gemini API Key (hardcoded)
GEMINI_API_KEY = "[enter api here]"

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False



from src.memory import AgentMemory

from src.reasoning import ReasoningService

from src.database.db import get_db_connection

from src.services.data_service import DataService



class AIAgent:
    """Simple AI Agent with LangChain"""
    
    def __init__(self, db_path: str, student_db_path: str = None):
        self.db_path = db_path
        self.student_db_path = student_db_path
        self.memory = AgentMemory(db_path)
        self.reasoning = ReasoningService(db_path)
        self.data_service = DataService()
        
        # Initialize LangChain LLM with Google Gemini
        self.llm = None
        api_key = GEMINI_API_KEY
        if api_key and LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.7,
                    google_api_key=api_key
                )
            except Exception as e:
                print(f"Gemini initialization error: {e}")
                pass
    
    def explain_topic(self, topic: str) -> Dict:
        """Explain a topic with comprehensive resources - returns content based on query type"""
        # Store original topic for Wikipedia link (exact as searched)
        original_topic = topic.strip()
        
        # Extract base topic and detect content type from query
        base_topic = topic.strip()
        content_type = None
        
        # Detect content type from the query and extract base topic
        topic_lower = topic.lower()
        base_topic = topic.strip()
        
        # #region agent log
        import json
        try:
            with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"src/agent.py:103","message":"Backend: Received query","data":{"originalTopic":topic[:100],"topicLower":topic_lower[:100]},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + '\n')
        except: pass
        # #endregion
        
        # Try to extract base topic from common patterns - simplified detection (order matters)
        # Check content type first (most specific patterns first to avoid false matches)
        if 'research papers' in topic_lower or ('research' in topic_lower and 'papers' in topic_lower):
            content_type = 'research_papers'
            if 'related to ' in topic_lower:
                after_related = topic.split('related to ', 1)[1]
                base_topic = after_related.split('.')[0].strip()
        elif 'advanced' in topic_lower and 'problems' in topic_lower:
            content_type = 'advanced_problems'
            if 'related to ' in topic_lower:
                after_related = topic.split('related to ', 1)[1]
                base_topic = after_related.split('.')[0].strip()
        elif 'advanced' in topic_lower and 'concepts' in topic_lower:
            content_type = 'advanced_concepts'
            if 'for ' in topic_lower:
                after_for = topic.split('for ', 1)[1]
                base_topic = after_for.split('.')[0].strip()
        elif 'problems' in topic_lower and ('practice' in topic_lower or 'exercises' in topic_lower):
            content_type = 'problems'
            if 'related to ' in topic_lower:
                after_related = topic.split('related to ', 1)[1]
                base_topic = after_related.split('.')[0].strip()
            elif 'of ' in topic_lower:
                after_of = topic.split('of ', 1)[1]
                base_topic = after_of.split('.')[0].strip()
        elif 'applications' in topic_lower:
            content_type = 'applications'
            if 'of ' in topic_lower:
                after_of = topic.split('of ', 1)[1]
                base_topic = after_of.split('.')[0].strip()
        elif 'examples' in topic_lower:
            content_type = 'examples'
            if 'of ' in topic_lower:
                after_of = topic.split('of ', 1)[1]
                base_topic = after_of.split('.')[0].strip()
        elif 'definition' in topic_lower:
            content_type = 'definition'
            if 'of ' in topic_lower:
                after_of = topic.split('of ', 1)[1]
                base_topic = after_of.split('.')[0].strip()
        elif 'introduction' in topic_lower:
            content_type = 'introduction'
            if 'for ' in topic_lower:
                after_for = topic.split('for ', 1)[1]
                base_topic = after_for.split('.')[0].strip()
        elif 'detailed explanation' in topic_lower or 'comprehensive explanation' in topic_lower:
            content_type = 'explanation'
            if 'of ' in topic_lower:
                # Extract topic after "of "
                parts = topic.split('of ', 1)[1].split()
                base_topic = parts[0].strip() if parts else topic.strip()
        
        # Clean up base topic - remove any trailing punctuation or extra words
        base_topic = base_topic.strip('.,;:!?')
        # Remove any trailing text after the topic name (common patterns)
        if base_topic:
            # Remove common trailing phrases
            for phrase in [' focus on', ' do not', ' include', ' explain', ' provide']:
                if phrase in base_topic.lower():
                    base_topic = base_topic.split(phrase, 1)[0].strip()
            # Take only first word or first few words (topic name is usually first)
            words = base_topic.split()
            if len(words) > 3:  # If too many words, likely got extra text
                # Try to find where the topic name ends (usually 1-3 words)
                base_topic = ' '.join(words[:3]).strip()
        
        # Fallback: remove any concept-specific suffixes
        if ' - ' in base_topic:
            parts = base_topic.split(' - ', 1)
            base_topic = parts[0].strip()
        
        # Final cleanup
        base_topic = base_topic.strip('.,;:!?').strip()
        
        # Fallback: If content_type is still None, try to infer from keywords
        if content_type is None:
            if 'introduction' in topic_lower:
                content_type = 'introduction'
            elif 'definition' in topic_lower and 'clear' in topic_lower:
                content_type = 'definition'
            elif 'examples' in topic_lower:
                content_type = 'examples'
            elif 'applications' in topic_lower:
                content_type = 'applications'
            elif 'problems' in topic_lower and 'practice' in topic_lower:
                content_type = 'problems'
            elif 'advanced' in topic_lower and 'concepts' in topic_lower:
                content_type = 'advanced_concepts'
            elif 'advanced' in topic_lower and 'problems' in topic_lower:
                content_type = 'advanced_problems'
            elif 'research' in topic_lower and 'papers' in topic_lower:
                content_type = 'research_papers'
            elif 'explanation' in topic_lower:
                content_type = 'explanation'
        
        # #region agent log
        import json
        import time
        try:
            with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"src/agent.py:210","message":"Backend: Content type detection result","data":{"contentType":content_type,"baseTopic":base_topic,"originalTopic":topic[:100],"topicLower":topic_lower[:150]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + '\n')
        except Exception as e:
            try:
                with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"location":"src/agent.py:210","message":"Backend: Log write error","data":{"error":str(e)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1"}) + '\n')
            except: pass
        # #endregion
        
        # Generate content using LLM if available
        if self.llm:
            print(f"Using LLM to generate {content_type or 'comprehensive'} content for: {base_topic}")
            try:
                # Generate different prompts based on content type
                if content_type == 'introduction':
                    prompt = f"""Provide ONLY an introduction and background context for {base_topic}. 

Focus on:
- What {base_topic} is and its purpose
- Historical development and origins
- Why it was created or developed
- Its significance and importance
- Context and background information

Do NOT include definitions, examples, applications, or detailed explanations. ONLY provide introduction and background context.

Write 3-5 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'definition':
                    prompt = f"""Provide ONLY a clear, precise definition of {base_topic}.

Focus on:
- What {base_topic} means exactly
- Core meaning and fundamental characteristics
- Essential properties and key attributes
- What distinguishes {base_topic} from similar concepts

Do NOT include examples, applications, explanations, or background. ONLY provide the definition.

Write 2-4 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'examples':
                    prompt = f"""Provide ONLY specific examples and use cases of {base_topic}.

Focus on:
- Concrete examples of {base_topic}
- Real-world use cases
- Code snippets if applicable
- Practical illustrations
- Specific scenarios where {base_topic} is used

Do NOT include definitions, explanations, or applications. ONLY provide examples.

Write 3-5 well-structured paragraphs with examples, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'applications':
                    prompt = f"""Provide ONLY real-world applications and practical uses of {base_topic}.

Focus on:
- Where {base_topic} is used in industry
- Applications in research and academia
- Practical uses in daily life
- Various domains and fields where it's applied
- Real-world impact and benefits

Do NOT include examples, definitions, or explanations. ONLY provide applications.

Write 3-5 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'problems':
                    prompt = f"""Provide ONLY practice problems, exercises, and questions related to {base_topic}.

Focus on:
- Problem statements and exercises
- Practice questions for students
- Hands-on exercises
- Problems to solve and practice

Do NOT include solutions, definitions, or explanations. ONLY provide problems and exercises.

Write 3-5 well-structured paragraphs with problems, each containing multiple practice questions. Separate paragraphs with blank lines."""
                
                elif content_type == 'advanced_concepts':
                    prompt = f"""Provide ONLY advanced related concepts, theories, and topics connected to {base_topic}.

Focus on:
- Cutting-edge developments in {base_topic}
- Advanced theories and concepts
- Related research areas
- Complex and advanced topics
- State-of-the-art developments

Do NOT include basic explanations. ONLY provide advanced concepts.

Write 4-6 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'advanced_problems':
                    prompt = f"""Provide ONLY advanced problems, challenges, and complex exercises related to {base_topic}.

Focus on:
- Difficult and challenging problems
- Research-level questions
- Complex scenarios and exercises
- Advanced problem-solving challenges

Do NOT include solutions or basic problems. ONLY provide advanced problems.

Write 3-5 well-structured paragraphs with advanced problems, each containing challenging questions. Separate paragraphs with blank lines."""
                
                elif content_type == 'research_papers':
                    prompt = f"""Provide ONLY information about research papers, academic resources, and scholarly work related to {base_topic}.

Focus on:
- Important research papers on {base_topic}
- Key researchers and their contributions
- Academic journals and publications
- Research directions and trends
- Scholarly resources and references

Do NOT include explanations or definitions. ONLY provide research paper information and academic resources.

Write 3-5 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                elif content_type == 'explanation':
                    # Check if it's intermediate level (5 paragraphs)
                    if 'exactly 5' in topic_lower or '5 comprehensive paragraphs' in topic_lower:
                        prompt = f"""Provide a detailed explanation of {base_topic} with EXACTLY 5 comprehensive paragraphs.

Each paragraph should be 8-12 sentences and cover:
1) How {base_topic} works - mechanisms and processes
2) Key principles and fundamental mechanisms
3) Important concepts and relationships
4) Technical details and processes
5) Why understanding {base_topic} matters

Do NOT include examples or applications. ONLY provide explanation.

Write EXACTLY 5 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                    else:
                        prompt = f"""Provide a comprehensive explanation of {base_topic} covering how it works.

Focus on:
- How {base_topic} functions and operates
- Key principles and mechanisms
- Technical details and processes
- Important concepts and relationships

Do NOT include examples, applications, or definitions. ONLY provide explanation of how {base_topic} works.

Write 4-6 well-structured paragraphs, each 8-12 sentences long. Separate paragraphs with blank lines."""
                
                else:
                    # Default comprehensive explanation
                    prompt = f"""Explain {base_topic} comprehensively for students. Provide a detailed explanation that includes:



1. A clear definition and overview of {base_topic}

2. Fundamental principles and basic concepts

3. Core concepts and key ideas

4. Real-world applications and examples

5. Why {base_topic} is important



IMPORTANT FORMATTING REQUIREMENTS:

- Write EXACTLY 6-10 well-structured paragraphs

- Each paragraph should be 8-12 sentences long (significantly longer and more detailed)

- Separate each paragraph with a blank line (double newline)

- Each paragraph should cover a distinct aspect of {base_topic} in depth

- Make the explanation comprehensive, educational, and clear with substantial detail

- Use proper paragraph breaks - do NOT write as one continuous block of text

- Each paragraph should be substantial (at least 150-200 words per paragraph)



Format your response with clear paragraph breaks like this:

[First paragraph about definition - 8-12 sentences, 150-200 words]



[Second paragraph about principles - 8-12 sentences, 150-200 words]



[Third paragraph about core concepts - 8-12 sentences, 150-200 words]



[Continue with 3-7 more paragraphs covering applications, importance, etc. - each 8-12 sentences long]



Now provide a comprehensive explanation of {base_topic} with 6-10 well-separated paragraphs, each being 8-12 sentences long (150-200 words per paragraph)."""
                
                # #region agent log
                import json
                try:
                    with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"src/agent.py:371","message":"Backend: Generated prompt","data":{"contentType":content_type,"baseTopic":base_topic,"promptPreview":prompt[:200]+'...'},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"}) + '\n')
                except: pass
                # #endregion
                
                response = self.llm.invoke(prompt)
                explanation = response.content
                
                # Log the explanation length for debugging
                print(f"LLM returned explanation of length: {len(explanation)} characters")
                
                # #region agent log
                try:
                    with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"src/agent.py:380","message":"Backend: LLM response received","data":{"contentType":content_type,"baseTopic":base_topic,"explanationLength":len(explanation),"explanationPreview":explanation[:200]+'...'},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"}) + '\n')
                except: pass
                # #endregion
                
                # Ensure explanation is not empty
                if not explanation or len(explanation.strip()) < 50:
                    print(f"Warning: LLM returned short explanation ({len(explanation.strip())} chars), using fallback")
                    raise Exception("LLM returned empty or too short explanation")
                
                # Post-process to ensure proper paragraph formatting
                # If explanation doesn't have double newlines, try to add them
                if '\n\n' not in explanation and '\n' in explanation:
                    # Already has some line breaks, ensure they're double
                    explanation = explanation.replace('\n', '\n\n')
                elif '\n\n' not in explanation and '\n' not in explanation:
                    # No line breaks at all - split by sentences and create paragraphs
                    sentences = explanation.split('. ')
                    # Group sentences into paragraphs (8-12 sentences per paragraph for longer paragraphs)
                    paragraphs = []
                    sentences_per_para = 10  # Increased from 3 to 10 for longer paragraphs
                    for i in range(0, len(sentences), sentences_per_para):
                        para_sentences = sentences[i:i+sentences_per_para]
                        para_text = '. '.join(para_sentences)
                        if not para_text.endswith('.'):
                            para_text += '.'
                        paragraphs.append(para_text)
                    explanation = '\n\n'.join(paragraphs)
                    
            except Exception as e:
                print(f"Error getting LLM explanation: {e}")
                explanation = self._generate_explanation_from_data(base_topic)
        else:
            print(f"LLM not available, using data-based explanation for: {base_topic}")
            explanation = self._generate_explanation_from_data(base_topic)
        
        # Use base_topic for resource generation (YouTube, etc.)
        topic_for_resources = base_topic
        # Use original_topic for Wikipedia link (exact topic as searched)
        topic_for_wikipedia = original_topic
        
        # Generate comprehensive resources using LLM
        youtube_links = []
        website_references = []
        
        if self.llm:
            try:
                # Get a single specific YouTube video recommendation
                youtube_prompt = f"""Provide ONE specific, popular, educational YouTube video title for learning {topic_for_resources}.

The video should be:
- Well-known and popular
- Educational and comprehensive
- Suitable for learning {topic_for_resources}

Format as:
[Video Title]

Example: "Machine Learning Full Course - Learn Machine Learning 10 Hours | Machine Learning Tutorial | Edureka"

Provide only the video title, nothing else."""
                
                youtube_response = self.llm.invoke(youtube_prompt)
                youtube_title = youtube_response.content.strip()
                
                # Clean up the title (remove quotes, numbers, etc.)
                youtube_title = youtube_title.lstrip('0123456789.-) ').strip()
                if youtube_title.startswith('"') and youtube_title.endswith('"'):
                    youtube_title = youtube_title[1:-1]
                if youtube_title.startswith("'") and youtube_title.endswith("'"):
                    youtube_title = youtube_title[1:-1]
                
                # Get the 2nd video from YouTube search results
                try:
                    import requests
                    import re
                    search_query = f"{topic_for_resources} tutorial"
                    # Search YouTube and extract video IDs from the page
                    search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}&sp=EgIQAQ%3D%3D"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(search_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        # Extract video IDs from the page (YouTube embeds video IDs in the HTML)
                        video_ids = re.findall(r'"videoId":"([^"]{11})"', response.text)
                        if len(video_ids) >= 2:
                            # Get the 2nd video ID (index 1)
                            video_id = video_ids[1]
                            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                            video_title = youtube_title if youtube_title else f"{topic_for_resources} - Tutorial"
                            print(f"[DEBUG] Found 2nd video ID: {video_id}")
                        else:
                            # Fallback: Use search URL if not enough videos found
                            youtube_url = search_url
                            video_title = youtube_title if youtube_title else f"{topic_for_resources} - Complete Tutorial"
                            print(f"[DEBUG] Could not find 2nd video, using search URL")
                    else:
                        # Fallback: Use search URL
                        youtube_url = search_url
                        video_title = youtube_title if youtube_title else f"{topic_for_resources} - Complete Tutorial"
                        print(f"[DEBUG] YouTube request failed, using search URL")
                except Exception as e:
                    # Fallback: Use search URL
                    print(f"[DEBUG] Error getting 2nd video: {e}, using search URL")
                    search_query_encoded = f"{topic_for_resources} tutorial".replace(' ', '+')
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query_encoded}&sp=EgIQAQ%3D%3D"
                    video_title = youtube_title if youtube_title else f"{topic_for_resources} - Complete Tutorial"
                
                youtube_links = [{
                    "title": video_title,
                    "url": youtube_url
                }]
                
                # Generate Wikipedia link for the exact topic searched (use original topic name)
                # Format topic name for Wikipedia URL (replace spaces with underscores, preserve capitalization)
                # Wikipedia URLs are case-sensitive and use underscores
                wiki_topic = topic_for_wikipedia.replace(' ', '_')
                # Remove any special characters that might cause issues, but keep underscores and hyphens
                wiki_topic = ''.join(c if c.isalnum() or c in ['_', '-'] else '' for c in wiki_topic)
                # Ensure it's a direct Wikipedia page link, not a search
                wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic}"
                print(f"[DEBUG] Generated Wikipedia URL: {wiki_url} for topic: {topic_for_wikipedia}")
                website_references = [{
                    "title": f"{topic_for_wikipedia} - Wikipedia",
                    "url": wiki_url
                }]
                    
            except Exception as e:
                print(f"Error generating resources: {e}")
                # Fallback: Get 2nd video from YouTube search
                try:
                    import requests
                    import re
                    search_query = f"{topic_for_resources} tutorial"
                    search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}&sp=EgIQAQ%3D%3D"
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.get(search_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        video_ids = re.findall(r'"videoId":"([^"]{11})"', response.text)
                        if len(video_ids) >= 2:
                            video_id = video_ids[1]
                            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                            video_title = f"{topic_for_resources} - Tutorial"
                            print(f"[DEBUG] Fallback: Found 2nd video ID: {video_id}")
                        else:
                            youtube_url = search_url
                            video_title = f"{topic_for_resources} - Complete Tutorial"
                    else:
                        youtube_url = search_url
                        video_title = f"{topic_for_resources} - Complete Tutorial"
                except Exception as e:
                    print(f"[DEBUG] Fallback error: {e}")
                    search_query_encoded = f"{topic_for_resources} tutorial".replace(' ', '+')
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query_encoded}&sp=EgIQAQ%3D%3D"
                    video_title = f"{topic_for_resources} - Complete Tutorial"
                
                youtube_links = [{
                    "title": video_title,
                    "url": youtube_url
                }]
                # Generate Wikipedia link for the exact topic searched (use original topic name)
                wiki_topic = topic_for_wikipedia.replace(' ', '_')
                # Remove any special characters that might cause issues, but keep underscores and hyphens
                wiki_topic = ''.join(c if c.isalnum() or c in ['_', '-'] else '' for c in wiki_topic)
                # Ensure it's a direct Wikipedia page link, not a search
                wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic}"
                print(f"[DEBUG] Generated Wikipedia URL (fallback): {wiki_url} for topic: {topic_for_wikipedia}")
                website_references = [
                    {"title": f"{topic_for_wikipedia} - Wikipedia", "url": wiki_url}
                ]
        else:
            # Fallback without LLM: Get 2nd video from YouTube search
            try:
                import requests
                import re
                search_query = f"{topic_for_resources} tutorial"
                search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}&sp=EgIQAQ%3D%3D"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(search_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    video_ids = re.findall(r'"videoId":"([^"]{11})"', response.text)
                    if len(video_ids) >= 2:
                        video_id = video_ids[1]
                        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                        video_title = f"{topic_for_resources} - Tutorial"
                        print(f"[DEBUG] No LLM: Found 2nd video ID: {video_id}")
                    else:
                        youtube_url = search_url
                        video_title = f"{topic_for_resources} - Complete Tutorial"
                else:
                    youtube_url = search_url
                    video_title = f"{topic_for_resources} - Complete Tutorial"
            except Exception as e:
                print(f"[DEBUG] No LLM error: {e}")
                search_query_encoded = f"{topic_for_resources} tutorial".replace(' ', '+')
                youtube_url = f"https://www.youtube.com/results?search_query={search_query_encoded}&sp=EgIQAQ%3D%3D"
                video_title = f"{topic_for_resources} - Complete Tutorial"
            
            youtube_links = [{
                "title": video_title,
                "url": youtube_url
            }]
            # Generate Wikipedia link for the exact topic searched (use original topic name)
            wiki_topic = topic_for_wikipedia.replace(' ', '_')
            # Remove any special characters that might cause issues, but keep underscores and hyphens
            wiki_topic = ''.join(c if c.isalnum() or c in ['_', '-'] else '' for c in wiki_topic)
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic}"
            website_references = [
                {"title": f"{topic_for_wikipedia} - Wikipedia", "url": wiki_url}
            ]
        
        # Ensure only one YouTube video link
        youtube_links = youtube_links[:1]
        
        # Final validation: Ensure website_references only contains Wikipedia URLs
        # Remove any non-Wikipedia URLs and ensure we have at least one Wikipedia link
        validated_website_references = []
        for ref in website_references:
            url = ref.get('url', '')
            # Only keep Wikipedia URLs
            if 'wikipedia.org/wiki' in url.lower() and 'google.com' not in url.lower():
                validated_website_references.append(ref)
        
        # If no valid Wikipedia URLs, generate one from the topic
        if not validated_website_references:
            wiki_topic = topic_for_wikipedia.replace(' ', '_')
            wiki_topic = ''.join(c if c.isalnum() or c in ['_', '-'] else '' for c in wiki_topic)
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_topic}"
            validated_website_references = [{
                "title": f"{topic_for_wikipedia} - Wikipedia",
                "url": wiki_url
            }]
            print(f"[DEBUG] Generated Wikipedia URL (final validation): {wiki_url} for topic: {topic_for_wikipedia}")
        
        # Ensure only one Wikipedia link
        website_references = validated_website_references[:1]
        
        # Calculate completeness and confidence scores
        completeness = min(len(explanation) / 500, 1.0)  # Normalize to 0-1
        confidence = 0.9 if self.llm else 0.6  # Higher confidence with LLM
        
        print(f"[DEBUG] Final website_references being returned: {website_references}")
        
        return {
            "topic": base_topic,
            "explanation": explanation,
            "youtube_links": youtube_links,
            "website_references": website_references,
            "completeness_score": round(completeness, 2),
            "confidence_score": round(confidence, 2)
        }
    
    def _generate_explanation_from_data(self, topic: str) -> str:
        """Generate explanation using dataset information when LLM is not available"""
        # Try to get information from dataset
        dataset_results = self.data_service.search(topic, limit=1)
        
        paragraphs = []
        
        if dataset_results and len(dataset_results) > 0:
            # Use actual data from dataset
            data = dataset_results[0]
            description = data.get("description", "")
            key_concepts = data.get("key_concepts", [])
            tags = data.get("tags", [])
            
            # Paragraph 1: Expand description from dataset with more detail
            if description and len(description) > 50:
                # Expand the description into a full paragraph
                paragraphs.append(
                    f"{description}. "
                    f"{topic} is a fundamental area of study that plays a crucial role in modern technology and education. "
                    f"It encompasses a comprehensive range of concepts, principles, and practical applications that are essential for understanding contemporary systems and methodologies. "
                    f"Students learning {topic} will gain valuable knowledge and skills that can be applied across various domains and industries. "
                    f"The study of {topic} combines theoretical understanding with hands-on practice, making it both intellectually engaging and practically relevant."
                )
            else:
                paragraphs.append(
                    f"{topic} is an important subject in modern education and technology. "
                    f"It encompasses a wide range of concepts and practical applications that are essential for understanding contemporary systems and methodologies. "
                    f"This field combines theoretical knowledge with practical skills, making it valuable for students and professionals alike. "
                    f"Understanding {topic} opens up numerous opportunities for learning, problem-solving, and career advancement."
                )
            
            # Paragraph 2: Key concepts from dataset - expanded
            if key_concepts and len(key_concepts) > 0:
                concepts_text = ", ".join(key_concepts[:5])  # Use first 5 concepts
                concepts_list = ", ".join(key_concepts[:3])  # First 3 for detailed mention
                paragraphs.append(
                    f"The core concepts of {topic} include {concepts_text}. "
                    f"These fundamental principles form the foundation of understanding {topic} and are essential for mastering this subject. "
                    f"Specifically, {concepts_list} are among the most important concepts that students must understand thoroughly. "
                    f"Each concept builds upon the others, creating a comprehensive framework for learning and application. "
                    f"Mastering these key concepts enables students to grasp more advanced topics and apply their knowledge effectively in real-world scenarios. "
                    f"The interconnected nature of these concepts means that understanding one often helps in understanding the others."
                )
            else:
                paragraphs.append(
                    f"The study of {topic} involves understanding fundamental principles, core methodologies, and practical applications. "
                    f"These concepts are interconnected and build upon each other to create a comprehensive understanding of the subject."
                )
            
            # Paragraph 3: Applications and importance - expanded
            category = data.get("category", "").lower()
            if "programming" in category or "code" in category:
                paragraphs.append(
                    f"{topic} has extensive applications in software development, web development, data analysis, automation, and system design. "
                    f"Programmers and developers use {topic} to build applications, solve computational problems, and create innovative solutions. "
                    f"In the technology industry, expertise in {topic} is highly valued and opens up numerous career opportunities. "
                    f"The practical applications range from building simple scripts to developing complex enterprise systems. "
                    f"Understanding {topic} is essential for anyone pursuing a career in software development or computer science."
                )
            elif "ai" in category or "machine learning" in category.lower():
                paragraphs.append(
                    f"{topic} finds applications in artificial intelligence, data science, predictive analytics, and intelligent systems. "
                    f"It is used in developing machine learning models, natural language processing systems, computer vision applications, and recommendation engines. "
                    f"Industries such as healthcare, finance, e-commerce, and technology heavily rely on {topic} for innovation and problem-solving. "
                    f"The applications continue to expand as new AI technologies emerge and become more accessible."
                )
            else:
                paragraphs.append(
                    f"{topic} has numerous applications across various industries and fields. "
                    f"It is used in technology development, research, education, and many other domains. "
                    f"The practical applications of {topic} demonstrate its importance and relevance in today's world. "
                    f"Mastering {topic} opens up opportunities for problem-solving, innovation, and career advancement."
                )
            
            # Paragraph 4: Learning path and future
            paragraphs.append(
                f"Learning {topic} is a rewarding journey that begins with understanding the fundamentals and gradually progresses to more advanced concepts. "
                f"Students should start with the basics, practice regularly, and work on projects to reinforce their understanding. "
                f"The field of {topic} continues to evolve, with new developments and best practices emerging regularly. "
                f"Staying updated with the latest trends and technologies in {topic} is important for both students and professionals. "
                f"The future of {topic} looks promising, with increasing demand for expertise in this area across various sectors."
            )
        else:
            # No dataset information - create topic-specific explanation based on topic name
            topic_lower = topic.lower()
            
            # Paragraph 1: Topic-specific definition
            if "python" in topic_lower or "basics" in topic_lower:
                paragraphs.append(
                    "Python is a high-level, interpreted programming language known for its simplicity and readability. "
                    "Created by Guido van Rossum and first released in 1991, Python emphasizes code readability and allows programmers to express concepts in fewer lines of code than would be possible in languages such as C++ or Java. "
                    "Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. "
                    "It has a large standard library and a vast ecosystem of third-party packages, making it one of the most popular programming languages today. "
                    "Python is widely used in web development, data science, artificial intelligence, scientific computing, and automation."
                )
            elif "machine learning" in topic_lower or "ml" in topic_lower:
                paragraphs.append(
                    "Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. "
                    "It uses algorithms to analyze data, identify patterns, and make predictions or decisions based on that data. "
                    "Machine learning algorithms build mathematical models based on training data to make predictions or decisions. "
                    "There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. "
                    "Machine learning is used in various applications including image recognition, natural language processing, recommendation systems, and autonomous vehicles."
                )
            elif "data structure" in topic_lower:
                paragraphs.append(
                    "Data structures are ways of organizing and storing data in a computer so that it can be accessed and modified efficiently. "
                    "Different data structures are suited to different kinds of applications, and some are highly specialized to specific tasks. "
                    "Common data structures include arrays, linked lists, stacks, queues, trees, graphs, and hash tables. "
                    "Understanding data structures is fundamental to computer science and programming, as they determine how efficiently algorithms can process data. "
                    "The choice of appropriate data structure can significantly impact the performance of a program."
                )
            elif "algorithm" in topic_lower:
                paragraphs.append(
                    "An algorithm is a step-by-step procedure for solving a problem or accomplishing a task. "
                    "Algorithms are fundamental to computer science and are used to process data, perform calculations, and automate reasoning. "
                    "They can be expressed in natural language, pseudocode, or programming languages. "
                    "Key aspects of algorithms include correctness, efficiency, and clarity. "
                    "Common algorithm categories include sorting, searching, graph algorithms, dynamic programming, and greedy algorithms."
                )
            elif "neural network" in topic_lower:
                paragraphs.append(
                    "Neural networks are computing systems inspired by biological neural networks that constitute animal brains. "
                    "They are composed of interconnected nodes (neurons) that process information through weighted connections. "
                    "Neural networks learn by adjusting these weights based on training data, enabling them to recognize patterns and make predictions. "
                    "They are a key technology in deep learning and are used for tasks such as image recognition, natural language processing, and game playing. "
                    "Common types include feedforward neural networks, convolutional neural networks (CNNs), and recurrent neural networks (RNNs)."
                )
            elif "natural language processing" in topic_lower or "nlp" in topic_lower:
                paragraphs.append(
                    "Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. "
                    "NLP combines computational linguistics with machine learning, deep learning, and statistical models to process and analyze large amounts of natural language data. "
                    "Applications of NLP include machine translation, sentiment analysis, chatbots, speech recognition, and text summarization. "
                    "NLP enables computers to read text, hear speech, interpret it, measure sentiment, and determine which parts are important. "
                    "Modern NLP systems use neural networks and transformer architectures to achieve state-of-the-art performance."
                )
            else:
                # Generic but more informative fallback
                paragraphs.append(
                    f"{topic} is a significant area of study that combines theoretical knowledge with practical applications. "
                    f"It involves understanding fundamental concepts, principles, and methodologies that are essential in this field. "
                    f"Students learning {topic} will gain valuable skills and knowledge that can be applied in various professional and academic contexts."
                )
            
            # Paragraph 2: Core concepts (topic-specific)
            if "python" in topic_lower:
                paragraphs.append(
                    "Python's core concepts include variables and data types (integers, floats, strings, lists, dictionaries), control flow (if statements, loops), functions, classes and object-oriented programming, modules and packages, exception handling, and file operations. "
                    "Python's dynamic typing and automatic memory management make it beginner-friendly, while its powerful features support advanced programming. "
                    "The language's syntax is clean and readable, using indentation to define code blocks rather than braces or keywords."
                )
            elif "machine learning" in topic_lower:
                paragraphs.append(
                    "Core concepts in machine learning include training and testing data, features and labels, models and algorithms, overfitting and underfitting, cross-validation, feature engineering, and model evaluation metrics. "
                    "Understanding these concepts is crucial for building effective machine learning systems. "
                    "The field also involves understanding different algorithm types such as linear regression, decision trees, neural networks, and clustering algorithms."
                )
            else:
                paragraphs.append(
                    f"The core concepts of {topic} include fundamental principles that form the foundation of this field. "
                    f"These concepts are interconnected and build upon each other, creating a comprehensive framework for understanding. "
                    f"Mastering these core concepts is essential for anyone looking to develop expertise in this area."
                )
            
            # Paragraph 3: Applications
            paragraphs.append(
                f"{topic} finds applications in numerous real-world scenarios across various industries. "
                f"In technology, it's used for developing software, systems, and solutions. "
                f"In research, it enables new discoveries and innovations. "
                f"In education, it helps students learn and understand complex concepts. "
                f"The practical applications of {topic} continue to evolve as new technologies and methodologies emerge."
            )
            
            # Paragraph 4: Importance
            paragraphs.append(
                f"The importance of {topic} in today's world cannot be overstated. "
                f"As technology and knowledge continue to advance, expertise in {topic} becomes increasingly valuable. "
                f"Learning {topic} not only enhances problem-solving abilities but also opens up numerous career opportunities. "
                f"Students and professionals who master {topic} will find themselves well-equipped to tackle challenges and contribute meaningfully to their fields."
            )
        
        # Join paragraphs with double newlines
        return '\n\n'.join(paragraphs)
    
    def generate_quiz(self, topic: str, num_questions: int, difficulty: str, marks_per_question: int) -> Dict:
        """Generate quiz questions using AI - generates 2x questions for selection"""
        questions = []
        # Generate 2x the requested questions so user can select
        questions_to_generate = num_questions * 2
        
        # Use LLM to generate real questions if available
        if self.llm:
            try:
                # Better prompt for diverse, real questions
                prompt = f"""You are an expert educator creating a quiz about {topic} at {difficulty} difficulty level.



Generate exactly {questions_to_generate} diverse, educational quiz questions about {topic}. Each question should:

1. Be unique and different from others

2. Test actual understanding of {topic}

3. Be appropriate for {difficulty} level

4. Cover different aspects: concepts, applications, principles, examples, comparisons

5. End with a question mark



Format: Write each question on a new line, numbered 1-{questions_to_generate}. Do NOT use phrases like "Sample question" or generic templates.

Make each question specific, detailed, and educational.



Example format:

1. What is the primary purpose of [specific concept] in {topic}?

2. How does [specific method] differ from [another method] in {topic}?

3. Explain the role of [specific component] in {topic}.



Now generate {questions_to_generate} unique questions about {topic}:"""
                
                response = self.llm.invoke(prompt)
                ai_content = response.content
                
                # Better parsing - handle various formats
                lines = ai_content.split('\n')
                question_num = 1
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Remove numbering patterns (1., 1), Q1, Question 1, etc.)
                    # Remove leading numbers, dots, dashes, Q, Question prefixes
                    cleaned = re.sub(r'^(\d+[\.\)\-\s]+|Q\d+[\.\)\-\s:]+|Question\s+\d+[\.\)\-\s:]+)', '', line, flags=re.IGNORECASE)
                    cleaned = cleaned.strip()
                    
                    # Must contain a question mark and be substantial
                    if '?' in cleaned and len(cleaned) > 20:
                        # Remove any remaining prefixes
                        if cleaned.startswith(':'):
                            cleaned = cleaned[1:].strip()
                        
                        questions.append({
                            "id": question_num,
                            "question": cleaned,
                            "type": "short_answer",
                            "marks": marks_per_question
                        })
                        question_num += 1
                        
                        if question_num > questions_to_generate:
                            break
                
                # If we got some questions but not enough, that's okay - we'll use what we have
                if len(questions) == 0:
                    raise Exception("No questions parsed from LLM response")
                    
            except Exception as e:
                print(f"Error generating quiz with AI: {e}")
                # Fallback to diverse template questions
                questions = self._generate_fallback_questions(topic, difficulty, questions_to_generate, marks_per_question)
        else:
            # No LLM available - use diverse fallback questions
            questions = self._generate_fallback_questions(topic, difficulty, questions_to_generate, marks_per_question)


        # Ensure we have at least the requested number
        if len(questions) < num_questions:
            additional = self._generate_fallback_questions(topic, difficulty, num_questions - len(questions), marks_per_question, start_id=len(questions) + 1)
            questions.extend(additional)
        
        return {
            "quiz_id": f"quiz_{datetime.now().timestamp()}",
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "total_marks": len(questions) * marks_per_question,
            "completeness_score": round(min(len(questions) / questions_to_generate, 1.0), 2),
            "confidence_score": round(0.9 if self.llm else 0.7, 2)
        }
    
    def generate_quiz_from_pdf(self, pdf_text: str, num_questions: int, difficulty: str, marks_per_question: int) -> Dict:
        """Generate quiz questions from PDF content"""
        questions = []
        # Generate 2x the requested questions so user can select
        questions_to_generate = num_questions * 2
        
        # Limit PDF text to avoid token limits (keep first 10000 characters)
        pdf_text_limited = pdf_text[:10000] if len(pdf_text) > 10000 else pdf_text
        
        # Use LLM to generate questions from PDF content if available
        if self.llm:
            try:
                prompt = f"""You are an expert educator creating a quiz based on the following document content at {difficulty} difficulty level.

Document Content:
{pdf_text_limited}

Generate exactly {questions_to_generate} diverse, educational quiz questions based on the content above. Each question should:

1. Be directly related to the content in the document
2. Test understanding of key concepts, facts, or information from the document
3. Be appropriate for {difficulty} level
4. Cover different aspects: concepts, applications, principles, examples, comparisons
5. End with a question mark
6. Be answerable based on the provided document content

Format: Write each question on a new line, numbered 1-{questions_to_generate}. Do NOT use phrases like "Sample question" or generic templates.

Make each question specific to the document content and educational.

Now generate {questions_to_generate} unique questions based on the document:"""
                
                response = self.llm.invoke(prompt)
                ai_content = response.content
                
                # Parse questions (same logic as generate_quiz)
                lines = ai_content.split('\n')
                question_num = 1
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Remove numbering patterns
                    cleaned = re.sub(r'^(\d+[\.\)\-\s]+|Q\d+[\.\)\-\s:]+|Question\s+\d+[\.\)\-\s:]+)', '', line, flags=re.IGNORECASE)
                    cleaned = cleaned.strip()
                    
                    # Must contain a question mark and be substantial
                    if '?' in cleaned and len(cleaned) > 20:
                        if cleaned.startswith(':'):
                            cleaned = cleaned[1:].strip()
                        
                        questions.append({
                            "id": question_num,
                            "question": cleaned,
                            "type": "short_answer",
                            "marks": marks_per_question
                        })
                        question_num += 1
                        
                        if question_num > questions_to_generate:
                            break
                
                if len(questions) == 0:
                    raise Exception("No questions parsed from LLM response")
                    
            except Exception as e:
                print(f"Error generating quiz from PDF with AI: {e}")
                # Fallback: generate questions based on key terms from PDF
                questions = self._generate_questions_from_text(pdf_text, difficulty, questions_to_generate, marks_per_question)
        else:
            # No LLM available - generate from PDF text
            questions = self._generate_questions_from_text(pdf_text, difficulty, questions_to_generate, marks_per_question)

        # Ensure we have at least the requested number
        if len(questions) < num_questions:
            additional = self._generate_questions_from_text(pdf_text, difficulty, num_questions - len(questions), marks_per_question, start_id=len(questions) + 1)
            questions.extend(additional)
        
        return {
            "quiz_id": f"quiz_pdf_{datetime.now().timestamp()}",
            "topic": "PDF Document",
            "difficulty": difficulty,
            "questions": questions,
            "total_marks": len(questions) * marks_per_question,
            "completeness_score": round(min(len(questions) / questions_to_generate, 1.0), 2),
            "confidence_score": round(0.9 if self.llm else 0.7, 2)
        }
    
    def _generate_questions_from_text(self, text: str, difficulty: str, num_questions: int, marks_per_question: int, start_id: int = 1) -> List[Dict]:
        """Generate questions from text content when LLM is not available"""
        questions = []
        # Extract sentences and key phrases
        sentences = re.split(r'[.!?]\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Generate questions based on sentences
        for i, sentence in enumerate(sentences[:num_questions * 2]):
            if i >= num_questions:
                break
            
            # Create question from sentence
            if difficulty.lower() == "beginner":
                question = f"According to the document, {sentence.lower()} Explain this concept."
            elif difficulty.lower() == "intermediate":
                question = f"Based on the document content, explain: {sentence}"
            else:  # Advanced
                question = f"Analyze and discuss: {sentence}"
            
            questions.append({
                "id": start_id + i,
                "question": question + "?",
                "type": "short_answer",
                "marks": marks_per_question
            })
        
        # If we need more questions, use generic templates
        if len(questions) < num_questions:
            remaining = num_questions - len(questions)
            templates = [
                "What are the main topics discussed in this document?",
                "Summarize the key points from the document.",
                "What important information is presented?",
                "Explain the primary concepts covered.",
                "What are the main conclusions?",
                "Describe the key ideas presented.",
                "What are the important details mentioned?",
                "Explain the main themes of the document."
            ]
            for i in range(remaining):
                questions.append({
                    "id": start_id + len(questions) + i,
                    "question": templates[i % len(templates)],
                    "type": "short_answer",
                    "marks": marks_per_question
                })
        
        return questions[:num_questions]
    
    def _generate_fallback_questions(self, topic: str, difficulty: str, num_questions: int, marks_per_question: int, start_id: int = 1) -> List[Dict]:
        """Generate diverse fallback questions when LLM is not available"""
        # More diverse question templates based on difficulty
        if difficulty.lower() == "beginner":
            templates = [
                f"What is {topic} and why is it important?",
                f"Name three basic concepts related to {topic}.",
                f"Explain in simple terms what {topic} does.",
                f"What are the fundamental components of {topic}?",
                f"How would you describe {topic} to someone new to the field?",
                f"What is the primary purpose of {topic}?",
                f"Give an example of how {topic} is used in practice.",
                f"What skills are needed to understand {topic}?",
                f"What makes {topic} different from similar concepts?",
                f"What are the first steps to learning {topic}?",
                f"What problems does {topic} solve?",
                f"What are common misconceptions about {topic}?",
                f"How does {topic} relate to everyday applications?",
                f"What background knowledge is helpful for understanding {topic}?",
                f"What are the key terms associated with {topic}?"
            ]
        elif difficulty.lower() == "intermediate":
            templates = [
                f"Explain the core principles that govern {topic}.",
                f"How does {topic} differ from related approaches?",
                f"What are the main challenges when working with {topic}?",
                f"Describe the relationship between different aspects of {topic}.",
                f"What are the advantages and limitations of {topic}?",
                f"How would you implement {topic} in a real-world scenario?",
                f"What are the key factors that influence {topic}?",
                f"Compare and contrast {topic} with alternative methods.",
                f"What are the best practices for using {topic}?",
                f"Explain how {topic} has evolved over time.",
                f"What are the critical components of a successful {topic} implementation?",
                f"How do different variations of {topic} compare?",
                f"What role does {topic} play in modern applications?",
                f"What are the performance considerations for {topic}?",
                f"How would you troubleshoot common issues with {topic}?"
            ]
        else:  # Advanced
            templates = [
                f"Analyze the theoretical foundations of {topic}.",
                f"What are the advanced techniques and optimizations in {topic}?",
                f"Explain the mathematical or algorithmic principles behind {topic}.",
                f"How would you design a complex system using {topic}?",
                f"What are the cutting-edge developments in {topic}?",
                f"Critically evaluate the strengths and weaknesses of {topic}.",
                f"How does {topic} integrate with other advanced concepts?",
                f"What are the research directions in {topic}?",
                f"Explain the scalability and performance implications of {topic}.",
                f"How would you optimize {topic} for production environments?",
                f"What are the architectural considerations for {topic}?",
                f"Discuss the trade-offs in different {topic} approaches.",
                f"What are the security and reliability aspects of {topic}?",
                f"How does {topic} relate to emerging technologies?",
                f"What are the future prospects and challenges for {topic}?"
            ]
        
        questions = []
        for i in range(num_questions):
            template_idx = (i + start_id - 1) % len(templates)
            questions.append({
                "id": start_id + i,
                "question": templates[template_idx],
                "type": "short_answer",
                "marks": marks_per_question
            })
        
        return questions
    
    def chat(self, message: str, user_id: str) -> Dict:
        """Chat with agent using memory and context"""
        # Get context from memory (recent conversation history) - returns list of dicts
        context = self.memory.get_memory(user_id, limit=5)
        
        # Try to get relevant information from dataset first
        dataset_info = None
        try:
            search_results = self.data_service.search(message, limit=1)
            if search_results:
                dataset_info = search_results[0]
        except:
            pass
        
        # Build conversation context string
        context_str = ""
        if context:
            context_str = "\n\nRecent conversation history:\n"
            for conv in context[-3:]:  # Use last 3 conversations for context
                context_str += f"Student: {conv.get('user_message', '')}\n"
                context_str += f"Assistant: {conv.get('ai_response', '')}\n"
        
        # Build enhanced prompt with dataset information if available
        if self.llm:
            try:
                print(f"[DEBUG] Chat - User message: {message}")
                print(f"[DEBUG] Chat - LLM is available, using LLM for response")
                print(f"[DEBUG] Chat - Using LLM with context: {len(context)} previous messages")
                if dataset_info:
                    print(f"[DEBUG] Chat - Found relevant topic in dataset: {dataset_info.get('topic', '')}")
                else:
                    print(f"[DEBUG] Chat - No relevant topic found in dataset for: {message}")
                
                # Create a more natural, conversational prompt
                prompt_parts = []
                
                # System instruction - more direct and focused
                prompt_parts.append("""You are an expert AI educational assistant. Answer the student's question directly and comprehensively.

IMPORTANT INSTRUCTIONS:
1. Provide a direct, accurate answer to the question asked
2. Give detailed explanations (at least 4-6 sentences)
3. Use clear, simple language that students can understand
4. Include examples and real-world applications when relevant
5. Be specific and factual - avoid generic responses
6. If you don't know something, say so honestly
7. Focus on AI, machine learning, deep learning, and related technical topics

DO NOT:
- Give generic responses like "This is an interesting topic"
- Ask the student to provide more details if the question is clear
- Redirect to other topics unnecessarily
- Use placeholder text or incomplete answers""")
                
                # Add dataset information if available
                if dataset_info:
                    topic_name = dataset_info.get('topic', '')
                    description = dataset_info.get('description', '')
                    key_concepts = dataset_info.get('key_concepts', [])
                    tags = dataset_info.get('tags', [])
                    
                    prompt_parts.append(f"\n\nRelevant information from knowledge base:\nTopic: {topic_name}\nDescription: {description}")
                    if key_concepts:
                        prompt_parts.append(f"Key concepts: {', '.join(key_concepts[:5])}")
                    if tags:
                        prompt_parts.append(f"Related topics: {', '.join(tags[:3])}")
                    prompt_parts.append("\nUse this information to provide accurate and detailed answers.")
                
                # Add conversation context
                if context_str:
                    prompt_parts.append(context_str)
                
                # Add current question
                prompt_parts.append(f"\n\nStudent's current question: {message}")
                prompt_parts.append("\nProvide a helpful, detailed, and educational response:")
                
                full_prompt = "\n".join(prompt_parts)
                
                # Invoke LLM with better error handling
                print(f"[DEBUG] Chat - Full prompt length: {len(full_prompt)} characters")
                print(f"[DEBUG] Chat - Prompt preview: {full_prompt[:300]}...")
                
                response = self.llm.invoke(full_prompt)
                ai_response = response.content.strip()
                
                print(f"[DEBUG] Chat - Raw LLM response (first 300 chars): {ai_response[:300]}...")
                
                # Clean up response
                if ai_response:
                    # Remove any system-like prefixes
                    prefixes_to_remove = ["Assistant:", "AI:", "Response:", "Answer:", "Here's", "Here is"]
                    for prefix in prefixes_to_remove:
                        if ai_response.startswith(prefix):
                            ai_response = ai_response[len(prefix):].strip()
                            # Remove leading colon if present
                            if ai_response.startswith(":"):
                                ai_response = ai_response[1:].strip()
                    
                    # Remove quotes if the entire response is quoted
                    if (ai_response.startswith('"') and ai_response.endswith('"')) or \
                       (ai_response.startswith("'") and ai_response.endswith("'")):
                        ai_response = ai_response[1:-1].strip()
                    
                    # Ensure it starts with a proper sentence
                    if ai_response and not ai_response[0].isupper():
                        # Try to find first sentence
                        sentences = ai_response.split('.')
                        if len(sentences) > 1:
                            ai_response = '. '.join(sentences[1:]).strip()
                        elif len(sentences) == 1 and len(ai_response) > 1:
                            # If only one sentence, capitalize first letter
                            ai_response = ai_response[0].upper() + ai_response[1:]
                
                # Ensure response is meaningful (at least 30 characters)
                if not ai_response or len(ai_response) < 30:
                    print(f"[DEBUG] Chat - Response too short ({len(ai_response) if ai_response else 0} chars), raising exception")
                    raise Exception(f"LLM returned empty or too short response ({len(ai_response) if ai_response else 0} characters)")
                
                print(f"[DEBUG] Chat - Final LLM response length: {len(ai_response)} characters")
                
            except Exception as e:
                print(f"[DEBUG] Chat - LLM error: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback: Use dataset information to generate a better response
                if dataset_info:
                    topic_name = dataset_info.get('topic', '')
                    description = dataset_info.get('description', '')
                    key_concepts = dataset_info.get('key_concepts', [])
                    category = dataset_info.get('category', '')
                    
                    # Build a comprehensive response from dataset
                    response_parts = []
                    
                    if description:
                        response_parts.append(description)
                    else:
                        response_parts.append(f"{topic_name} is an important topic in AI and machine learning.")
                    
                    if key_concepts:
                        concepts_str = ', '.join(key_concepts[:5])
                        response_parts.append(f"\n\nKey concepts include: {concepts_str}.")
                    
                    if category:
                        response_parts.append(f"\n\nThis topic falls under the category of {category}.")
                    
                    response_parts.append(f"\n\nWould you like me to explain any specific aspect of {topic_name} in more detail?")
                    
                    ai_response = ''.join(response_parts)
                else:
                    # Try to use reasoning service for better fallback
                    try:
                        # Use reasoning service to generate a better response
                        reasoning_response = self.reasoning.explain_with_llm(message)
                        if reasoning_response and len(reasoning_response) > 50:
                            ai_response = reasoning_response
                        else:
                            # Last resort: helpful generic response
                            ai_response = f"I understand you're asking about: {message}. This is an important topic in AI and machine learning. Let me provide you with a helpful explanation.\n\n{message} is a fundamental concept that plays a crucial role in modern technology and education. It encompasses various principles, methodologies, and applications that are essential for understanding contemporary systems. Understanding {message} requires a solid foundation in its core concepts and the ability to apply theoretical knowledge to practical scenarios.\n\nWould you like me to explain any specific aspect of {message} in more detail?"
                    except:
                        # Final fallback
                        ai_response = f"I understand you're asking about: {message}. This is an important topic in AI and machine learning. I'd be happy to help you understand this better. Could you provide more specific details about what aspect you'd like to learn about?"
        else:
            # No LLM available - use data service and reasoning
            print(f"[DEBUG] Chat - LLM not available, using fallback methods")
            if dataset_info:
                topic_name = dataset_info.get('topic', '')
                description = dataset_info.get('description', '')
                key_concepts = dataset_info.get('key_concepts', [])
                category = dataset_info.get('category', '')
                
                # Build comprehensive response from dataset
                response_parts = []
                if description:
                    response_parts.append(description)
                else:
                    response_parts.append(f"{topic_name} is an important topic in AI and machine learning.")
                
                if key_concepts:
                    concepts_str = ', '.join(key_concepts[:5])
                    response_parts.append(f"\n\nKey concepts include: {concepts_str}.")
                
                if category:
                    response_parts.append(f"\n\nThis topic falls under the category of {category}.")
                
                response_parts.append(f"\n\nWould you like me to explain any specific aspect of {topic_name} in more detail?")
                ai_response = ''.join(response_parts)
            else:
                # Try reasoning service for better fallback
                try:
                    reasoning_response = self.reasoning.explain_with_llm(message)
                    if reasoning_response and len(reasoning_response) > 50:
                        # Use first paragraph from reasoning service
                        paragraphs = reasoning_response.split('\n\n')
                        if paragraphs:
                            ai_response = paragraphs[0]  # Use first paragraph
                            if len(ai_response) < 100:
                                # If too short, use more
                                ai_response = '\n\n'.join(paragraphs[:2])
                        else:
                            ai_response = reasoning_response
                    else:
                        # Last resort: helpful response
                        ai_response = f"I understand you're asking about: {message}. This is an important topic in AI and machine learning. {message} is a fundamental concept that plays a crucial role in modern technology and education. It encompasses various principles, methodologies, and applications that are essential for understanding contemporary systems.\n\nWould you like me to explain any specific aspect of {message} in more detail?"
                except:
                    ai_response = f"I understand you're asking about: {message}. This is an important topic in AI and machine learning. I'd be happy to help you understand this better. Could you provide more specific details about what aspect you'd like to learn about?"
        
        # Store in memory
        self.memory.store_conversation(user_id, message, ai_response)
        
        return {
            "message": ai_response,
            "action": "general_response",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory(self, user_id: str, limit: int) -> Dict:
        """Get conversation memory"""
        conversations = self.memory.get_memory(user_id, limit)
        return {
            "user_id": user_id,
            "conversations": conversations,
            "total_count": len(conversations)
        }
    
    def query(self, query_type: str, query: str, limit: int, filters: Dict = None) -> Dict:
        """Query data (search, filter, categorize) - Uses multiple data sources"""
        results = []
        source_used = "dataset"
        
        # Use data service for dataset operations (JSON/CSV)
        if query_type == "search":
            results = self.data_service.search(query, limit)
            source_used = "JSON/CSV dataset"
        elif query_type == "filter":
            filter_dict = filters or {}
            results = self.data_service.filter(filter_dict, limit)
            source_used = "JSON/CSV dataset"
        elif query_type == "categorize":
            categorized = self.data_service.categorize(limit)
            results = [{"category": k, "items": v, "count": len(v)} for k, v in categorized.items()]
            source_used = "JSON/CSV dataset"
        elif query_type == "database_search":
            # Also support querying from database
            conn = get_db_connection(self.db_path)
            cursor = conn.execute(
                "SELECT * FROM topic_queries WHERE topic_name LIKE ? LIMIT ?",
                (f"%{query}%", limit)
            )
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            source_used = "SQLite database"
        else:
            results = []
        
        # Log query
        conn = get_db_connection(self.db_path)
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)""",
            ("query", f"{query_type} from {source_used}", f"Found {len(results)} results", 0.8, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        return {
            "query_type": query_type,
            "query": query,
            "results": results,
            "count": len(results),
            "data_source": source_used
        }
    
    def summarize(self, content: str) -> Dict:
        """Summarize content"""
        summary = self.reasoning.summarize(content)
        
        # Log decision
        conn = get_db_connection(self.db_path)
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)""",
            ("summarization", content[:100], summary[:200], 0.85, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        # Calculate completeness and confidence scores
        completeness = min(len(summary) / max(len(content) * 0.3, 1), 1.0)
        confidence = 0.85
        
        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "completeness_score": round(completeness, 2),
            "confidence_score": round(confidence, 2)
        }
    
    def classify(self, content: str, categories: List[str]) -> Dict:
        """Classify content"""
        result = self.reasoning.classify(content, categories)
        
        # Log decision
        conn = get_db_connection(self.db_path)
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)""",
            ("classification", content[:100], result["category"], result.get("confidence", 0.8),
             datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        # Add completeness score
        result["completeness_score"] = round(1.0 if result.get("category") else 0.0, 2)
        
        return result
    
    def evaluate_quiz(self, quiz_id: str, answers: Dict, questions: List[Dict] = None,
                      topic: str = None, difficulty: str = None, marks_per_question: int = 10,
                      user_id: str = "default", time_taken_seconds: int = 0) -> Dict:
        """Evaluate quiz answers - gives 0 marks for wrong or unanswered questions"""
        feedback = []
        correct_count = 0
        total_marks = 0
        obtained_marks = 0
        
        # If questions provided, use them; otherwise assume all questions have same marks
        if questions:
            question_dict = {q.get("id"): q for q in questions}
        else:
            question_dict = {}

        # Convert answer keys to integers if they're strings
        normalized_answers = {}
        for q_id, answer in answers.items():
            try:
                # Convert string key to int if possible
                int_key = int(q_id) if isinstance(q_id, str) else q_id
                normalized_answers[int_key] = answer
            except (ValueError, TypeError):
                # Keep original key if conversion fails
                normalized_answers[q_id] = answer

        # Use normalized answers for the rest of the function
        answers = normalized_answers

        # Debug: Print received data
        print(f"[DEBUG] Evaluating quiz: quiz_id={quiz_id}, topic={topic}")
        print(f"[DEBUG] Received {len(answers)} answers")
        print(f"[DEBUG] Received {len(questions) if questions else 0} questions")
        print(f"[DEBUG] Question IDs in questions: {[q.get('id') for q in (questions or [])]}")
        print(f"[DEBUG] Answer IDs: {list(answers.keys())}")
        
        # Evaluate each answer
        for q_id, answer in answers.items():
            # Get question details
            question = question_dict.get(q_id, {})
            question_marks = question.get("marks", marks_per_question)
            question_text = question.get("question", f"Question {q_id}")
            
            print(f"[DEBUG] Evaluating Q{q_id}: answer_length={len(str(answer))}, question_text={question_text[:50]}...")
            
            total_marks += question_marks
            
            # Check if answer is provided
            if not answer or answer.strip() == "":
                # No answer provided - 0 marks
                feedback.append({
                    "question_id": q_id,
                    "question": question_text,
                    "answer": "",
                    "correct": False,
                    "marks_awarded": 0,
                    "max_marks": question_marks,
                    "feedback": "No answer provided - 0 marks"
                })
                continue
            
            # Answer provided - evaluate using AI if available
            answer_trimmed = answer.strip()
            is_correct = False
            marks_awarded = 0
            evaluation_feedback = ""
            
            if self.llm:
                try:
                    # Use LLM to evaluate the answer - be more lenient and award partial marks
                    evaluation_prompt = f"""You are evaluating a quiz answer. Award marks based on correctness and completeness.

Question: {question_text}
Student Answer: {answer_trimmed}
Maximum Marks: {question_marks}

Evaluate the answer and award marks (0 to {question_marks}):
- Full marks ({question_marks}): Answer is correct and demonstrates good understanding
- Partial marks (1 to {question_marks-1}): Answer is partially correct or shows some understanding
- Zero marks (0): Answer is completely wrong or irrelevant

IMPORTANT: Be fair and generous. If the answer shows understanding of the topic, award marks even if not perfect.

Format your response EXACTLY as:
Marks: [number between 0 and {question_marks}]
Feedback: [brief explanation of why these marks were awarded]

Example responses:
Marks: 8
Feedback: Good answer showing understanding of the concept, minor details missing

Marks: 5
Feedback: Partially correct, shows some knowledge but incomplete

Marks: 0
Feedback: Incorrect or irrelevant answer

Now evaluate:"""
                    response = self.llm.invoke(evaluation_prompt)
                    eval_text = response.content
                    
                    print(f"[DEBUG] LLM Evaluation Response for Q{q_id}: {eval_text[:200]}...")
                    
                    # Parse LLM response - look for marks
                    marks_match = re.search(r'marks:\s*(\d+(?:\.\d+)?)', eval_text, re.IGNORECASE)
                    if marks_match:
                        marks_awarded = min(max(float(marks_match.group(1)), 0), question_marks)
                        is_correct = marks_awarded > 0
                        
                        # Extract feedback
                        feedback_match = re.search(r'feedback:\s*(.+?)(?:\n|$)', eval_text, re.IGNORECASE | re.DOTALL)
                        if feedback_match:
                            evaluation_feedback = feedback_match.group(1).strip()
                        else:
                            evaluation_feedback = f"Awarded {marks_awarded} marks based on answer quality"
                    else:
                        # If marks not found, try to infer from response
                        eval_lower = eval_text.lower()
                        if any(word in eval_lower for word in ['correct', 'good', 'accurate', 'right', 'proper']):
                            # Answer seems correct - award partial to full marks
                            if len(answer_trimmed) > 50:
                                marks_awarded = question_marks * 0.8  # 80% for substantial correct answer
                            else:
                                marks_awarded = question_marks * 0.5  # 50% for shorter correct answer
                            is_correct = True
                            evaluation_feedback = "Answer shows understanding - awarded partial marks"
                        else:
                            marks_awarded = 0
                            evaluation_feedback = "Could not determine correctness - 0 marks"
                    
                    print(f"[DEBUG] Q{q_id} Evaluation: marks={marks_awarded}, correct={is_correct}")
                    
                except Exception as e:
                    print(f"Error evaluating with LLM: {e}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    # Fallback: award marks based on answer length and quality
                    if len(answer_trimmed) < 10:
                        marks_awarded = 0
                        evaluation_feedback = "Answer too short - 0 marks"
                    elif len(answer_trimmed) < 30:
                        marks_awarded = question_marks * 0.3  # 30% for short but provided answer
                        is_correct = True
                        evaluation_feedback = "Short answer provided - partial marks"
                    else:
                        marks_awarded = question_marks * 0.6  # 60% for substantial answer when LLM fails
                        is_correct = True
                        evaluation_feedback = "Substantial answer provided - partial marks (LLM evaluation unavailable)"
            else:
                # No LLM - award marks based on answer length and quality
                if len(answer_trimmed) < 10:
                    marks_awarded = 0
                    evaluation_feedback = "Answer too short - 0 marks"
                elif len(answer_trimmed) < 30:
                    marks_awarded = question_marks * 0.4  # 40% for short answer
                    is_correct = True
                    evaluation_feedback = "Short answer provided - partial marks"
                else:
                    marks_awarded = question_marks * 0.7  # 70% for substantial answer
                    is_correct = True
                    evaluation_feedback = "Substantial answer provided - partial marks (AI evaluation unavailable)"
            
            if is_correct or marks_awarded > 0:
                correct_count += 1
                obtained_marks += marks_awarded
            
            feedback.append({
                "question_id": q_id,
                "question": question_text,
                "answer": answer_trimmed,
                "correct": is_correct,
                "marks_awarded": round(marks_awarded, 2),
                "max_marks": question_marks,
                "feedback": evaluation_feedback
            })
        
        # Calculate score percentage
        score = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        
        # Debug: Print evaluation summary
        print(f"[DEBUG] Evaluation Summary:")
        print(f"  Total marks: {total_marks}")
        print(f"  Obtained marks: {obtained_marks}")
        print(f"  Score: {score}%")
        print(f"  Correct answers: {correct_count}")
        print(f"  Total questions: {len(answers)}")
        print(f"  Feedback items: {len(feedback)}")
        
        # Ensure we have valid data
        total_questions = len(answers) if answers else 0
        if total_questions == 0:
            raise ValueError("No answers provided for evaluation")
        
        # Store in database - quiz_evaluations table
        try:
            conn = get_db_connection(self.db_path)
            conn.execute(
                """INSERT INTO quiz_evaluations
                (quiz_id, topic, difficulty, score, total_questions, correct_answers, total_marks, obtained_marks, timestamp, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (quiz_id, topic or '', difficulty or '', score, total_questions, correct_count, total_marks, obtained_marks,
                 datetime.now().isoformat(), user_id)
            )
        
            # Store in student_scores table for detailed tracking
            try:
                conn.execute(
                    """INSERT INTO student_scores
                    (student_id, quiz_id, topic, difficulty, score, total_marks, obtained_marks, correct_answers, total_questions, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, quiz_id, topic or '', difficulty or '', score, total_marks, obtained_marks, correct_count, total_questions,
                     datetime.now().isoformat())
                )
                print(f"Student score saved to student_scores table")
            except Exception as score_error:
                print(f"Warning: Could not save to student_scores table: {score_error}")
                # Continue - quiz_evaluations was already saved
            
            conn.commit()
            conn.close()
            print(f"Quiz evaluation data saved to main database: quiz_id={quiz_id}, student_id={user_id}, score={score}%")
        except Exception as db_error:
            import traceback
            print(f"ERROR: Database save failed (quiz will still be evaluated): {db_error}")
            print(f"Traceback: {traceback.format_exc()}")
            # Continue even if database save fails
        
        # Also save to student database if available (non-blocking)
        if self.student_db_path:
            try:
                from src.database.student_db import (
                    save_quiz_attempt, create_or_update_student
                )
                import traceback
                
                # Ensure student exists
                try:
                    create_or_update_student(self.student_db_path, user_id, user_id, None)
                except Exception as e:
                    print(f"Warning: Could not create/update student: {e}")
                
                # Prepare quiz data
                incorrect_count = len(answers) - correct_count
                unanswered_count = sum(1 for f in feedback if f.get('marks_awarded', 0) == 0 and not f.get('answer', '').strip())
                
                quiz_data = {
                    'quiz_id': quiz_id,
                    'topic': topic or '',
                    'difficulty': difficulty or '',
                    'score': score,
                    'total_marks': total_marks,
                    'obtained_marks': obtained_marks,
                    'total_questions': total_questions,
                    'correct_answers': correct_count,
                    'incorrect_answers': incorrect_count,
                    'unanswered_questions': unanswered_count,
                    'time_taken_seconds': time_taken_seconds or 0
                }
                # Debug: Print time value to verify it's being set
                print(f"[DEBUG] Agent: Preparing quiz_data with time_taken_seconds = {quiz_data.get('time_taken_seconds')}")
                
                # Prepare question details
                question_details = []
                for f in feedback:
                    question_details.append({
                        'question_id': f.get('question_id'),
                        'question_text': f.get('question', ''),
                        'student_answer': f.get('answer', ''),
                        'correct_answer': '',  # Not stored currently
                        'is_correct': f.get('correct', False),
                        'marks_awarded': f.get('marks_awarded', 0.0),
                        'max_marks': f.get('max_marks', 0.0),
                        'feedback': f.get('feedback', '')
                    })
                
                # Save to student database
                try:
                    save_quiz_attempt(self.student_db_path, user_id, quiz_data, question_details)
                    print(f"Quiz attempt saved to student database for student: {user_id}")
                except Exception as e:
                    print(f"Warning: Could not save quiz attempt to student database: {e}")
                    print(f"Traceback: {traceback.format_exc()}")
            except ImportError as e:
                print(f"Warning: Student database module not available: {e}")
            except Exception as e:
                import traceback
                print(f"Warning: Error accessing student database: {e}")
                print(f"Traceback: {traceback.format_exc()}")
        
        # Calculate completeness and confidence
        completeness = 1.0 if len(feedback) == total_questions else (len(feedback) / total_questions if total_questions > 0 else 0.0)
        confidence = 0.9 if self.llm else 0.6
        
        return {
            "quiz_id": quiz_id,
            "score": round(score, 2),
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "total_marks": round(total_marks, 2),
            "obtained_marks": round(obtained_marks, 2),
            "feedback": feedback,
            "completeness_score": round(completeness, 2),
            "confidence_score": round(confidence, 2)
        }