# Nodus Decoded AI Chatbot
A conversational AI chatbot built for Nodus Decoded, a boutique AI transformation consultancy. The chatbot answers visitor questions about services, captures leads, and supports voice interaction — all running on a free tech stack.

---

## What it does

- Greets website visitors and asks for their name and email before chatting
- Answers questions about Nodus Decoded Company using AI trained on company documents
- Captures and stores visitor details as leads in a PostgreSQL database
- Supports voice input — speak your question, review the text, then send
- Streams responses word by word like ChatGPT
- Logs every conversation for analytics
- download leads and conversation as csv file

---

## Tech Stack

**Frontend**
- React with Vite
- Tailwind CSS for styling
- Hosted on Render (free)

**Backend**
- Python with FastAPI
- LangChain for AI orchestration
- Groq API (llama-3.1-8b-instant) for generating responses
- Groq Whisper for voice-to-text transcription
- ChromaDB as the local vector database
- Sentence Transformers for embedding documents locally

**Database**
- PostgreSQL for storing leads and conversation logs

**Deployment**
- Frontend: Render static site
- Backend: Railway or vercel or Render web service

---

## Project Structure

```
nodus-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/          # Chat, lead, voice, and dashboard endpoints
│   │   ├── core/         # Config and session management
│   │   ├── models/       # Request and response schemas
│   │   ├── rag/          # AI pipeline: intent, embedder, retriever, chain
│   │   └── utils/        # Database connections
│   ├── knowledge_base/
│   │   └── raw/          # Add Nodus content files here
│   ├── models/           # Cached sentence transformer model
│   ├── scripts/
│   │   └── ingest.py     # Builds ChromaDB from knowledge base files
|   |   └── backup_db.py  # easy way download backup leads and conversation csv files in backend/Exports/
|   |   └── pg_backup.py  # traditional way of direct postgres.sql db backup in backend/Exports/
|   |   └── ER Diagram    # ER diagram png file
|   |   └── ERD_schema.sql# ER diagram schema.sql
│   ├── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   ├── start.sh          # Production startup script
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/   # Chat UI components
    │   ├── hooks/        # useChat, useStream, useVoice
    │   ├── pages/        # Dashboard page
    │   └── services/     # API calls
    ├── index.html
    └── package.json
```

---

## Local Setup

### Requirements
- Python 3.11
- Node.js 18 or higher
- PostgreSQL 14 or higher installed locally

