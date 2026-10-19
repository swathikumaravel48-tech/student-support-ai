from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Import custom modules
from utils.rag_system import RAGSystem
from utils.memory_manager import MemoryManager
from utils.response_generator import ResponseGenerator

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize systems
rag_system = RAGSystem()
memory_manager = MemoryManager()
response_generator = ResponseGenerator()

# In-memory session store (use Redis in production)
sessions = {}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        user_query = data.get('message', '')
        
        if not user_query:
            return jsonify({"error": "Message is required"}), 400
        
        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = {
                'messages': [],
                'memory': memory_manager.create_memory(session_id)
            }
        
        # Retrieve relevant context using RAG
        context = rag_system.retrieve(user_query)
        
        # Get user memory/history
        user_memory = sessions[session_id]['memory']
        
        # Generate response
        response = response_generator.generate(
            query=user_query,
            context=context,
            memory=user_memory
        )
        
        # Store in memory
        sessions[session_id]['messages'].append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now().isoformat()
        })
        sessions[session_id]['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update memory with conversation
        memory_manager.update_memory(session_id, user_query, response)
        
        return jsonify({
            "session_id": session_id,
            "response": response,
            "context_used": len(context),
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """Search knowledge base"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Query parameter required"}), 400
        
        results = rag_system.search(query, top_k=5)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/faq', methods=['GET'])
def get_faqs():
    """Get all FAQs"""
    try:
        faqs = rag_system.get_faqs()
        return jsonify({
            "faqs": faqs,
            "count": len(faqs)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/syllabus/<subject>', methods=['GET'])
def get_syllabus(subject):
    """Get syllabus for a subject"""
    try:
        syllabus = rag_system.get_syllabus(subject)
        if not syllabus:
            return jsonify({"error": "Syllabus not found"}), 404
        
        return jsonify({"subject": subject, "syllabus": syllabus}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regulations', methods=['GET'])
def get_regulations():
    """Get college regulations"""
    try:
        regulations = rag_system.get_regulations()
        return jsonify({
            "regulations": regulations,
            "count": len(regulations)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get chat history for a session"""
    try:
        if session_id not in sessions:
            return jsonify({"error": "Session not found"}), 404
        
        messages = sessions[session_id]['messages']
        return jsonify({
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear session data"""
    try:
        if session_id in sessions:
            del sessions[session_id]
            memory_manager.clear_memory(session_id)
        
        return jsonify({
            "status": "Session cleared",
            "session_id": session_id
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
