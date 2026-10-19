from typing import List, Dict, Any
import json

class ResponseGenerator:
    """Generate responses based on query, context, and memory"""
    
    def __init__(self):
        """Initialize response generator"""
        self.response_templates = self._load_templates()
    
    def generate(self, query: str, context: List[Dict], memory: Dict) -> str:
        """Generate a response using context and memory"""
        
        # If we have relevant context, use it
        if context and len(context) > 0:
            return self._generate_from_context(query, context, memory)
        else:
            return self._generate_fallback_response(query, memory)
    
    def _generate_from_context(self, query: str, context: List[Dict], memory: Dict) -> str:
        """Generate response using retrieved context"""
        response = "Based on our knowledge base:\n\n"
        
        for i, doc in enumerate(context, 1):
            if 'answer' in doc:  # FAQ
                response += f"{doc['answer']}"
            elif 'content' in doc:
                response += f"**{doc.get('title', 'Information')}**: {doc['content']}\n"
        
        # Add helpful follow-up
        response += "\n\nIs there anything else you'd like to know about this topic?"
        
        return response
    
    def _generate_fallback_response(self, query: str, memory: Dict) -> str:
        """Generate response when no context is found"""
        fallback_responses = [
            "I'm not sure about that specific question. Could you provide more details or contact the Student Support Center at support@example.edu?",
            "That's an interesting question! I don't have information about that in my knowledge base. Please reach out to the relevant department through the student portal.",
            "I don't have specific information about that. Please contact the Student Success Center (Room 201) or call 1-800-EXAMPLE.",
            "That's beyond my current knowledge base. I recommend visiting the student portal or contacting the administration office."
        ]
        
        # Choose response based on query keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['how', 'when', 'where', 'why']):
            return fallback_responses[0]
        elif any(word in query_lower for word in ['policy', 'regulation', 'rule']):
            return fallback_responses[1]
        elif any(word in query_lower for word in ['help', 'support', 'assistance']):
            return fallback_responses[2]
        else:
            return fallback_responses[3]
    
    def _load_templates(self) -> Dict:
        """Load response templates"""
        return {
            'greeting': "Hello! I'm the Student Support Assistant. How can I help you today?",
            'help': "I can help you with:\n- Course registration and academic information\n- FAQ and general inquiries\n- College regulations and policies\n- Syllabus and course details\n\nWhat would you like to know?",
            'unknown': "I'm sorry, I didn't understand that. Could you rephrase your question?",
            'closing': "Thank you for using the Student Support Assistant. Have a great day!"
        }
    
    def format_faq_response(self, faq: Dict) -> str:
        """Format FAQ response"""
        return f"**Q: {faq.get('question')}**\n\nA: {faq.get('answer')}"
    
    def format_regulation(self, regulation: Dict) -> str:
        """Format regulation response"""
        return f"**{regulation.get('title')}**\n\n{regulation.get('content')}\n\n_(Effective from {regulation.get('effective_date')})_"
    
    def format_syllabus(self, subject: str, syllabus: Dict) -> str:
        """Format syllabus response"""
        if not syllabus:
            return f"Sorry, I don't have syllabus information for {subject}."
        
        response = f"**{syllabus.get('title')} ({syllabus.get('code')})**\n\n"
        response += f"**Instructor:** {syllabus.get('instructor')}\n"
        response += f"**Credits:** {syllabus.get('credits')}\n\n"
        
        response += "**Topics Covered:**\n"
        for topic in syllabus.get('topics', []):
            response += f"- {topic}\n"
        
        response += f"\n**Assessment:** {syllabus.get('assessment')}"
        
        return response
    
    def create_helpful_prompt(self, query: str, memory: Dict) -> str:
        """Create a prompt for Claude or another LLM"""
        
        user_info = memory.get('user_info', {})
        topics = memory.get('topics', [])
        
        prompt = f"""You are a helpful Student Support Assistant for a college.

User Query: {query}

{f'User Background: {user_info}' if user_info else ''}
{f'Previous Topics: {", ".join(topics)}' if topics else ''}

Provide a helpful, clear, and concise response. If you don't know the answer, suggest contacting the Student Support Center or the relevant department.
"""
        
        return prompt
    
    def generate_suggestions(self, query: str) -> List[str]:
        """Generate follow-up suggestions based on query"""
        
        suggestions = []
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['registration', 'course', 'enroll']):
            suggestions = [
                "Show me the registration deadline",
                "How do I add/drop courses?",
                "What courses are available next semester?"
            ]
        elif any(word in query_lower for word in ['grade', 'exam', 'result']):
            suggestions = [
                "How is my grade calculated?",
                "When are exam results released?",
                "How do I appeal a grade?"
            ]
        elif any(word in query_lower for word in ['fee', 'payment', 'tuition']):
            suggestions = [
                "When is the fee payment deadline?",
                "What are the payment methods?",
                "Are there scholarships available?"
            ]
        elif any(word in query_lower for word in ['library', 'book', 'resource']):
            suggestions = [
                "What are the library hours?",
                "How many books can I borrow?",
                "Are there digital resources available?"
            ]
        else:
            suggestions = [
                "Show me FAQs",
                "Tell me about regulations",
                "Connect me to student support"
            ]
        
        return suggestions
