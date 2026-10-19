# 🎓 AI Student Support Assistant

An intelligent chatbot system that provides students with quick answers to academic and administrative questions using Retrieval Augmented Generation (RAG), memory management, and AI tools.

## 📋 Project Overview

This project implements an **AI Student Support Assistant** that uses:
- **RAG (Retrieval Augmented Generation)** - Search and retrieve relevant information from knowledge base
- **Memory Management** - Maintains conversation history and user context
- **Tool Calling** - Integrates various college services and tools

### Key Features

✅ **Smart Q&A** - Answer college-related questions from regulations, syllabus, FAQs, and notices  
✅ **Knowledge Base** - Comprehensive database of college information  
✅ **Conversation Memory** - Maintains session history and user context  
✅ **Search Functionality** - Find information by keywords  
✅ **User-Friendly Interface** - Modern, responsive web UI  
✅ **RESTful API** - Easy integration with other systems  

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Handle cross-origin requests
- **Python 3.8+** - Programming language
- **JSON** - Data format for knowledge base

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with animations
- **JavaScript (Vanilla)** - Interactivity
- **Responsive Design** - Mobile-friendly

### Architecture
- **RAG System** - Knowledge base retrieval
- **Memory Manager** - Session and conversation management
- **Response Generator** - Intelligent response creation

## 📁 Project Structure

```
student-support-ai/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── README.md                   # Project documentation
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── rag_system.py          # RAG and knowledge base
│   ├── memory_manager.py      # Session and conversation memory
│   └── response_generator.py  # Response generation logic
│
├── data/                       # Knowledge base files
│   ├── knowledge_base.json    # Main knowledge base
│   ├── faqs.json              # Frequently asked questions
│   ├── syllabus.json          # Course syllabi
│   └── regulations.json       # College regulations
│
├── static/                     # Frontend files
│   ├── index.html             # Main HTML file
│   ├── style.css              # Stylesheets
│   └── script.js              # JavaScript functionality
│
└── templates/                 # Flask templates (if needed)
```

## 🚀 Installation & Setup

### Step 1: Clone or Download Project
```bash
cd student-support-ai
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

#### Start Flask Backend
```bash
python app.py
```
Backend runs on: `http://localhost:5000`

#### Access Frontend
Open your browser and navigate to:
```
http://localhost:5000/static/index.html
```

Or serve the static files with any HTTP server:
```bash
# Using Python
python -m http.server 8000

# Then visit: http://localhost:8000/static/index.html
```

## 📚 API Endpoints

### Chat Endpoint
**POST** `/api/chat`
```json
{
  "session_id": "session_xxx",
  "message": "How do I register for courses?"
}
```

