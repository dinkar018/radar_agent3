# Radar Research Paper Implementation Agent

A full-stack AI agent system that takes a research paper, understands it in the context of your radar hardware setup, generates Python code implementing the paper's methodology on your radar data, executes it in a Docker sandbox, and returns results.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────┐ │
│  │Dashboard │ │Knowledge Base│ │ Experiments │ │ Results │ │
│  └──────────┘ └──────────────┘ └────────────┘ └─────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ KB API  │  │Paper API │  │  Agent    │  │ WebSocket │  │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘  └───────────┘  │
│       │             │              │                         │
│  ┌────▼─────────────▼──────────────▼─────┐                  │
│  │         RAG Pipeline                   │                  │
│  │  PDF Parse → Chunk → Embed → ChromaDB │                  │
│  └────────────────────────────────────────┘                  │
│       │                                                      │
│  ┌────▼──────────────────────────────────┐                  │
│  │        LangGraph Agent                │                  │
│  │  Retrieve → Generate → Execute →      │                  │
│  │  Reflect → Retry/Finalize            │                  │
│  └──────────────────┬───────────────────┘                  │
│                     │                                       │
│  ┌──────────────────▼───────────────────┐                  │
│  │     Docker Sandbox Executor           │                  │
│  │  numpy, scipy, matplotlib, pandas     │                  │
│  └───────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, shadcn/ui, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy (async), SQLite |
| RAG | ChromaDB, sentence-transformers |
| Agent | LangGraph, Google Gemini API |
| PDF Parsing | pymupdf4llm |
| Code Sandbox | Docker (isolated containers) |
| Scientific | numpy, scipy, matplotlib, pandas |

## Radar Hardware

- **Model**: TI IWR1843BOOST
- **TX Antennas**: 3
- **RX Antennas**: 4
- **Virtual Channels**: 12 (MIMO)
- **Frequency**: 76-81 GHz
- **ADC Samples**: 256 per chirp

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- Google Gemini API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Generate synthetic test data
python generate_synthetic_data.py

# Build Docker sandbox
docker build -t radar-sandbox:latest ../sandbox/

# Start server
python run.py
```

The API will be available at http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The UI will be available at http://localhost:3000

### 3. Using the System

1. **Upload Knowledge Base**: Go to Knowledge Base → upload your radar datasheet and hardware setup documents
2. **Upload Radar Data**: Upload your collected radar data files (.npy format)
3. **Create Experiment**: 
   - Upload a research paper (PDF)
   - Select your radar data files
   - Add optional instructions
   - Click "Start Experiment"
4. **View Results**: Watch real-time execution, view generated code, plots, and metrics

## API Endpoints

### Knowledge Base
- `POST /api/kb/upload` — Upload KB document
- `GET /api/kb/documents` — List documents
- `DELETE /api/kb/documents/{id}` — Delete document
- `POST /api/kb/search` — Semantic search

### Radar Data
- `POST /api/data/upload` — Upload data file
- `GET /api/data/files` — List data files

### Experiments
- `POST /api/experiments` — Create & run experiment
- `GET /api/experiments` — List experiments
- `GET /api/experiments/{id}` — Get experiment details
- `POST /api/experiments/{id}/rerun` — Re-run experiment

### WebSocket
- `WS /ws/experiments/{id}` — Real-time execution updates

## Project Structure

```
radar_agent3/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/                # Config, database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # Route handlers + WebSocket
│   │   ├── agent/               # LangGraph agent engine
│   │   └── services/            # Business logic + RAG
│   ├── data/                    # File storage
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages
│       ├── components/          # React components
│       ├── lib/                 # API client, utils
│       └── hooks/               # React hooks
├── sandbox/
│   └── Dockerfile               # Scientific Python sandbox
└── README.md
```

## License

MIT
