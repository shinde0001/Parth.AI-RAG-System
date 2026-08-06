# Parth.AI - AI Chatbot using RAG

A production-ready, highly modular Retrieval-Augmented Generation (RAG) system built with Clean Architecture. It features a modern, Claude-inspired React frontend and a powerful FastAPI backend.

<img width="1834" height="960" alt="image" src="https://github.com/user-attachments/assets/ee0125c8-677d-4d48-8771-8b84c88558a5" />


## Features
- **Multi-Source Ingestion**: Upload PDF, DOCX, TXT, Markdown files, or **paste Web Links** for automatic scraping.
- **Hybrid Search**: Combines Dense (Semantic) and Sparse (BM25 Keyword) retrieval using Reciprocal Rank Fusion (RRF) for highly accurate answers.
- **Clean Architecture**: Decoupled domain models, port interfaces, and infrastructure adapters.
- **Cost Effective**: Uses local HuggingFace sentence-transformers (`all-MiniLM-L6-v2`) for embeddings and ChromaDB for vector storage.
- **LLM Integration**: Powered by Google's free **Gemini Flash** API for blazing fast, intelligent context-aware responses.
- **Optional Reranker**: Cross-encoder reranking (`BAAI/bge-reranker-large`) available via `RERANKER_ENABLED=true` env var for enhanced accuracy.
- **Beautiful UI**: Built with React, Vite, and Lucide icons for a premium, interactive user experience.

## Tech Stack
- **Backend API**: FastAPI, Pydantic, Uvicorn, BeautifulSoup4 (Web Scraping)
- **Frontend UI**: React, TypeScript, Vite
- **Vector Store**: ChromaDB
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **LLM**: Google Gemini (`google-genai` SDK)
- **Sparse Retriever**: rank_bm25

---

## 🚀 Quick Start (Local Development)

### 1. Configure your API Key
Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
Copy the example environment file and add your key:
```bash
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

### 2. Install Dependencies
Make sure you have Python 3 and Node.js installed.
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Start the Project
You can easily start both the backend API and the frontend dashboard with a single command:
```bash
./start.sh
```

Once running, simply click the link in your terminal to open the dashboard:
👉 **http://localhost:5173**

To stop the servers, just press `CTRL+C` in your terminal.

---

## Architecture details
This project follows Clean Architecture principles:
- `src/core/`: Domain models and Port interfaces (ABCs). Completely dependency-free.
- `src/adapters/`: Infrastructure implementations (ChromaDB, Gemini, PDF Loaders) that satisfy the Ports.
- `src/services/`: Application orchestrators (Ingestion, Retrieval, Chat) that use Ports to perform business logic.
- `src/api/`: FastAPI layer handling HTTP routing and Dependency Injection.
- `frontend/`: React application communicating strictly over REST with the API.

## Testing & Linting
```bash
# Run Python Linter
ruff check .

# Run Tests
pytest tests/
```
