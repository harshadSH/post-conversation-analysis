# 💬 Post Conversation Analysis — Django REST API  
### Kipps.AI Internship Task | Developed by Harshad Hole

---

## 🚀 Overview
This project is an automated **Post-Conversation Analysis System** built with **Django REST Framework**.  
It analyzes chat messages between a **human user** and an **AI agent** to measure parameters like clarity, empathy, relevance, sentiment, and fallback frequency.

The system stores each conversation and its analysis in a database and includes a **daily cron job** to automatically analyze new conversations.

---

## 🧠 Features
- Accepts chat messages (JSON) via API  
- Performs AI-powered conversation analysis using NLP (TextBlob + Sentence Transformers)  
- Calculates 10 key parameters:
  - Clarity Score  
  - Relevance Score  
  - Accuracy Score  
  - Completeness Score  
  - Empathy Score  
  - Sentiment (Positive / Neutral / Negative)  
  - Resolution Detection  
  - Escalation Need  
  - Fallback Frequency  
  - Overall User Satisfaction Score  
- Stores analysis in database (SQLite/PostgreSQL)  
- Automated **daily cron job** using `django-crontab`  
- REST APIs built with Django REST Framework  

---

## 🛠️ Tech Stack
- **Backend:** Django 5.0 + Django REST Framework  
- **Database:** SQLite (default) or PostgreSQL  
- **NLP Libraries:**  
  - `TextBlob` → for sentiment & clarity  
  - `Sentence Transformers` → for semantic relevance  
  - `nltk` → for tokenization and lemmatization  
- **Automation:** `django-crontab`

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/harshadSH/post-conversation-analysis.git
cd post-conversation-analysis

**###2️⃣ Create a Virtual Environment**
python -m venv venv
source venv/bin/activate   # (on Linux/Mac)
venv\Scripts\activate      # (on Windows)

**3️⃣ Install Dependencies**
pip install -r requirements.txt

**4️⃣ Apply Migrations**
python manage.py makemigrations
python manage.py migrate

**5️⃣ Run the Server**
python manage.py runserver


Access API at →
👉 http://127.0.0.1:8000/api/

🧩 API Endpoints
Endpoint	           Method	  Description
/api/conversations/	 POST	    Upload chat messages (JSON)
/api/analyse/	       POST	    Analyze a stored conversation
/api/reports/	       GET	    Get list of all analyzed reports
