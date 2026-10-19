import json
import os
from typing import List, Dict
import re

class RAGSystem:
    """Retrieval Augmented Generation System for Knowledge Base"""
    
    def __init__(self):
        """Initialize RAG system with knowledge base"""
        self.knowledge_base = self._load_knowledge_base()
        self.faqs = self._load_faqs()
        self.syllabus = self._load_syllabus()
        self.regulations = self._load_regulations()
    
    def _load_knowledge_base(self) -> List[Dict]:
        """Load knowledge base documents"""
        kb_file = os.path.join(os.path.dirname(__file__), '../data/knowledge_base.json')
        try:
            with open(kb_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_knowledge_base()
    
    def _load_faqs(self) -> List[Dict]:
        """Load FAQs"""
        faq_file = os.path.join(os.path.dirname(__file__), '../data/faqs.json')
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_faqs()
    
    def _load_syllabus(self) -> Dict:
        """Load course syllabus"""
        syll_file = os.path.join(os.path.dirname(__file__), '../data/syllabus.json')
        try:
            with open(syll_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_syllabus()
    
    def _load_regulations(self) -> List[Dict]:
        """Load college regulations"""
        reg_file = os.path.join(os.path.dirname(__file__), '../data/regulations.json')
        try:
            with open(reg_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_regulations()
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant documents from knowledge base"""
        query_lower = query.lower()
        scored_docs = []
        
        # Score documents based on keyword matching
        for doc in self.knowledge_base:
            score = self._calculate_relevance(query_lower, doc)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Also search in FAQs
        for faq in self.faqs:
            score = self._calculate_relevance(query_lower, faq)
            if score > 0:
                scored_docs.append((score, faq))
        
        # Sort by relevance score and return top-k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search knowledge base with detailed results"""
        results = self.retrieve(query, top_k)
        formatted_results = []
        
        for result in results:
            formatted_results.append({
                'title': result.get('title', result.get('question', 'Document')),
                'content': result.get('content', result.get('answer', '')),
                'type': result.get('type', 'document'),
                'category': result.get('category', 'General')
            })
        
        return formatted_results
    
    def _calculate_relevance(self, query: str, document: Dict) -> float:
        """Calculate relevance score between query and document"""
        score = 0.0
        
        # Check title/question
        title = (document.get('title') or document.get('question') or '').lower()
        content = (document.get('content') or document.get('answer') or '').lower()
        
        # Split query into keywords
        keywords = query.split()
        
        # Score based on keyword matches
        for keyword in keywords:
            if len(keyword) > 2:  # Only consider keywords with 3+ characters
                if keyword in title:
                    score += 3.0
                if keyword in content:
                    score += 1.0
        
        return score
    
    def get_faqs(self) -> List[Dict]:
        """Get all FAQs"""
        return self.faqs
    
    def get_syllabus(self, subject: str) -> Dict:
        """Get syllabus for a specific subject"""
        subject_lower = subject.lower()
        return self.syllabus.get(subject_lower, {})
    
    def get_regulations(self) -> List[Dict]:
        """Get all regulations"""
        return self.regulations
    
    def _get_default_knowledge_base(self) -> List[Dict]:
        """Default knowledge base"""
        return [
            {
                "title": "Course Registration Process",
                "content": "Students must register for courses during the designated registration period. Visit the student portal at portal.example.edu to select courses.",
                "type": "procedure",
                "category": "Academic"
            },
            {
                "title": "Attendance Policy",
                "content": "Students are required to maintain 75% attendance in all courses. Absence exceeding limits may result in course withdrawal.",
                "type": "policy",
                "category": "Academic"
            },
            {
                "title": "Grading System",
                "content": "Grades are calculated based on continuous assessment (30%), mid-term (30%), and final exam (40%). Grade points range from 0 to 10.",
                "type": "policy",
                "category": "Academic"
            },
            {
                "title": "Library Services",
                "content": "The library provides 24/7 access to physical and digital resources. Students can borrow up to 5 books at a time for 2 weeks.",
                "type": "service",
                "category": "Campus"
            },
            {
                "title": "Fee Payment",
                "content": "Semester fees must be paid before course registration closes. Payment methods include online portal, bank transfer, and cash at the cashier.",
                "type": "procedure",
                "category": "Administration"
            }
        ]
    
    def _get_default_faqs(self) -> List[Dict]:
        """Default FAQs"""
        return [
            {
                "question": "How do I reset my student portal password?",
                "answer": "Click 'Forgot Password' on the login page. Enter your email and follow the instructions sent to your inbox.",
                "category": "Technical"
            },
            {
                "question": "What is the last day to drop a course?",
                "answer": "The last day to drop a course without penalty is the end of the 4th week of the semester.",
                "category": "Academic"
            },
            {
                "question": "How can I contact academic support?",
                "answer": "Academic support services are available at the Student Success Center, Room 201. Email: support@example.edu or call 1-800-EXAMPLE.",
                "category": "Support"
            },
            {
                "question": "Are there scholarships available?",
                "answer": "Yes, we offer merit-based and need-based scholarships. Apply through the financial aid office before the deadline.",
                "category": "Financial"
            },
            {
                "question": "What are the lab timings?",
                "answer": "Computer labs are open Monday to Friday 8 AM - 8 PM, Saturday 10 AM - 6 PM. Closed on Sundays.",
                "category": "Campus"
            }
        ]
    
    def _get_default_syllabus(self) -> Dict:
        """Default syllabus"""
        return {
            "python": {
                "code": "CS101",
                "title": "Python Programming",
                "instructor": "Dr. John Doe",
                "credits": 3,
                "topics": ["Variables and Data Types", "Control Flow", "Functions", "OOP", "File Handling"],
                "assessment": "30% assignments, 30% mid-term, 40% final exam"
            },
            "web_development": {
                "code": "CS201",
                "title": "Web Development",
                "instructor": "Prof. Jane Smith",
                "credits": 3,
                "topics": ["HTML/CSS", "JavaScript", "React", "Backend APIs", "Deployment"],
                "assessment": "40% projects, 20% quizzes, 40% final project"
            },
            "database": {
                "code": "CS202",
                "title": "Database Systems",
                "instructor": "Dr. Mike Johnson",
                "credits": 3,
                "topics": ["SQL", "Normalization", "Indexing", "Transactions", "NoSQL"],
                "assessment": "25% assignments, 25% mid-term, 25% final exam, 25% project"
            }
        }
    
    def _get_default_regulations(self) -> List[Dict]:
        """Default regulations"""
        return [
            {
                "title": "Academic Integrity Policy",
                "content": "All students must adhere to academic integrity standards. Plagiarism, cheating, and unauthorized collaboration are strictly prohibited.",
                "effective_date": "2024-01-01"
            },
            {
                "title": "Code of Conduct",
                "content": "Students are expected to maintain professional behavior on and off campus. Violation of code of conduct may result in disciplinary action.",
                "effective_date": "2024-01-01"
            },
            {
                "title": "Anti-Harassment Policy",
                "content": "The institution has zero tolerance for harassment, discrimination, and bullying. Report incidents to the Student Conduct Office.",
                "effective_date": "2024-01-01"
            },
            {
                "title": "Leave of Absence Policy",
                "content": "Students can apply for leave of absence (LOA) for up to 2 semesters. Submit application with valid reasons to the Dean's office.",
                "effective_date": "2024-01-01"
            }
        ]
