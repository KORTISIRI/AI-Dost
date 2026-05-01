# 🤖 AI Dost — Hinglish AI Assistant Backend

> **"Bhai tension mat le, AI Dost hai na! 😄"**

A hackathon-ready backend for a Hinglish AI assistant with **Chat API**, **Scam Detection**, and **RAG (Retrieval-Augmented Generation)** support. Built with FastAPI + Ollama + ChromaDB.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Chat API** | Conversational endpoint with Hinglish personality |
| 🔍 **Scam Detection** | Regex/rule-based fraud detection layer |
| 📚 **RAG Pipeline** | ChromaDB + sentence-transformers for grounded answers |
| 📱 **WhatsApp Webhook** | Ready-to-integrate webhook endpoint |
| 🧠 **Session Memory** | In-memory conversation history (last 5 turns) |
| 🎭 **Hinglish Personality** | Friendly Indian AI buddy tone |
| 📖 **Swagger Docs** | Auto-generated API docs at `/docs` |
| 🐳 **Docker Ready** | Dockerfile included |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Pydantic settings (from .env)
│   ├── models/
│   │   └── schemas.py        # Request/response Pydantic models
│   ├── routes/
│   │   ├── chat.py           # POST /chat
│   │   ├── whatsapp.py       # POST /whatsapp-webhook
│   │   └── health.py         # GET /health
│   ├── services/
│   │   ├── ollama_client.py  # Async Ollama HTTP client
│   │   ├── rag.py            # ChromaDB retrieval + ingestion
│   │   └── session.py        # In-memory session manager
│   ├── utils/
│   │   └── scam_detector.py  # Rule-based scam detection
│   └── prompts/
│       └── templates.py      # System prompt + prompt builder
├── data/
│   └── knowledge_base.json   # RAG knowledge chunks
├── chroma_db/                # ChromaDB persistence (auto-created)
├── ingest.py                 # Knowledge base ingestion script
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Ollama** installed and running

### 1. Install Ollama

Download from: https://ollama.ai/download

```bash
# After installing, pull the model
ollama pull llama3.2:3b

# Verify it's running
ollama list
```

### 2. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is pre-configured with defaults. Modify if needed:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=120
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. Ingest Knowledge Base

```bash
python ingest.py
```

This loads the Hinglish knowledge chunks into ChromaDB for RAG.

### 5. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Server will be live at: **http://localhost:8000**

- 📖 Swagger Docs: http://localhost:8000/docs
- 📘 ReDoc: http://localhost:8000/redoc

---

## 📡 API Endpoints

### `GET /health`

Check server and Ollama status.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "ollama": true,
  "model": "llama3.2:3b"
}
```

---

### `POST /chat`

Main chat endpoint.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "bhai mujhe resume tips do",
    "session_id": "abc123"
  }'
```

**Response:**
```json
{
  "reply": "Bhai resume mein projects highlight kar, skills section strong rakh, aur 1 page mein fit kar 😄",
  "scam_detected": false,
  "scam_warning": null,
  "sources": [
    "Resume Tips: Apna resume 1 page mein rakho..."
  ]
}
```

---

### `POST /chat` (Scam Detection Example)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bhai yeh dekh — click this link and win free iPhone! Share OTP fast!",
    "session_id": "abc123"
  }'
```

**Response:**
```json
{
  "reply": "⚠️ Bhai yeh message suspicious lag raha hai!\n  • Suspicious link push\n  • OTP sharing request\nKisi bhi link pe click mat kar aur OTP ya payment mat karna. 🙏\n\nBhai yeh scam hai...",
  "scam_detected": true,
  "scam_warning": "⚠️ Bhai yeh message suspicious lag raha hai!...",
  "sources": []
}
```

---

### `POST /whatsapp-webhook`

Receive WhatsApp messages (Twilio Webhook).

```bash
curl -X POST http://localhost:8000/whatsapp-webhook \
  -d "From=whatsapp:+919876543210" \
  -d "Body=Bhai career advice do" \
  -d "MessageType=text"
```

**Response:**
```xml
<Response></Response>
```

---

## 🐳 Docker

```bash
# Build
docker build -t ai-dost-backend .

# Run (ensure Ollama is accessible)
docker run -p 8000:8000 --env OLLAMA_BASE_URL=http://host.docker.internal:11434 ai-dost-backend
```

---

## 🧪 Testing Quick Commands

```bash
# Health check
curl http://localhost:8000/health

# Simple chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello bhai", "session_id": "test1"}'

# Resume help
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "resume kaise banau?", "session_id": "test1"}'

# Scam test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Click this link to double your crypto!", "session_id": "test2"}'

# Career advice
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "DSA kaise prepare karun placement ke liye?", "session_id": "test1"}'
```

---

## ⚙️ Configuration

All settings are configurable via `.env` or environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:3b` | LLM model name |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `CHROMA_COLLECTION` | `ai_dost_kb` | Collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer model |
| `RAG_TOP_K` | `3` | Number of RAG chunks to retrieve |
| `DEBUG` | `true` | Enable debug logging |

---

## 🏗️ Architecture

```
User Message
    │
    ▼
┌─────────────┐
│ Scam Detect  │──→ Flag if suspicious
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ RAG Retrieve │──→ Fetch relevant knowledge chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Build Prompt │──→ System + Context + History + Query
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Ollama LLM  │──→ Generate Hinglish response
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Session Mgr  │──→ Save to history
└──────┬──────┘
       │
       ▼
   Response
```

---

## 📝 License

MIT — Built with ❤️ for hackathons.
