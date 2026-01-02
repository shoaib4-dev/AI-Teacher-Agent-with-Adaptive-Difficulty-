"""
Reasoning Service - AI Reasoning Features
Simple implementation: Summarization, Classification, LLM Explanation
"""

from typing import List, Dict

class ReasoningService:
    """Simple reasoning service"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def summarize(self, content: str, max_length: int = 200) -> str:
        """Summarize content"""
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        if not sentences:
            return content[:max_length] + "..."
        summary = '. '.join(sentences[:3])
        return summary[:max_length] + "..." if len(summary) > max_length else summary
    
    def classify(self, content: str, categories: List[str]) -> Dict:
        """Classify content"""
        content_lower = content.lower()
        scores = {}
        keywords = {
            "academic": ["study", "learn", "education", "course"],
            "technical": ["code", "programming", "algorithm", "function"],
            "general": ["hello", "help", "question", "explain"]
        }
        
        for cat in categories:
            score = sum(1 for kw in keywords.get(cat, []) if kw in content_lower)
            scores[cat] = score
        
        best = max(scores, key=scores.get)
        confidence = min(scores[best] / max(len(content.split()), 1), 1.0)
        return {"category": best, "confidence": round(confidence, 2), "scores": scores}
    
    def classify_topics(self, topics: List[str]) -> List[Dict]:
        """Classify topics"""
        result = []
        for topic in topics:
            topic_lower = topic.lower()
            if any(kw in topic_lower for kw in ["python", "java", "code"]):
                cat = "programming"
            elif any(kw in topic_lower for kw in ["math", "algebra"]):
                cat = "mathematics"
            elif any(kw in topic_lower for kw in ["physics", "chemistry"]):
                cat = "science"
            else:
                cat = "general"
            result.append({"topic": topic, "category": cat})
        return result
    
    def explain_with_llm(self, topic: str) -> str:
        """Generate explanation - fallback when LLM is not available"""
        # Generate a comprehensive multi-paragraph explanation as fallback
        paragraphs = []
        
        # Paragraph 1: Definition and Overview
        paragraphs.append(
            f"{topic} is a fundamental concept that plays a crucial role in modern technology and education. "
            f"It represents a comprehensive field of study that encompasses various principles, methodologies, and applications. "
            f"Understanding {topic} requires a solid foundation in its core concepts and the ability to apply theoretical knowledge to practical scenarios. "
            f"This topic has gained significant importance due to its wide-ranging applications across multiple industries and domains. "
            f"Students and professionals alike benefit from a deep understanding of {topic} as it opens doors to numerous career opportunities and problem-solving capabilities. "
            f"The study of {topic} involves both theoretical understanding and hands-on practice, making it an engaging and rewarding subject to explore."
        )
        
        # Paragraph 2: Core Concepts
        paragraphs.append(
            f"The core concepts of {topic} include fundamental principles that form the foundation of this field. "
            f"These concepts are interconnected and build upon each other, creating a comprehensive framework for understanding. "
            f"Key principles involve understanding the underlying mechanisms, processes, and relationships that govern how {topic} functions. "
            f"Mastering these core concepts is essential for anyone looking to develop expertise in this area. "
            f"The concepts range from basic introductory ideas to more advanced and specialized topics that require deeper study. "
            f"Each concept contributes to a holistic understanding of {topic} and its various applications."
        )
        
        # Paragraph 3: Applications
        paragraphs.append(
            f"{topic} finds applications in numerous real-world scenarios, making it highly relevant and practical. "
            f"Industries such as technology, healthcare, finance, education, and research all benefit from the principles of {topic}. "
            f"These applications demonstrate the versatility and importance of understanding this topic thoroughly. "
            f"From solving complex problems to creating innovative solutions, {topic} provides tools and methodologies that are essential in today's world. "
            f"The practical applications of {topic} continue to evolve as new technologies and methodologies emerge. "
            f"Understanding these applications helps bridge the gap between theoretical knowledge and real-world implementation."
        )
        
        # Paragraph 4: Importance and Future
        paragraphs.append(
            f"The importance of {topic} cannot be overstated in our modern, technology-driven world. "
            f"As society continues to evolve, the demand for expertise in {topic} grows across various sectors. "
            f"Learning {topic} not only enhances one's problem-solving abilities but also opens up numerous career opportunities. "
            f"The future of {topic} looks promising, with continuous advancements and new developments on the horizon. "
            f"Students and professionals who invest time in mastering {topic} will find themselves well-equipped to tackle challenges and contribute meaningfully to their fields. "
            f"The comprehensive understanding of {topic} serves as a valuable asset in both academic and professional settings."
        )
        
        # Join paragraphs with double newlines
        return '\n\n'.join(paragraphs)

