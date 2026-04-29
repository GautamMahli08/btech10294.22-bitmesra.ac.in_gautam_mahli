RagMedic – Clinical RAG Assistant

A Retrieval-Augmented Generation (RAG) based medical assistant that provides source-backed, non-hallucinated answers using trusted medical data.

 Features
 JWT Authentication (Doctor / Admin roles)
 RAG-based Answering (No hallucination)
 Source-backed responses (CDC, WHO, NICE, PubMed)
 Auto-ingestion (fetches data when missing)
 Confidence scoring (High / Medium / Low)
 Query history with sources
 Admin ingestion panel
 Mobile-friendly React U


 Architecture


 How it works
User asks a medical question
Query is converted to embedding
Qdrant retrieves relevant chunks
If insufficient → system fetches data from trusted sources:
World Health Organization
Centers for Disease Control and Prevention
National Institute for Health and Care Excellence
National Library of Medicine (PubMed)



🛠 Tech Stack
Backend
FastAPI
SQLAlchemy
JWT Auth
Sentence Transformers (Embeddings)
Qdrant (Vector DB)
Frontend
React (Vite)
Tailwind CSS
AI / ML
Ollama (Local LLM)
RAG Architecture

Folder Structure
app/
 ├── main.py
 ├── config.py
 ├── database.py
 ├── models.py
 ├── auth/
 ├── rag/
 │    ├── retriever.py
 │    ├── generator.py
 │    ├── embeddings.py
 │    ├── qdrant_store.py
 │    ├── confidence.py
 │    └── gate.py
 │
 ├── ingestion/
 │    ├── website_ingestor.py
 │    ├── auto_ingestor.py
 │    ├── seed_data.py
 │    ├── chunker.py
 │    └── loaders/
 │
frontend/
 ├── src/
 ├── App.jsx
 └── api.js



 Backend setup

python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

docker run -p 6333:6333 qdrant/qdrant


| Endpoint                | Description          |
| ----------------------- | -------------------- |
| POST `/auth/login`      | Login                |
| POST `/auth/register`   | Register             |
| POST `/ask`             | Ask medical question |
| GET `/history`          | Query history        |
| POST `/ingest/pubmed`   | Ingest PubMed        |
| POST `/ingest/cdc-url`  | Ingest CDC page      |
| POST `/ingest/who-url`  | Ingest WHO page      |
| POST `/ingest/nice-url` | Ingest NICE page     |

Data is chunked → embedded → stored in Qdrant
Retrieved context is sent to LLM
LLM generates answer strictly from context
