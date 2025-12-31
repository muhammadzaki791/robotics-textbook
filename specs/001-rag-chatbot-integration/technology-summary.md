# RAG Chatbot Integration: Technology Summary

## Project Overview
The RAG (Retrieval Augmented Generation) Chatbot has been integrated into the Physical AI & Humanoid Robotics textbook to provide students with an AI-powered Q&A system that answers questions based strictly on textbook content.

## Architecture Components

### Backend (FastAPI)
- **Framework**: FastAPI for high-performance API development
- **Language**: Python 3.11
- **Key Dependencies**:
  - OpenAI SDK for embeddings and agent-based responses
  - Qdrant Client for vector database operations
  - asyncpg for asynchronous PostgreSQL operations
  - Pydantic for data validation
  - SQLAlchemy for ORM operations

### Frontend Integration
- **Framework**: React components for chatbot UI
- **Integration**: Embedded as widget in Docusaurus textbook
- **Features**: Text selection detection, conversation history, responsive design

### Storage Systems
- **Qdrant Cloud Free Tier**: Vector database for textbook content embeddings
- **Neon Serverless Postgres**: Metadata storage for document mapping and session management

## Key Implementation Details

### RAG Pipeline
1. **Text Chunking**: Textbook content is split into semantically meaningful chunks
2. **Embedding Generation**: OpenAI embeddings created for each chunk
3. **Vector Storage**: Embeddings stored in Qdrant with metadata
4. **Retrieval**: Semantic search to find relevant content
5. **Response Generation**: OpenAI Agents create grounded responses

### Selected-Text Mode
- JavaScript detects text selection in the textbook
- API endpoint restricts retrieval to only selected content
- Provides focused answers based on highlighted text

### API Endpoints
- `POST /chat/ask`: Main Q&A endpoint
- `POST /embed/chunk-and-store`: Content ingestion
- `POST /embed/update`: Content updates
- `GET /documents/mapping`: Document metadata retrieval
- `GET /documents/search`: Content search
- `GET /health`: System health monitoring
- `GET /stats`: Usage statistics

## Technical Constraints
- Free-tier infrastructure (Qdrant Cloud Free Tier, Neon Free Tier)
- No external web access - responses grounded only in textbook content
- Static Docusaurus site compatibility
- Sub-300ms response time requirement
- Privacy-compliant data handling

## Data Model
- **DocumentChunk**: Text content with embeddings and metadata
- **ChatQuery**: User questions with context and session info
- **ChatResponse**: System responses with source references
- **UserSession**: Session management with privacy considerations
- **DocumentMetadata**: Textbook organization and mapping

## Security & Privacy
- API key authentication
- Rate limiting to prevent abuse
- Minimal data logging
- No personal information storage
- Protection against prompt injection

## Deployment
- Serverless platforms: Railway, Fly.io, or Vercel
- Static site hosting for Docusaurus integration
- Separate backend service for API operations