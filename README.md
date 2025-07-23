# 📘 FastAPI Backend for Chinese Learning App

This FastAPI service powers the AI and dictionary features for the Chinese Learning App. It handles vocabulary lookups using CC-CEDICT and provides endpoints for AI-driven features like story generation, quiz evaluation, and pronunciation feedback.

---

## 🚀 Features

- 🔍 **CEDICT Lookup**: Fast search of Chinese characters, pinyin, and definitions.
- 🧠 **AI Endpoints** *(planned)*:
  - Story and dialogue generation
  - Speech-to-text grading (Whisper)
  - Grammar and tone correction

---

## 📁 Project Structure

```
fastapi-backend/
├── main.py               # FastAPI app with all routes
├── cedict.db             # SQLite version of CC-CEDICT
├── requirements.txt      # Python dependencies
└── README.md             # You're here!
```

---

## 🏁 Getting Started

### 1. 🐍 Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 2. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### 3. ▶️ Run the server

```bash
uvicorn main:app --reload
```

The server will be available at:  
`http://localhost:8000`

---

## 🔍 Dictionary Lookup Endpoint

### `GET /lookup`

Search for a word in the CC-CEDICT database.

#### Query Parameters:
- `text` (string): Simplified or traditional character to search

#### Example:

```http
GET /lookup?text=吃
```

#### Response:

```json
[
  {
    "simplified": "吃",
    "traditional": "吃",
    "pinyin": "chi1",
    "definition": "to eat; to consume"
  }
]
```

---

## 🔒 Authentication

No authentication is required for `/lookup`. Future AI routes may require Supabase JWT validation.

---

## 🧠 Future Development

- [ ] AI-powered story/dialogue generation
- [ ] Pronunciation grading with Whisper
- [ ] Integration with Supabase user tokens for secure endpoints
- [ ] Rate limiting and error handling

---