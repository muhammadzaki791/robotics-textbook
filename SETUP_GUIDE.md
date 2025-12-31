# RAG Chatbot Setup Guide

This guide explains how to set up and run the RAG Chatbot system with Cohere embeddings and Google Gemini text generation.

## Prerequisites

- Python 3.11 or higher
- Node.js (for frontend development)
- Qdrant vector database
- PostgreSQL database (Neon recommended)

## API Key Requirements

You'll need the following API keys:

1. **Cohere API Key** - For text embeddings
   - Sign up at [cohere.com](https://cohere.com)
   - Get your API key from the dashboard

2. **Google Gemini API Key** - For text generation
   - Get your API key from [Google AI Studio](https://aistudio.google.com/)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with your API keys:
```env
COHERE_API_KEY=your_cohere_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=your_postgres_connection_string
SECRET_KEY=your_secret_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the System

### Backend Server

1. Start the backend API server:
```bash
cd backend
python -m src.api.main
# or
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Frontend Development Server

1. Start the frontend development server:
```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Docusaurus Integration

To integrate the chatbot with your Docusaurus site:

1. Copy the embed script from `frontend/static/chatbot-embed.js` to your Docusaurus static directory
2. Add the script to your Docusaurus HTML template or pages where you want the chatbot to appear

## Textbook Content Ingestion

To add your textbook content to the system:

1. Place your textbook content in the `docs/` directory in Markdown format
2. Run the ingestion script to process and embed the content:
```bash
cd backend
python -m src.scripts.ingest_documents
```

This will chunk the content, generate embeddings using Cohere, and store them in Qdrant.

## Configuration

### Environment Variables

See `ENVIRONMENT_VARIABLES.md` for a complete list of configuration options.

### Key Configuration Options

- `EMBEDDING_MODEL`: Cohere model to use (default: `embed-english-v3.0`)
- `GEMINI_MODEL`: Gemini model to use (default: `gemini-pro`)
- `RETRIEVAL_TOP_K`: Number of results to retrieve (default: 5)
- `RETRIEVAL_MIN_SCORE`: Minimum similarity score (default: 0.5)

## Features

### 1. Basic Question Answering
- Students can ask questions about textbook content
- Responses are grounded in textbook content only
- Source citations provided for all answers

### 2. Selected-Text Mode
- Students can highlight text on any page
- Ask questions specifically about the selected text
- Responses restricted to the selected content

### 3. Contextual Learning Support
- Multi-turn conversations with session management
- Concept connections and related topics
- Educational explanations with examples

## API Endpoints

- `POST /chat/ask` - Main chat endpoint for asking questions
- `GET /health` - Health check endpoint
- Other endpoints for document management and administration

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify your Cohere and Gemini API keys are correct and have sufficient quota
2. **Qdrant Connection**: Ensure Qdrant is running and accessible at the configured host/port
3. **Database Connection**: Verify your PostgreSQL connection string is correct

### Rate Limits

Both Cohere and Google Gemini have rate limits. If you encounter rate limit errors:
- Check your API key quotas in the respective dashboards
- Consider implementing additional caching or rate limiting in production

## Production Deployment

For production deployment:

1. Use secure, non-default values for all configuration
2. Set up proper logging and monitoring
3. Implement caching for better performance
4. Use a production-grade database and vector store
5. Set up proper authentication and authorization

## Updating the System

To update the system with new textbook content:

1. Add new content to the `docs/` directory
2. Re-run the ingestion process
3. The new content will be available for querying immediately

## Support

For issues with the system:

- Check the API logs for error messages
- Verify all API keys are valid and have sufficient quota
- Ensure all services (Qdrant, PostgreSQL) are running
- Confirm environment variables are properly set