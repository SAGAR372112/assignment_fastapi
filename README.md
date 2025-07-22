Trade Opportunities API

AI-powered FastAPI service for market analysis and trade opportunities in Indian sectors using Google Gemini.

# Features
AI Analysis: Google Gemini integration for market insights
Real-time Data: Automated market data collection
Secure Auth: JWT authentication with demo/guest access
Markdown Reports: Structured analysis reports
Rate Limited: Built-in API protection

#Quick Start

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
echo "SECRET_KEY=your-secret-key" >> .env

# Run server
uvicorn main:app --reload

Get Gemini API Key
Visit [Google AI Studio](https://aistudio.google.com/apikey) for free API key.

Authentication
# Demo login 
curl -X POST "http://localhost:8000/auth/login" -d "username=demo&password=demo123"

# Analyze Sector (5 requests limits)
curl -X GET "http://localhost:8000/analyze/pharmaceuticals" \
     -H "Authorization: Bearer YOUR_TOKEN"

# python
'''
import requests

# Get token
auth = requests.post("http://localhost:8000/auth/guest")
token = auth.json()["access_token"]

# Analyze sector
response = requests.get("http://localhost:8000/analyze/technology",headers={"Authorization": f"Bearer {token}"})

# Save report
with open("report.md", "w") as f:
    f.write(response.json()["markdown_report"])
'''

# API Endpoints
Method  End-Points              Discriptions
POST    /auth/login             Demo login (demo/demo123)
GET     /analyze/{sector}       Market Analysis

# Supported Sectors
pharmaceuticals, technology, agriculture, textiles, automotive, renewable-energy, manufacturing, healthcare, fintech, e-commerce

# Environment Variables
GEMINI_API_KEY=your_gemini_key          # Required
SECRET_KEY=your-jwt-secret              # Required  
ACCESS_TOKEN_EXPIRE_MINUTES=30          # Optional

# Development
uvicorn main:app --reload --port 8000

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# Response Format
{
  "sector": "Technology",
  "analysis_date": "2024-07-22T10:30:00",
  "markdown_report": "# Trade Opportunities Analysis...",
  "data_sources_count": 4,
  "user": "demo"
}

# Troubleshooting
401 Unauthorized: Token expired, re-authenticate
429 Rate Limited: Wait or use different session
404 No Data: Try different sector names
Gemini Error: Check API key in .env file