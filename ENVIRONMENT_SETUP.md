# Environment Setup Guide

This guide explains how to configure the environment variables for the RAG Chatbot system.

## Overview

The RAG Chatbot system consists of:
- **Backend**: FastAPI server handling API requests, embeddings, and text generation
- **Frontend**: React application providing the chatbot UI

Each component requires its own environment configuration.

## Backend Environment Setup

### 1. Navigate to the Backend Directory

```bash
cd backend
```

### 2. Copy the Environment Template

```bash
cp .env .env.local  # or just edit the .env file directly
```

### 3. Required API Keys

You must obtain and configure these API keys:

#### Cohere API Key
1. Go to [Cohere Dashboard](https://dashboard.cohere.com/)
2. Create an account or log in
3. Navigate to the API keys section
4. Create a new API key
5. Add it to your `.env` file:
   ```
   COHERE_API_KEY=your_actual_cohere_api_key_here
   ```

#### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an account or log in
3. Create an API key
4. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

### 4. Database Configuration

#### PostgreSQL Connection
You need a PostgreSQL database connection string. Here are options:

**Option A: Neon (Recommended for Development)**
1. Go to [Neon](https://neon.tech/)
2. Create a free account
3. Create a new project
4. Copy the connection string from the project dashboard
5. Add it to your `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@ep-xxxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

**Option B: Self-hosted PostgreSQL**
1. Set up your own PostgreSQL instance
2. Create a database for the application
3. Configure user permissions
4. Format the connection string as:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

### 5. Qdrant Configuration

#### Running Qdrant Locally (Recommended for Development)
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Then use these settings in your `.env`:
```
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

#### Using Qdrant Cloud (Production)
1. Go to [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create an account and cluster
3. Get your cluster URL and API key
4. Update your `.env`:
   ```
   QDRANT_HOST=your-cluster-url.qdrant.tech
   QDRANT_PORT=6333
   QDRANT_API_KEY=your_actual_api_key_here
   ```

### 6. Security Configuration

#### Secret Key
Generate a strong secret key for JWT tokens (at least 32 characters):

```bash
# Using Python to generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add it to your `.env`:
```
SECRET_KEY=your_very_long_secure_key_here
```

### 7. Complete Backend .env Example

Here's a complete example of a configured backend `.env` file:

```
# API Keys
COHERE_API_KEY=your_cohere_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://username:password@ep-xxxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Security
SECRET_KEY=your_very_long_secure_key_here_must_be_at_least_32_characters_long

# Server (optional)
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Other configurations (optional)
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.5
EMBEDDING_BATCH_SIZE=10
```

## Frontend Environment Setup

### 1. Navigate to the Frontend Directory

```bash
cd frontend
```

### 2. Copy the Environment Template

```bash
cp .env .env.local  # or just edit the .env file directly
```

### 3. API Configuration

#### Backend API URL
Set the URL where your backend server is running:

```
# For local development
REACT_APP_API_BASE_URL=http://localhost:8000

# For production
REACT_APP_API_BASE_URL=https://yourdomain.com/api
```

### 4. Complete Frontend .env Example

Here's a complete example of a configured frontend `.env` file:

```
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000

# Development Configuration
REACT_APP_DEBUG=true

# Timeout Configuration
REACT_APP_REQUEST_TIMEOUT=30000

# Feature Flags
REACT_APP_ENABLE_SELECTED_TEXT=true
REACT_APP_ENABLE_CONTEXTUAL_LEARNING=true
REACT_APP_ENABLE_CONVERSATION_HISTORY=true

# UI Configuration
REACT_APP_CHATBOT_TITLE=Textbook Assistant
REACT_APP_CHAT_INPUT_PLACEHOLDER=Ask a question about the textbook...

# Theming
REACT_APP_PRIMARY_COLOR=#4a6cf7
REACT_APP_SECONDARY_COLOR=#e3f2fd
```

## Environment Variables Reference

### Backend Environment Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `COHERE_API_KEY` | String | Yes | - | Cohere API key for embeddings |
| `GEMINI_API_KEY` | String | Yes | - | Google Gemini API key for text generation |
| `DATABASE_URL` | String | Yes | - | PostgreSQL connection string |
| `QDRANT_HOST` | String | Yes | localhost | Qdrant server host |
| `QDRANT_PORT` | Integer | Yes | 6333 | Qdrant server port |
| `SECRET_KEY` | String | Yes | - | JWT secret key |
| `QDRANT_API_KEY` | String | No | - | Qdrant authentication key |
| `HOST` | String | No | 0.0.0.0 | Server host |
| `PORT` | Integer | No | 8000 | Server port |
| `DEBUG` | Boolean | No | false | Enable debug mode |
| `ALLOWED_ORIGINS` | JSON Array | No | ["*"] | CORS allowed origins |
| `RATE_LIMIT_REQUESTS` | Integer | No | 100 | Rate limit requests per window |
| `RATE_LIMIT_WINDOW` | Integer | No | 60 | Rate limit time window in seconds |
| `DATABASE_POOL_SIZE` | Integer | No | 20 | Database connection pool size |
| `DATABASE_POOL_OVERFLOW` | Integer | No | 0 | Database overflow connections |
| `EMBEDDING_MODEL` | String | No | embed-english-v3.0 | Cohere embedding model |
| `EMBEDDING_BATCH_SIZE` | Integer | No | 10 | Embedding batch size |
| `RETRIEVAL_TOP_K` | Integer | No | 5 | Number of results to retrieve |
| `RETRIEVAL_MIN_SCORE` | Float | No | 0.5 | Minimum similarity score |
| `CHUNK_SIZE` | Integer | No | 512 | Text chunk size in tokens |
| `CHUNK_OVERLAP` | Integer | No | 51 | Chunk overlap in tokens |
| `SESSION_EXPIRY_HOURS` | Integer | No | 24 | Session expiry time |
| `GEMINI_MODEL` | String | No | gemini-pro | Gemini model to use |
| `MAX_TOKENS` | Integer | No | 1000 | Maximum tokens for generation |
| `TEMPERATURE` | Float | No | 0.1 | Generation temperature |
| `QDRANT_COLLECTION_NAME` | String | No | textbook_content | Qdrant collection name |
| `API_TIMEOUT` | Integer | No | 30 | API timeout in seconds |
| `EMBEDDING_VECTOR_SIZE` | Integer | No | 1024 | Expected embedding vector size |

### Frontend Environment Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `REACT_APP_API_BASE_URL` | String | Yes | - | Backend API base URL |
| `REACT_APP_DEBUG` | Boolean | No | true | Enable debug mode |
| `REACT_APP_REQUEST_TIMEOUT` | Integer | No | 30000 | Request timeout in ms |
| `REACT_APP_ENABLE_SELECTED_TEXT` | Boolean | No | true | Enable selected text feature |
| `REACT_APP_ENABLE_CONTEXTUAL_LEARNING` | Boolean | No | true | Enable contextual learning |
| `REACT_APP_ENABLE_CONVERSATION_HISTORY` | Boolean | No | true | Enable conversation history |
| `REACT_APP_CHATBOT_TITLE` | String | No | Textbook Assistant | Chatbot title |
| `REACT_APP_CHAT_INPUT_PLACEHOLDER` | String | No | Ask a question... | Chat input placeholder |
| `REACT_APP_PRIMARY_COLOR` | String | No | #4a6cf7 | Primary theme color |
| `REACT_APP_SECONDARY_COLOR` | String | No | #e3f2fd | Secondary theme color |

## Testing Your Configuration

### 1. Backend Testing

After setting up your backend `.env` file:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend server:
   ```bash
   python -m src.api.main
   # or
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. Visit `http://localhost:8000/health` to test the health endpoint

### 2. Frontend Testing

After setting up your frontend `.env` file:

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the frontend development server:
   ```bash
   npm start
   ```

3. Visit `http://localhost:3000` to access the chatbot UI

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify your API keys are correct and have sufficient quota
2. **Database Connection**: Check your PostgreSQL connection string format
3. **Qdrant Connection**: Ensure Qdrant is running and accessible
4. **CORS Issues**: Check that your frontend URL is allowed in `ALLOWED_ORIGINS`

### Environment Validation

To validate your environment setup, you can create a simple test script that checks if all required environment variables are set:

```python
# backend/env_validation.py
import os
from src.config.settings import settings

def validate_environment():
    required_vars = [
        'COHERE_API_KEY',
        'GEMINI_API_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var):
            missing_vars.append(var)

    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        return False

    print("All required environment variables are set!")
    return True

if __name__ == "__main__":
    validate_environment()
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, unique secret keys**
3. **Rotate API keys regularly**
4. **Use environment-specific configurations**
5. **Implement proper access controls for databases**
6. **Use HTTPS in production**
7. **Set `DEBUG=false` in production**

## Production Considerations

When deploying to production:

1. Use secure, non-default values for all configuration
2. Set up proper logging and monitoring
3. Implement caching for better performance
4. Use production-grade database and vector store
5. Set up proper authentication and authorization
6. Configure SSL/TLS certificates
7. Implement proper error handling and reporting