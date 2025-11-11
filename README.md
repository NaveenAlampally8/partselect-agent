# PartSelect Chat Agent - Instalily AI Case Study

> AI-powered chat assistant for refrigerator and dishwasher parts search, compatibility checking, and installation guidance.

## 📋 Project Overview

This project is a conversational AI agent prototype built for PartSelect, designed to help customers find appliance parts, check model compatibility, and get installation instructions. The system uses a multi-agent RAG architecture with semantic search capabilities to provide accurate, context-aware responses about refrigerator and dishwasher parts.

---

## 🛠️ Tech Stack

### Frontend

- React 18.2
- Vite
- Axios
- React Markdown
- Tailwind CSS

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy
- ChromaDB (vector database)
- sentence-transformers (local embeddings)
- SQLite

### LLM Integration

- Deepseek API (primary)
- OpenAI API (backup)

---

## 🏗️ Architecture Overview

The system uses a modular multi-agent architecture where each agent specializes in specific tasks. A central orchestrator routes queries to the appropriate agent based on intent classification.

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                         │
│              Chat Interface + Streaming Display             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐      │
│  │         ORCHESTRATOR AGENT                          │     │
│  │    (Manages conversation flow & context)            │     │
│  └──────────┬──────────────────────────────────────────┘     │
│             │                                                │
│             ↓                                                │
│  ┌────────────────────────────────────────────────────┐      │
│  │            ROUTER AGENT                             │     │
│  │    (Classifies intent & routes queries)             │     │
│  └──────────┬──────────────────────────────────────────┘     │
│             │                                                │
│        ┌────┴────┬────────┬────────────┬──────────┐          │
│        ↓         ↓        ↓            ↓          ↓          │
│  ┌─────────┐ ┌──────┐ ┌────────┐ ┌─────────┐ ┌──────┐        │
│  │Product  │ │Compat│ │Install │ │Trouble  │ │General│       │
│  │Search   │ │-ility│ │-ation  │ │-shooting│ │Support│       │
│  └─────────┘ └──────┘ └────────┘ └─────────┘ └──────┘        │
│                                                              │
└───────┬────────────────────────────┬─────────────────────────┘
        │                            │
        ↓                            ↓
┌──────────────────┐      ┌─────────────────────────┐
│  SQLite Database │      │  ChromaDB Vector Store  │
│  • Parts (100)   │      │  • Semantic search      │
│  • Models (16)   │      │  • Local embeddings     │
│  • Relationships │      │  • 384-dim vectors      │
└──────────────────┘      └─────────────────────────┘
        │
        ↓
┌──────────────────────────────────────────┐
│        DEEPSEEK API (LLM)                │
│   Natural language understanding         │
│   & response generation                  │
└──────────────────────────────────────────┘
```

**Key Components:**

- **Router Agent**: Intent classification (product search, compatibility, installation, troubleshooting)
- **Product Search Agent**: Semantic search using ChromaDB + SQLite filtering
- **Compatibility Agent**: Model-part relationship checks
- **Installation Agent**: Step-by-step installation guides with time estimates
- **Troubleshooting Agent**: Symptom-based diagnostics and part recommendations

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/seed_data.py

# Generate vector embeddings
cd vector_store && python embeddings.py && cd ..

# Start backend server
python app.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000` and backend at `http://localhost:8000`.

---

## 🔐 Environment Variables

### Backend `.env`

```env
# API Keys
DEEPSEEK_API_KEY=#DeepSeek Api Key

# Database
DATABASE_URL=sqlite:///partselect.db

# Server
HOST=0.0.0.0
PORT=8000

# SSL (for development)
PYTHONHTTPSVERIFY=0
```

### Frontend `.env`

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📊 Sample Data Note

**For this case study, the system uses a small sample dataset (JSON) of 100 refrigerator and dishwasher parts instead of live-scraped data.**

**Why sample data?**

- When scraping real data using Selenium, we encountered issues with unwanted data like `"common_symptoms": ["John W", "Verified Purchase"]` appearing in results
- BeautifulSoup attempts were blocked by the site's bot detection
- Sample data ensures clean, controlled, and reproducible testing
- The backend architecture is **modular and can later integrate with a real API, database, or scraper** without code restructuring

---

## 💻 Usage

### Starting the Application

1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm start`
3. Open browser to `http://localhost:3000`

### Example Queries

**Product Search:**

```
"Show me dishwasher spray arms"
"Find refrigerator ice makers under $100"
```

**Compatibility Check:**

```
"Is PS57956370 compatible with WRF555SDFZ?"
"Which models work with refrigerator water inlet valve PS55946236?"
```

**Installation Help:**

```
"How do I install Refrigerator Door Gasket?"
"Show installation steps for dishwasher pump PS61911325"
"How long does it take to install a spray arm?"
```

**Troubleshooting:**

```
"My ice maker isn't making ice"
"Dishwasher won't drain properly"
"Refrigerator is too warm"
```

---

## 🔄 Extensibility

The architecture is designed for easy scaling and enhancement:

- **Data Layer**: Replace JSON with PostgreSQL or connect to PartSelect API
- **Vector Search**: Already integrated with ChromaDB; can scale to millions of documents
- **Agent System**: Add new specialized agents (e.g., warranty, pricing, returns) by implementing the base agent interface
- **LLM Provider**: Swap Deepseek with OpenAI, Anthropic, or local models by changing the client
- **Caching**: Add Redis for frequent queries
- **Authentication**: Integrate JWT or OAuth2 for user management
- **Multi-language**: Add translation layer before LLM calls

---

## 📁 Project Structure

```
partselect-chat-agent/
├── backend/
│   ├── agents/              # Multi-agent system
│   ├── database/            # SQLite + models
│   ├── vector_store/        # ChromaDB embeddings
│   ├── app.py              # FastAPI app
│   └── parts_data.json     # Sample dataset (100 parts)
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   └── api/            # API client
│   └── package.json
└── README.md
```

---

## 🎯 Key Features

- Multi-agent architecture with specialized domains
- Hybrid search (semantic + structured)
- Conversation memory across multiple turns
- Streaming responses for better UX
- Context-aware follow-up question handling
- Real-time part compatibility checking
- Installation time estimates

---
