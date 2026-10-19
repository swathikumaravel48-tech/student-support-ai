# ⚡ Quick Start Guide

## 5 Minute Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Flask Backend
```bash
python app.py
```
✅ Server starts at `http://localhost:5000`

### 3. Open Frontend
- **Option A**: Direct browser access
  ```
  http://localhost:5000/static/index.html
  ```

- **Option B**: Run separate server
  ```bash
  # In another terminal
  cd static
  python -m http.server 8000
  # Visit: http://localhost:8000/index.html
  ```

### 4. Start Chatting! 💬
```
User: How do I register for courses?
Bot: [Retrieves from knowledge base and responds]
```

## Example Queries to Try

1️⃣ **Course Registration**
   - "How do I register for courses?"
   - "What is the course registration deadline?"

2️⃣ **Grades & Exams**
   - "How are grades calculated?"
   - "When is my exam schedule released?"

3️⃣ **Policies**
   - "What is the attendance policy?"
   - "Tell me about academic integrity"

4️⃣ **Services**
   - "What are the library hours?"
   - "How do I access the computer lab?"

5️⃣ **Support**
   - "How do I contact academic support?"
   - "How do I request a transcript?"

## Test the API with CURL

```bash
# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"How do I register?"}'

# Search endpoint
curl "http://localhost:5000/api/search?q=registration"

# Get FAQs
curl http://localhost:5000/api/faq

# Get Regulations
curl http://localhost:5000/api/regulations

# Get Syllabus
curl http://localhost:5000/api/syllabus/python
```

## File Structure Overview

```
📦 student-support-ai
├── 📄 app.py                    ← Main Flask app
├── 📄 requirements.txt          ← Dependencies
├── 📄 .env                      ← Configuration
├── 📁 utils/                    ← Backend logic
│   ├── rag_system.py           ← Knowledge base
│   ├── memory_manager.py       ← Session memory
│   └── response_generator.py   ← Response logic
├── 📁 data/                     ← Knowledge base files
│   ├── knowledge_base.json
│   ├── faqs.json
│   ├── syllabus.json
│   └── regulations.json
└── 📁 static/                   ← Frontend
    ├── index.html              ← Chat interface
    ├── style.css               ← Styling
    └── script.js               ← JavaScript
```

## Troubleshooting

❌ **Port 5000 already in use**
```bash
# Change port in .env
PORT=5001
```

❌ **Module not found error**
```bash
pip install flask flask-cors python-dotenv
```

❌ **Static files not loading**
- Make sure you're accessing the correct URL
- Check browser console for errors
- Ensure Flask is serving static files

## Next Steps

✨ **Enhance the Project:**
1. Add more knowledge base documents
2. Integrate with Claude API for smarter responses
3. Add user authentication
4. Deploy to cloud (Heroku, AWS, Azure)
5. Add database support (PostgreSQL, MongoDB)

## Configuration Tips

**For Development:**
```env
DEBUG=True
FLASK_ENV=development
```

**For Production:**
```env
DEBUG=False
FLASK_ENV=production
CORS allowed_origins=your-domain.com
```

## Common Tasks

### Add New Course Syllabus
Edit `data/syllabus.json`:
```json
"new_course": {
  "code": "CS999",
  "title": "New Course",
  "instructor": "Prof. Name",
  ...
}
```

### Add New FAQ
Edit `data/faqs.json`:
```json
{
  "id": 13,
  "question": "Your question?",
  "answer": "Your answer",
  "category": "Support"
}
```

### Modify Knowledge Base
Edit `data/knowledge_base.json` to add/update information.

## Performance Tips

🚀 **Optimization:**
- Keep JSON files under 10MB
- Limit `MAX_HISTORY` to 20 messages
- Use caching for frequently accessed data
- Consider Redis for multi-user deployment

## Support

📖 Read `README.md` for detailed documentation
🔧 Check `.env` file for configuration options
💻 Review code comments for implementation details

---

**Ready? Start with:** `python app.py`
