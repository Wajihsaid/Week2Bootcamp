# Historical RAG Backend - Echoes of History

Professional FastAPI backend for the Historical RAG system with NLP processing, vector search, and role-prompted LLM generation.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── routers/               # API endpoints
│   │   ├── chat.py            # Chat with historical characters
│   │   ├── tts.py             # Text-to-Speech
│   │   └── stt.py             # Speech-to-Text
│   ├── services/              # Core services
│   │   ├── nlp_processor.py   # STAGE 1: Text cleaning & entity extraction
│   │   ├── rag_service.py     # STAGE 2: Document chunking, FAISS, retrieval
│   │   └── llm_service.py     # STAGE 3: Role-prompted generation
│   ├── models/                # Data models
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── characters.py      # Historical character personas
│   └── data/                  # Data storage
│       ├── documents/         # Dataset CSV file goes here
│       └── faiss_index/       # Cached FAISS index & documents
└── requirements.txt
```

## 📋 Prerequisites

- Python 3.9+
- 8GB+ RAM (16GB recommended for local LLM)
- GPU optional (for faster inference)

## 🚀 Installation

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Place Your Dataset

**IMPORTANT:** Copy your historical dataset CSV file to:
```
backend/app/data/documents/historical_events_cleaned_full.csv
```

The dataset should have columns like:
- `name_of_incident` or `event_name`
- `description`, `rag_document`, or similar text fields
- `historical_character`
- `year` or `year_display`

### Step 3: Configure Environment

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Edit `.env` with your settings:

```env
# Basic settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# CORS origins (add your frontend URL)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Model configuration
USE_GPU=false
EMBEDDING_MODEL=all-mpnet-base-v2
HISTORICAL_BERT_MODEL=dbmdz/bert-base-historic-english-cased

# LLM (optional - leave empty for context-only mode)
LLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0

# External LLM API (recommended for production)
# EXTERNAL_LLM_API_URL=https://api.openai.com/v1/chat/completions
# EXTERNAL_LLM_API_KEY=your-api-key
# EXTERNAL_LLM_MODEL=gpt-3.5-turbo

# RAG settings
CHUNK_SIZE=250
CHUNK_OVERLAP=40
TOP_K_RETRIEVAL=5
MAX_CONTEXT_LENGTH=2000
BERT_RERANK_WEIGHT=0.3

# Data paths
DATASET_PATH=app/data/documents/historical_events_cleaned_full.csv
FAISS_INDEX_PATH=app/data/faiss_index
```

## 🎯 Running the Server

### Development Mode

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Chat with Historical Characters
```
POST /api/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Tell me about the Battle of Cannae"}
  ],
  "characterId": "hannibal",
  "stream": true
}
```

**Available Characters:**
- `hannibal` - Hannibal Barca
- `hamilcar` - Hamilcar Barca
- `elyssa` - Queen Dido (Elissa)
- `uqba` - Uqba ibn Nafi
- `kahina` - Kahina (Amazigh Queen)
- `ibn-khaldoun` - Ibn Khaldoun
- `abu-zakariya` - Abu Zakariya Yahya
- `kheireddine` - Kheireddine Barbarossa
- `farhat-hached` - Farhat Hached

### Text-to-Speech
```
POST /api/tts
Content-Type: application/json

{
  "text": "I am Hannibal Barca",
  "characterId": "hannibal"
}

Response: audio/mpeg file
```

### Speech-to-Text
```
POST /api/stt
Content-Type: multipart/form-data

file: audio_file.wav

Response:
{
  "text": "Transcribed text",
  "confidence": 0.95
}
```

## 🔧 System Stages

### STAGE 1: NLP Processing
- **Text Cleaning:** Date normalization, name resolution
- **Entity Extraction:** Historical BERT-based entity recognition
- **Context Extraction:** Period, civilization, and key figure detection

### STAGE 2: RAG Pipeline
- **Document Chunking:** Overlapping chunks with metadata
- **Embedding Generation:** Sentence-Transformers (768-dim)
- **FAISS Indexing:** Fast approximate nearest neighbor search
- **Hybrid Retrieval:** Semantic search + BERT re-ranking

### STAGE 3: LLM Generation
- **Role Prompting:** Character-specific system prompts
- **RAG Grounding:** Context-constrained generation
- **Anti-Hallucination:** Strict rules to prevent invented facts
- **Streaming Support:** Real-time response generation

## 📊 First-Time Startup

On first startup, the system will:

1. **Load Historical BERT** (dbmdz/bert-base-historic-english-cased)
2. **Load Sentence Transformer** (all-mpnet-base-v2)
3. **Process Dataset:**
   - Clean text
   - Create document chunks
   - Generate embeddings
   - Build FAISS index
4. **Cache Everything** (subsequent startups are instant)

This takes 5-15 minutes depending on dataset size.

## 🎭 Character Personas

Each character has:
- **Unique voice** and speaking style
- **Historical context** (time period, role, civilization)
- **Strict RAG rules** to prevent hallucination
- **Character-specific voice** for TTS

Example: Hannibal speaks as a military strategist with firsthand battle knowledge, while Ibn Khaldoun analyzes events through the lens of historiography.

## 🔗 Frontend Integration

Update your frontend `.env`:
```env
VITE_API_URL=http://localhost:8000
```

The backend is CORS-enabled and compatible with your existing React frontend.

## 🐛 Troubleshooting

### "Dataset not found"
Place `historical_events_cleaned_full.csv` in `backend/app/data/documents/`

### Models downloading slowly
First run downloads ~2GB of models. Be patient!

### Out of memory
- Set `USE_GPU=false` in `.env`
- Reduce `CHUNK_SIZE` to 150
- Don't load local LLM (leave `LLM_MODEL` empty)

### External LLM not working
- Check `EXTERNAL_LLM_API_KEY` is set
- Verify API URL format
- Test with OpenAI, Anthropic, or any OpenAI-compatible API

## 📈 Performance Optimization

### Use External LLM (Recommended)
Set up external API (OpenAI/Anthropic) for best results:
```env
EXTERNAL_LLM_API_URL=https://api.openai.com/v1/chat/completions
EXTERNAL_LLM_API_KEY=your-key
EXTERNAL_LLM_MODEL=gpt-3.5-turbo
```

### Enable GPU
```env
USE_GPU=true
```

### Adjust Retrieval
```env
TOP_K_RETRIEVAL=3          # Fewer docs = faster
BERT_RERANK_WEIGHT=0.0      # Disable re-ranking = faster
```

## 📝 Logging

Logs are output to console with structured information:
- INFO: System initialization, requests
- WARNING: Fallbacks, missing data
- ERROR: Failures, exceptions

## 🔒 Security Notes

- Add authentication middleware for production
- Rate limit the `/api/chat` endpoint
- Validate file uploads in `/api/stt`
- Keep API keys in `.env` (never commit)

## 🎓 Citation

This system implements:
- Historical BERT: [dbmdz/bert-base-historic-english-cased](https://huggingface.co/dbmdz/bert-base-historic-english-cased)
- Sentence-Transformers: [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
- FAISS: Facebook AI Similarity Search
- RAG: Retrieval-Augmented Generation

## 📧 Support

For issues:
1. Check logs for errors
2. Verify dataset is in correct location
3. Ensure all dependencies installed
4. Check `.env` configuration

---

Built with ❤️ for the Echoes of History project