---

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nodus-chatbot.git
cd nodus-chatbot
```

---

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Copy the environment file and fill in your keys:

```bash
cp .env.example .env
```

Open `.env` and add:

```
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/nodus_chatbot
```

---

### 3. Set up the database

Create the database in PostgreSQL:

```sql
CREATE DATABASE nodus_chatbot;
```

Tables are created automatically when the server starts for the first time.

---

### 4. Add knowledge base content

Drop your Nodus Decoded content files into:

```
backend/knowledge_base/raw/
```

Supported file types: `.md`, `.txt`, `.pdf`, `.json`

For FAQ content use `faq.json` in this format:

```json
{
  "faqs": [
    { "q": "What services do you offer?", "a": "We offer..." }
  ]
}
```

---

### 5. Build the knowledge base

```bash
cd backend
python scripts/ingest.py
```

This reads your content files, splits them into chunks, embeds them locally, and saves to ChromaDB. Run this again whenever you update the knowledge base.

---

### 6. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

---

### 7. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM and Whisper — free at console.groq.com |
| `DATABASE_URL` | PostgreSQL connection string |
| `CHROMA_PERSIST_DIR` | Where ChromaDB is stored on disk (default: `./chroma_db`) |
| `SIMILARITY_THRESHOLD` | Minimum similarity score for RAG retrieval (default: `0.1`) |
| `RETRIEVER_K` | Number of chunks to retrieve per query (default: `3`) |
| `CHUNK_SIZE` | Document chunk size for ingestion (default: `400`) |
| `CHUNK_OVERLAP` | Chunk overlap for context continuity (default: `50`) |
| `CONTEXT_WINDOW_TURNS` | Number of past conversation turns passed to LLM (default: `6`) |
| `APP_ENV` | Set to `production` on hosted servers |
| `CORS_ORIGIN` | Frontend URL for CORS (e.g. your Vercel or Render URL) |

---

## How the pipeline works:

1. User submits name and email — saved to PostgreSQL leads table
2. User sends a message
3. Groq classifies the message intent as general, lead, or fallback
4. For general queries the message is embedded locally using the sentence transformer model
5. ChromaDB finds the most relevant chunks from the knowledge base
6. Those chunks are injected into the prompt alongside conversation history
7. Groq generates a grounded response based only on the retrieved context
8. Response streams back to the frontend token by token
9. The full conversation turn is logged to PostgreSQL

---

## Voice feature

Click the microphone button in the chat input to speak your question. Recording stops when you click again. The audio is transcribed by Groq Whisper and the text appears in the input box for you to review before sending.

For natural bot voice responses, integrate ElevenLabs by adding your API key:

```
ELEVENLABS_API_KEY=your_key
```

Free tier provides 10,000 characters per month — approximately 10-15 minutes of speech.

---

## Updating the knowledge base

1. Add or edit files in `backend/knowledge_base/raw/`
2. Run `python scripts/ingest.py`
3. Restart the backend server

If deployed on Railway, push to GitHub and Railway redeploys automatically. The ingest script runs on startup if ChromaDB is missing.

---

## Database Backup & ER Diagram

### ER Diagram

The database schema ER diagram is available in `backend/scripts/ERD_schema.sql`. The full table structure including constraints and foreign keys is in it.
A visual version was generated using pgAdmin 4 also in it.

---

### CSV Backup

Exports all leads and conversation logs as CSV files. Use this when you need data in Excel.

```bash
cd backend
python scripts/backup_db.py
```
Output saved to `backend/exports/`:
```
leads_backup_YYYY-MM-DD.csv
conversation_logs_backup_YYYY-MM-DD.csv
```
Run this at the end of every week, before any major deployment, or anytime you need the latest lead data in Excel format.

---

### Full PostgreSQL Backup

Creates a complete `.sql` dump of the entire database including structure and all data.

```bash
cd backend
python scripts/pg_backup.py
```
Output saved to `backend/exports/`:
```
nodus_chatbot_backup_YYYY-MM-DD_HH-MM.sql
```
To restore on any machine:
```bash
psql -U postgres -d nodus_chatbot -f nodus_chatbot_backup_YYYY-MM-DD.sql
```
Run this once a week, before moving to a new server.
---

### What each backup contains

| File | Contains |
|------|----------|
| `leads_backup.csv` | All names, emails, phone numbers, and requirements captured by the chatbot |
| `conversation_logs_backup.csv` | Every message and bot reply with intent classification and response time |
| `nodus_chatbot_backup.sql` | Complete database — structure, all data, indexes, and constraints |

> Backup files are saved to `backend/exports/` which is excluded from GitHub via `.gitignore`. They live only on your local machine or server. 
### Never commit backup files to GitHub as they contain real user data.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/stream` | SSE streaming chat endpoint |
| POST | `/api/chat/sync` | Non-streaming chat for testing |
| POST | `/api/lead/` | Submit lead details |
| GET | `/api/lead/health` | Check database connection |
| POST | `/api/voice/transcribe` | Transcribe audio to text |
| POST | `/api/voice/speak` | Convert text to speech |
| GET | `/health` | Backend health check |

---
## COST BREAKDOWN 
| Service                     | Usage                                                                                                              | Cost                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| Groq API (LLM + Whisper)    | 14,400 requests/day; model/token limits also apply                                                                 | Free tier, 14,400 RPD; paid after limits                  |
| Sentence Transformers       | Local CPU inference; no API usage limit                                                                            | Free forever                                              |
| ChromaDB                    | Local vector storage; limited only by available disk/RAM                                                           | Free forever                                              |
| PostgreSQL                  | Lead and log storage; e.g. Neon Free: 0.5 GB/project, 50 CU-hours/month, 5 GB egress/month                         | Free tier, usage-based paid after limits                  |
| Railway backend (optional)  | Hosting; Free: 0.5 GB RAM, 1 vCPU, 0.5 GB volume storage                                                           | Free trial: $5 credit/30 days; then Free $1/month credit  |
| Railway frontend (optional) | Hosting; Free: 0.5 GB RAM, 1 vCPU, 0.5 GB volume storage                                                           | Free trial: $5 credit/30 days; then Free $1/month credit  |
| Render backend (optional)   | Hosting; 512 MB RAM, 0.1 CPU, 750 instance-hours/month; spins down after 15 min inactivity                         | Free tier, paid services from ~$7/month                   |
| Render frontend (optional)  | Static site hosting; free deployment, subject to workspace bandwidth/build limits                                  | Free tier, paid plans available                           |
| Vercel backend (optional)   | Serverless/API hosting; Hobby includes 1M function invocations/month, 4 CPU-hours/month and 100 GB bandwidth/month | Free tier, Pro $20/month + usage                          |
| Vercel frontend (optional)  | Frontend hosting; Hobby includes 100 GB/month bandwidth and 1M function invocations/month                          | Free tier, Pro $20/month + usage                          |
| ElevenLabs (optional)       | Text-to-speech; 10,000 characters/month on Free plan                                                               | Free tier, paid from ~$6/month                            |
| **Total**                   |                                                                                                                    | **$0 now, ~$5–$20+/month production**                     |
