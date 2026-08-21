# Customer Support AI

A multi-agent, RAG-powered customer support assistant.

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+)
- **AI/RAG:** Sentence Transformers (`all-MiniLM-L6-v2`) + FAISS + configurable LLM (OpenAI or Anthropic)
- **Database:** PostgreSQL (production) or SQLite (local dev, zero setup)
- **Auth:** JWT + bcrypt password hashing

## Project Status — Complete

| Phase | Description | Status |
|---|---|---|
| 1 | Project setup | Done |
| 2 | Backend foundation (CORS, logging, health check, error handling) | Done |
| 3 | Auth & database (JWT, register/login, protected routes) | Done |
| 4 | Knowledge base & RAG (chunking, embeddings, FAISS, sample docs) | Done |
| 5 | Multi-agent system (5 agents + router + intent detection) | Done |
| 6 | LLM integration (OpenAI/Anthropic, grounded fallback) | Done |
| 7 | Conversation memory (per-user history, sessions) | Done |
| 8 | Frontend (login/register/dashboard/chat UI) | Done |
| 9 | Response aggregation & escalation | Done |
| 10 | Testing (20 automated tests, all passing) | Done |
| 11 | Final review | Done |

## Architecture

```
User -> React Frontend -> FastAPI Backend -> Intent Detection -> Agent Router
     -> [Billing | Technical | Product | Complaint | FAQ] Agents (1 or more)
     -> RAG Retrieval (FAISS + sentence-transformers) -> LLM -> Response Aggregator
     -> Final Response (+ conversation persisted to DB)
```

Multi-agent example (built into the test suite): "I paid yesterday, but my
Premium account is still locked" routes to **both** the Billing agent and
the Technical agent, and the aggregator merges their answers into one
de-duplicated response.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- (Optional) PostgreSQL, if you don't want to use the SQLite dev mode
- (Optional) An OpenAI or Anthropic API key, for fully conversational LLM responses

> **No API key? No problem.** If `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` isn't
> set, the system automatically falls back to a grounded response mode that
> surfaces the retrieved knowledge-base content directly -- the whole app
> (auth, routing, RAG, memory, multi-agent aggregation) works end-to-end
> without any LLM key. This is useful for testing and demos.

## Setup (Windows / VS Code terminal)

**1. Backend:**
```powershell
cd customer-support-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and, at minimum, decide your database mode:
- **Easiest (no install needed):** set `DATABASE_TYPE=sqlite`
- **Production-like:** keep `DATABASE_TYPE=postgres` and set `POSTGRES_URL` to a running Postgres instance

Optionally add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (and set `LLM_PROVIDER` accordingly) for full conversational responses.

**2. Build the RAG index** (reads `knowledge_base/*.txt`, builds the FAISS index):
```powershell
python -m backend.rag.ingest
```
This also happens automatically on first server startup if no index exists yet, so this step is optional but recommended to run once up front.

**3. Frontend** (new terminal):
```powershell
cd customer-support-ai\frontend
npm install
```

## Running the app

```powershell
# Terminal 1 - backend
cd customer-support-ai
venv\Scripts\activate
uvicorn backend.main:app --reload

# Terminal 2 - frontend
cd customer-support-ai\frontend
npm run dev
```

- Backend: http://localhost:8000 (health check: http://localhost:8000/api/v1/health)
- Frontend: http://localhost:5173

Open the frontend, register an account, and start chatting. Try:
- "How much does the Pro plan cost?" -> routes to Product agent
- "I was charged twice this month" -> routes to Billing agent
- "I paid yesterday, but my Premium account is still locked" -> routes to **Billing + Technical**
- "This is unacceptable, I want to speak to a manager" -> routes to Complaint agent and **escalates** the conversation

## Running tests

```powershell
cd customer-support-ai
venv\Scripts\activate
pytest backend/tests/ -v
```

20 tests cover authentication, intent routing (including the multi-agent
case above), RAG chunking/indexing/search, conversation memory, and
escalation detection. Tests use a mocked embedding function so they run
fully offline without downloading model weights.

## Project Structure

```
customer-support-ai/
├── frontend/
│   ├── src/
│   │   ├── components/     # Sidebar, ChatWindow, MessageBubble, TypingIndicator, ProtectedRoute
│   │   ├── pages/          # Login, Register, Dashboard
│   │   ├── services/       # api.js (axios), auth.js, chat.js
│   │   ├── hooks/          # useAuth.js
│   │   ├── context/        # AuthContext.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── backend/
│   ├── api/                # auth.py, chat.py, health.py, deps.py
│   ├── agents/              # billing, technical, product, complaint, faq, intent_detector, router, base
│   ├── rag/                  # embeddings, chunking, loader, vector_store, ingest
│   ├── vectorstore/           # FAISS index files (generated)
│   ├── database/                # session.py (SQLAlchemy engine/session)
│   ├── models/                    # user.py, conversation.py
│   ├── schemas/                     # auth.py, chat.py (Pydantic)
│   ├── services/                      # llm.py, aggregator.py, chat_service.py
│   ├── tests/                          # 20 pytest tests
│   ├── config.py
│   └── main.py
│
├── knowledge_base/                        # sample docs for "NimbusCloud" (fictional company)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Notes on the multi-agent system

Intent detection uses weighted keyword matching (see
`backend/agents/intent_detector.py`) rather than an LLM call -- this keeps
routing fast, deterministic, and fully testable offline, and a message can
match multiple domains simultaneously (multi-label), which is what enables
true multi-agent responses. Each specialized agent then independently
retrieves RAG context biased toward its own knowledge-base document and
generates its part of the answer; the aggregator merges multiple agent
outputs, removes duplicate sentences, and appends an escalation notice when
warranted.

## Extending this project

- **Add a new agent:** create a class in `backend/agents/` extending `BaseAgent`, add keywords to `intent_detector.py`, register it in `router.py`'s `AGENT_REGISTRY`.
- **Add knowledge:** drop a `.txt` or `.pdf` file into `knowledge_base/` and re-run `python -m backend.rag.ingest`.
- **Switch LLM provider:** set `LLM_PROVIDER=anthropic` (or `openai`) and the matching API key in `.env`.
- **Switch to MongoDB:** the codebase currently uses SQLAlchemy (Postgres/SQLite); swapping to Mongo would mean replacing `backend/database/session.py` and the model classes with Motor-based equivalents -- the rest of the app only depends on the `get_db` dependency, so the blast radius is contained to that layer.
