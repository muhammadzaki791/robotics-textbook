# Environment Variables for RAG Chatbot

This document describes all the environment variables required for the RAG Chatbot system.

## Required Environment Variables

### API Keys
- `COHERE_API_KEY` - Your Cohere API key for generating embeddings
- `GEMINI_API_KEY` - Your Google Gemini API key for text generation

### Database Configuration
- `DATABASE_URL` - Connection string for the Neon PostgreSQL database

### Qdrant Configuration
- `QDRANT_HOST` - Host address for Qdrant vector database (default: localhost)
- `QDRANT_PORT` - Port for Qdrant vector database (default: 6333)
- `QDRANT_API_KEY` - API key for Qdrant (optional, if authentication is enabled)

### Security
- `SECRET_KEY` - Secret key for JWT token generation

## Optional Environment Variables

### Server Configuration
- `HOST` - Host address for the API server (default: 0.0.0.0)
- `PORT` - Port for the API server (default: 8000)
- `DEBUG` - Enable debug mode (default: False)

### CORS Configuration
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins (default: ["*"])

### Rate Limiting
- `RATE_LIMIT_REQUESTS` - Number of requests allowed per window (default: 100)
- `RATE_LIMIT_WINDOW` - Time window in seconds (default: 60)

### Database Pool Configuration
- `DATABASE_POOL_SIZE` - Size of the database connection pool (default: 20)
- `DATABASE_POOL_OVERFLOW` - Number of overflow connections (default: 0)

### Embedding Configuration
- `EMBEDDING_BATCH_SIZE` - Number of texts to embed in a single batch (default: 10)
- `EMBEDDING_MODEL` - Cohere model to use for embeddings (default: embed-english-v3.0)

### Retrieval Configuration
- `RETRIEVAL_TOP_K` - Number of top results to retrieve (default: 5)
- `RETRIEVAL_MIN_SCORE` - Minimum similarity score for valid results (default: 0.5)

### Text Processing
- `CHUNK_SIZE` - Size of text chunks in tokens (default: 512)
- `CHUNK_OVERLAP` - Overlap between chunks in tokens (default: 51)

### Session Configuration
- `SESSION_EXPIRY_HOURS` - Session expiry time in hours (default: 24)

### Model Configuration
- `GEMINI_MODEL` - Google Gemini model to use for generation (default: gemini-pro)
- `MAX_TOKENS` - Maximum tokens for generation (default: 1000)
- `TEMPERATURE` - Temperature for generation (default: 0.1)

## Example .env File

```env
# API Keys
COHERE_API_KEY=your_cohere_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=your_neon_database_connection_string_here

# Qdrant (optional if using local instance)
QDRANT_HOST=localhost
QDRANT_PORT=6333
# QDRANT_API_KEY=your_qdrant_api_key_if_needed

# Security
SECRET_KEY=your_secret_key_here

# Server (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS (optional)
ALLOWED_ORIGINS=["*"]

# Other configurations (optional)
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.5
EMBEDDING_BATCH_SIZE=10
```