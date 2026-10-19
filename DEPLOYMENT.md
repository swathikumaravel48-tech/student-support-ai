# 🚀 Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Step-by-Step Setup

```bash
# 1. Clone/Download project
cd student-support-ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py

# 6. Access in browser
# http://localhost:5000/static/index.html
```

## Production Deployment

### Using Gunicorn (Recommended for Linux/Mac)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Recommended for Windows)

```bash
# Install Waitress
pip install waitress

# Run with Waitress
waitress-serve --port=5000 app:app
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t student-support-ai .
docker run -p 5000:5000 student-support-ai
```

## Cloud Deployment

### Heroku Deployment

```bash
# 1. Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-app-name

# 4. Set environment variables
heroku config:set FLASK_ENV=production

# 5. Deploy
git push heroku main

# 6. Open app
heroku open
```

**Procfile** (add to project root):
```
web: gunicorn app:app
```

### AWS Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize EB application
eb init -p python-3.9 student-support-ai

# 3. Create environment
eb create production

# 4. Deploy
eb deploy

# 5. Open application
eb open
```

### Google Cloud Run

```bash
# 1. Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login

# 3. Build and deploy
gcloud run deploy student-support-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure App Service

```bash
# 1. Install Azure CLI
# Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# 2. Login
az login

# 3. Create resource group
az group create --name student-support --location eastus

# 4. Create app service plan
az appservice plan create --name student-support-plan \
  --resource-group student-support --sku B1 --is-linux

# 5. Create web app
az webapp create --resource-group student-support \
  --plan student-support-plan --name student-support-ai --runtime "python|3.9"

# 6. Deploy
az webapp deployment source config-zip \
  --resource-group student-support \
  --name student-support-ai --src app.zip
```

## Configuration for Production

### Update .env for Production

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-change-this
FLASK_CORS_ORIGINS=https://yourdomain.com
```

### Security Checklist

- ✅ Change `SECRET_KEY` to a strong random string
- ✅ Set `DEBUG=False`
- ✅ Use HTTPS everywhere
- ✅ Implement rate limiting
- ✅ Add authentication for admin endpoints
- ✅ Enable CORS only for trusted domains
- ✅ Use environment variables for sensitive data
- ✅ Regular security updates
- ✅ Add logging and monitoring
- ✅ Implement backup strategy

### Performance Optimization

```python
# Add caching headers
@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# Use gzip compression
from flask_compress import Compress
Compress(app)

# Add rate limiting
from flask_limiter import Limiter
limiter = Limiter(app)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("100 per hour")
def chat():
    # ... your code
```

## Database Integration

### PostgreSQL Setup

```python
# Install dependencies
pip install flask-sqlalchemy psycopg2

# app.py
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    content = db.Column(db.Text)
    role = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime)
```

### MongoDB Setup

```python
# Install dependencies
pip install pymongo

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['student_support']
messages = db['messages']

# Store message
messages.insert_one({
    'session_id': session_id,
    'content': content,
    'role': role,
    'timestamp': datetime.now()
})
```

## Monitoring & Logging

### Add Logging

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    logger.info(f"New chat message from {session_id}")
    # ... your code
```

### Add Error Tracking

```python
# Using Sentry
import sentry_sdk
sentry_sdk.init("your-sentry-dsn-url")

@app.errorhandler(Exception)
def handle_error(error):
    sentry_sdk.capture_exception(error)
    return jsonify({'error': str(error)}), 500
```

## Scaling Considerations

### Multi-Worker Setup

```bash
# Use gunicorn with multiple workers
gunicorn -w 8 -b 0.0.0.0:5000 \
  --worker-class sync \
  --timeout 30 \
  --max-requests 1000 \
  app:app
```

### Load Balancing

```nginx
# nginx configuration
upstream app {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://app;
    }
}
```

### Redis Caching

```python
# Install redis
pip install redis

from redis import Redis

cache = Redis(host='localhost', port=6379, db=0)

# Cache responses
@app.route('/api/faq')
def get_faqs():
    cached = cache.get('faqs')
    if cached:
        return json.loads(cached)
    
    faqs = rag_system.get_faqs()
    cache.set('faqs', json.dumps(faqs), ex=3600)
    return jsonify({'faqs': faqs})
```

## Backup Strategy

```bash
# Backup knowledge base
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Backup database
pg_dump dbname > backup_$(date +%Y%m%d).sql

# Upload to cloud storage
aws s3 cp backup_*.tar.gz s3://your-backup-bucket/
```

## Maintenance

### Regular Updates

```bash
# Check for outdated packages
pip list --outdated

# Update packages
pip install --upgrade package-name

# Update all packages
pip install --upgrade -r requirements.txt
```

### Logs Rotation

```bash
# Use logrotate on Linux
# /etc/logrotate.d/student-support-ai
/var/log/student-support-ai/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0600 app app
}
```

## Rollback Procedure

```bash
# Save previous version
git tag v1.0.0-backup

# Rollback to previous commit
git revert HEAD

# Deploy previous version
eb deploy --version v1.0.0-backup
```

## Performance Metrics

Monitor these key metrics:
- Response time (target: <200ms)
- Error rate (target: <1%)
- API availability (target: >99.9%)
- Memory usage
- CPU utilization
- Database query time

---

**Need Help?** Refer to the README.md or QUICKSTART.md for more information.