Response:
```json
{
  "session_id": "session_xxx",
  "response": "...",
  "context_used": 3,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Search Endpoint
**GET** `/api/search?q=registration&top_k=5`

Response:
```json
{
  "query": "registration",
  "results": [...],
  "count": 5
}
```

### FAQ Endpoint
**GET** `/api/faq`

### Regulations Endpoint
**GET** `/api/regulations`

### Syllabus Endpoint
**GET** `/api/syllabus/<subject>`

Example:
```
GET /api/syllabus/python
```

### History Endpoint
**GET** `/api/history/<session_id>`

### Clear Session
**DELETE** `/api/clear-session/<session_id>`

## 🧠 System Components

### 1. RAG System (`utils/rag_system.py`)
- Loads and manages knowledge base from JSON files
- Implements relevance scoring algorithm
- Retrieves top-k most relevant documents
- Supports keyword-based search

### 2. Memory Manager (`utils/memory_manager.py`)
- Creates and maintains session memory
- Stores conversation history
- Extracts and tracks topics discussed
- Manages user information and preferences

### 3. Response Generator (`utils/response_generator.py`)
- Generates contextual responses
- Formats FAQs, regulations, and syllabi
- Creates fallback responses
- Suggests follow-up questions

## 📖 Knowledge Base

The knowledge base consists of:

### Knowledge Base (10 documents)
- Course registration
- Attendance policy
- Grading system
- Library services
- Fee payment
- Exam schedule
- Lab access
- Internship programs
- Hostel facilities
- Scholarships

### FAQs (12 questions)
- Portal password reset
- Course drop deadline
- Academic support contact
- Scholarships availability
- Library/lab hours
- Transcript requests
- Medical certificates
- Exam results
- Course prerequisites
- Course retakes
- Internship process
- Hostel application

### Syllabus (5 courses)
- Python Programming
- Web Development with React
- Database Systems and SQL
- Cloud Computing and AWS
- Data Science and Machine Learning

### Regulations (10 policies)
- Academic integrity
- Code of conduct
- Anti-harassment policy
- Leave of absence
- Dress code
- Substance use policy
- Campus safety
- Fee and refund policy
- Grade appeals
- Exam regulations

## 🔧 Configuration

Edit `.env` file to configure:
```env
FLASK_ENV=development        # development or production
DEBUG=True                   # Enable/disable debug mode
HOST=0.0.0.0               # Server host
PORT=5000                  # Server port
MAX_HISTORY=20             # Maximum conversation history
```

## 💡 Usage Examples

### Example 1: Course Registration
**User**: "How do I register for courses?"
**Assistant**: Retrieves course registration information from knowledge base

### Example 2: FAQ Lookup
**User**: "What is the attendance policy?"
**Assistant**: Returns attendance policy from FAQ

### Example 3: Syllabus Query
**User**: "Tell me about the Python course"
**Assistant**: Retrieves and formats Python course syllabus

### Example 4: Regulation Check
**User**: "What is the academic integrity policy?"
**Assistant**: Returns college's academic integrity regulation

## 🎯 How RAG Works

1. **User Query** → "How do I register for courses?"
2. **Keyword Extraction** → Extract keywords: "register", "courses"
3. **Search** → Score all documents based on keyword matches
4. **Ranking** → Sort by relevance score
5. **Retrieval** → Return top-3 most relevant documents
6. **Response** → Generate response using retrieved documents + memory

## 🔒 Security Considerations

⚠️ For production deployment:
- Change `SECRET_KEY` in `.env`
- Set `DEBUG=False`
- Use HTTPS
- Implement authentication
- Add rate limiting
- Validate all inputs
- Use a production WSGI server (Gunicorn)

## 📈 Extending the Project

### Add More Knowledge Base Documents
Edit `data/knowledge_base.json`:
```json
{
  "id": 11,
  "title": "New Topic",
  "content": "Information about the topic",
  "type": "procedure",
  "category": "Academic",
  "keywords": ["keyword1", "keyword2"]
}
```

### Integrate with Claude API
Modify `utils/response_generator.py` to use Claude's API for more sophisticated responses.

### Add Database Support
Replace JSON files with a database:
```python
from sqlalchemy import create_engine, Column, String
# Add SQLAlchemy integration
```

### Implement Advanced NLP
Add spaCy or NLTK for better understanding:
```python
import spacy
nlp = spacy.load('en_core_web_sm')
```

## 🐛 Troubleshooting

### Issue: "Connection refused" error
**Solution**: Ensure Flask backend is running
```bash
python app.py
```

### Issue: Static files not loading
**Solution**: Check file paths and CORS settings in `app.py`

### Issue: Slow response
**Solution**: Reduce `MAX_HISTORY` or optimize JSON file size

### Issue: Session not persisting
**Solution**: Use Redis instead of in-memory storage for production

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created as a demonstration of AI-powered student support system using RAG, Memory Management, and Tool Calling.

## 🤝 Contributing

Feel free to fork, modify, and enhance this project. Some ideas:
- Add more sophisticated NLP
- Implement user authentication
- Add multilingual support
- Create mobile app
- Integrate with college management system
- Add analytics and reporting

## 📧 Support

For issues or questions, refer to the documentation or modify the code as needed.

---

**Happy learning! 🎓**
