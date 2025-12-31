# RAG Chatbot Backend

Backend API for the RAG (Retrieval Augmented Generation) chatbot integrated with the Physical AI & Humanoid Robotics textbook.

## Overview

This FastAPI-based backend provides:
- RAG pipeline: ingestion → chunking → embeddings → vector store → retrieval → response
- API endpoints for chat interactions and content management
- Integration with Qdrant vector database and Neon Postgres
- OpenAI Agent-based response generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with required environment variables (see `.env.template`)

3. Run the application:
```bash
cd backend
uvicorn src.api.main:app --reload --port 8000
```

## API Endpoints

- `/chat/ask` - Submit questions and receive textbook-based answers
- `/embed/chunk-and-store` - Ingest textbook content
- `/documents/mapping` - Get document metadata
- `/health` - Health check endpoint
- `/docs` - Interactive API documentation

## Environment Variables

See `.env.template` for required environment variables.

## Architecture

- FastAPI for web framework
- Pydantic for data validation
- OpenAI SDK for embeddings and agent responses
- Qdrant Client for vector database operations
- asyncpg for PostgreSQL operations
- SQLAlchemy for ORM operations