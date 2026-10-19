import json
from datetime import datetime
from typing import Dict, List

class MemoryManager:
    """Manage user memory and conversation history"""
    
    def __init__(self):
        """Initialize memory manager"""
        self.memories = {}
        self.max_history = 20  # Keep last 20 messages
    
    def create_memory(self, session_id: str) -> Dict:
        """Create a new memory for a session"""
        if session_id not in self.memories:
            self.memories[session_id] = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'messages': [],
                'user_info': {},
                'preferences': {},
                'topics': []
            }
        return self.memories[session_id]
    
    def update_memory(self, session_id: str, user_query: str, assistant_response: str):
        """Update memory with new conversation"""
        if session_id not in self.memories:
            self.create_memory(session_id)
        
        memory = self.memories[session_id]
        
        # Add messages
        memory['messages'].append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now().isoformat()
        })
        memory['messages'].append({
            'role': 'assistant',
            'content': assistant_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(memory['messages']) > self.max_history:
            memory['messages'] = memory['messages'][-self.max_history:]
        
        # Extract and store topics
        self._extract_topics(session_id, user_query)
    
    def get_memory(self, session_id: str) -> Dict:
        """Get memory for a session"""
        if session_id not in self.memories:
            self.create_memory(session_id)
        return self.memories[session_id]
    
    def get_recent_context(self, session_id: str, num_messages: int = 5) -> List[Dict]:
        """Get recent conversation context"""
        memory = self.get_memory(session_id)
        messages = memory['messages']
        
        # Return last num_messages
        return messages[-num_messages:] if len(messages) >= num_messages else messages
    
    def store_user_info(self, session_id: str, key: str, value: str):
        """Store user information"""
        memory = self.get_memory(session_id)
        memory['user_info'][key] = value
    
    def get_user_info(self, session_id: str) -> Dict:
        """Get stored user information"""
        memory = self.get_memory(session_id)
        return memory['user_info']
    
    def store_preference(self, session_id: str, key: str, value: str):
        """Store user preference"""
        memory = self.get_memory(session_id)
        memory['preferences'][key] = value
    
    def get_preferences(self, session_id: str) -> Dict:
        """Get user preferences"""
        memory = self.get_memory(session_id)
        return memory['preferences']
    
    def get_topics(self, session_id: str) -> List[str]:
        """Get topics discussed in conversation"""
        memory = self.get_memory(session_id)
        return memory['topics']
    
    def _extract_topics(self, session_id: str, query: str):
        """Extract and store topics from query"""
        keywords = {
            'registration': ['register', 'registration', 'enroll', 'course', 'select'],
            'grades': ['grade', 'marks', 'score', 'exam', 'result'],
            'attendance': ['attend', 'absent', 'presence', 'class'],
            'fees': ['fee', 'payment', 'cost', 'charge', 'tuition'],
            'academic': ['academic', 'study', 'course', 'subject', 'lesson'],
            'library': ['library', 'book', 'resource', 'borrow'],
            'technical': ['technical', 'portal', 'password', 'account', 'system'],
            'support': ['help', 'support', 'assistance', 'contact', 'issue']
        }
        
        memory = self.get_memory(session_id)
        query_lower = query.lower()
        
        for topic, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in query_lower:
                    if topic not in memory['topics']:
                        memory['topics'].append(topic)
                    break
    
    def clear_memory(self, session_id: str):
        """Clear memory for a session"""
        if session_id in self.memories:
            del self.memories[session_id]
    
    def get_summary(self, session_id: str) -> Dict:
        """Get summary of conversation"""
        memory = self.get_memory(session_id)
        
        return {
            'session_id': session_id,
            'created_at': memory['created_at'],
            'total_messages': len(memory['messages']),
            'user_info': memory['user_info'],
            'preferences': memory['preferences'],
            'topics': memory['topics']
        }
    
    def build_context_prompt(self, session_id: str) -> str:
        """Build context string for LLM"""
        memory = self.get_memory(session_id)
        user_info = memory['user_info']
        recent_context = self.get_recent_context(session_id, 3)
        
        context = "Previous conversation:\n"
        for msg in recent_context[-2:]:  # Include last 2 messages
            context += f"{msg['role']}: {msg['content']}\n"
        
        if user_info:
            context += "\nUser Info:\n"
            for key, value in user_info.items():
                context += f"- {key}: {value}\n"
        
        return context
