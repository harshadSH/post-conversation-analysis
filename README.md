````markdown
# 💬 Post-Conversation Analysis — Django REST API  
### Kipps.AI Internship Assignment | Developed by **Harshad Hole**

---

## 🧠 Project Overview
This project implements an **automated post-conversation analysis system** using **Django REST Framework**.  
It evaluates conversations between a human user and an AI agent to determine metrics like clarity, relevance, empathy, sentiment, fallback frequency, and resolution.  

The system provides REST APIs to:
1. Upload a chat JSON  
2. Analyze the conversation using NLP  
3. View stored analysis results  

Additionally, a **daily cron job** automatically analyzes all new conversations without manual input.  

---

## ⚙️ 1️⃣ Setup and Run Instructions

### Clone the Repository
```bash
git clone https://github.com/harshadSH/post-conversation-analysis.git
cd post-conversation-analysis
````

### Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run the Server

```bash
python manage.py runserver
```

Once running, access the API at:
👉 **[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)**

---

## ⏰ 2️⃣ Cron Job Setup Steps

The cron job automatically performs analysis on all new conversations every day at midnight (12:00 AM).

### Install django-crontab

```bash
pip install django-crontab
```

### Add to `INSTALLED_APPS` in `settings.py`

```python
INSTALLED_APPS = [
    ...,
    'django_crontab',
    'analysis',
]
```

### Add Cron Schedule in `settings.py`

```python
CRONJOBS = [
    ('0 0 * * *', 'analysis.cron.auto_analyse_conversations'),
]
```

### Register the Cron Job

```bash
python manage.py crontab add
python manage.py crontab show
```

Example Output:

```
Job: 1 -> (0 0 * * *) analysis.cron.auto_analyse_conversations
```
---
## So `'0 0 * * *'` Means:

> Run this function **every day at 12:00 AM (midnight)**.

Breakdown:

* `0` → minute = 0
* `0` → hour = 0
* `*` → every day
* `*` → every month
* `*` → every weekday
### (Optional) Run Manually for Testing

```bash
python manage.py crontab run <job_id>
```

---

## 🌐 3️⃣ API Documentation with Examples

### Base URL

```
http://127.0.0.1:8000/api/
```

| Endpoint              | Method   | Description                   |
| --------------------- | -------- | ----------------------------- |
| `/api/conversations/` | **POST** | Upload chat messages (JSON)   |
| `/api/analyse/`       | **POST** | Analyze a stored conversation |
| `/api/reports/`       | **GET**  | Retrieve all analyzed reports |

---

### 🔹 Upload Conversation

**POST** `/api/conversations/`
Upload chat messages between a user and the AI.

**Request Body**

```json
[
  {"sender": "user", "message": "Hi, my internet is not working since morning."},
  {"sender": "ai", "message": "I'm sorry to hear that. Can you please confirm your connection ID?"},
  {"sender": "user", "message": "It's 998877."},
  {"sender": "ai", "message": "Thank you! I can see your connection is currently down. It should be resolved in 2 hours."}
]
```

**Response**

```json
{
  "conversation_id": 1
}
```

---

### 🔹 Analyze Conversation

**POST** `/api/analyse/`
Run NLP analysis on the stored conversation.

**Request Body**

```json
{
  "conversation_id": 1
}
```

**Response**

```json
{
  "clarity_score": 0.91,
  "relevance_score": 0.87,
  "accuracy_score": 0.8,
  "completeness_score": 0.78,
  "empathy_score": 0.74,
  "sentiment": "negative",
  "resolution": true,
  "escalation_needed": false,
  "fallback_count": 0,
  "overall_score": 0.82
}
```

---

### 🔹 Get All Reports

**GET** `/api/reports/`

**Response**

```json
[
  {
    "conversation_id": 1,
    "title": "Chat",
    "clarity_score": 0.91,
    "relevance_score": 0.87,
    "accuracy_score": 0.8,
    "completeness_score": 0.78,
    "empathy_score": 0.74,
    "sentiment": "negative",
    "resolution": true,
    "escalation_needed": false,
    "fallback_count": 0,
    "overall_score": 0.82,
    "created_at": "2025-11-08T22:57:41Z"
  }
]
```

---

## 🧪 Testing the API with Postman

### Step 1 — Upload Conversation

**POST** → `http://127.0.0.1:8000/api/conversations/`
Paste JSON → Click **Send** → Get `conversation_id`.

### Step 2 — Analyze

**POST** → `http://127.0.0.1:8000/api/analyse/`
Body:

```json
{"conversation_id": 1}
```

→ Returns analysis metrics.

### Step 3 — View All Reports

**GET** → `http://127.0.0.1:8000/api/reports/`

✅ This shows all conversation analyses with their computed scores.

---

## 📦 Dependencies (requirements.txt)

```
Django>=5.0
djangorestframework
textblob
nltk
sentence-transformers
django-crontab
numpy
```
---
