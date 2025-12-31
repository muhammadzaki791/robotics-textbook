# API Contract: RAG Chatbot Integration

## 1. Overview

This document defines the API contracts for the RAG Chatbot integration with the Physical AI & Humanoid Robotics textbook. The API provides endpoints for chat interactions, content embedding, document management, and health monitoring.

## 2. Base URL and Versioning

- **Base URL**: `https://api.example.com/v1`
- **Versioning**: API version is included in the URL path (e.g., `/v1/`)
- **Content-Type**: All requests and responses use `application/json` unless otherwise specified

## 3. Authentication

All API endpoints require authentication using API keys. Include the API key in the request header:

```
Authorization: Bearer {api_key}
```

## 4. Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional error details"
  }
}
```

### Common Error Codes:
- `INVALID_INPUT`: Request data is invalid or malformed
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `RATE_LIMIT_EXCEEDED`: Rate limit has been exceeded
- `INTERNAL_ERROR`: Internal server error occurred
- `CONTENT_NOT_FOUND`: No relevant content found in textbook

## 5. API Endpoints

### 5.1 Chat Operations

#### POST /chat/ask
Submit a question to the chatbot and receive a response based on textbook content.

**Request:**
```json
{
  "question": "string (required) - The user's question",
  "selected_text": "string (optional) - Text highlighted by user",
  "session_id": "string (optional) - Session identifier for conversation context",
  "page_context": "string (optional) - Current page URL for context"
}
```

**Response (200):**
```json
{
  "response_id": "string - Unique identifier for this response",
  "answer": "string - The chatbot's answer to the question",
  "sources": [
    {
      "document_id": "string - ID of the source document",
      "title": "string - Title of the source section",
      "url": "string - URL to the source in the textbook"
    }
  ],
  "confidence_score": "number - Confidence in the response (0.0-1.0)",
  "mode": "string - Either 'normal' or 'selected-text'",
  "timestamp": "string - ISO 8601 timestamp"
}
```

**Response (404):**
```json
{
  "error": {
    "code": "CONTENT_NOT_FOUND",
    "message": "The answer is not found in the book."
  }
}
```

### 5.2 Content Embedding

#### POST /embed/chunk-and-store
Process textbook content, create embeddings, and store in the vector database.

**Request:**
```json
{
  "content": "string (required) - The text content to be embedded",
  "document_id": "string (required) - Unique identifier for the document",
  "chapter_id": "string (required) - Chapter identifier",
  "section_title": "string (optional) - Title of the section",
  "metadata": "object (optional) - Additional metadata"
}
```

**Response (201):**
```json
{
  "status": "string - Processing status",
  "document_id": "string - The document identifier",
  "chunks_processed": "number - Number of text chunks created",
  "embedding_time_ms": "number - Time taken to generate embeddings"
}
```

#### POST /embed/update
Update existing embeddings for changed content.

**Request:**
```json
{
  "document_id": "string (required) - Document to update",
  "new_content": "string (required) - Updated content",
  "force_reindex": "boolean (optional) - Whether to force complete reindexing"
}
```

**Response (200):**
```json
{
  "status": "string - Update status",
  "document_id": "string - The updated document identifier",
  "chunks_updated": "number - Number of chunks updated"
}
```

### 5.3 Document Operations

#### GET /documents/mapping
Retrieve the mapping between document IDs and their metadata.

**Query Parameters:**
- `chapter` (optional): Filter by chapter
- `limit` (optional): Number of results to return (default: 50, max: 1000)
- `offset` (optional): Number of results to skip (default: 0)

**Response (200):**
```json
{
  "documents": [
    {
      "document_id": "string - Unique document identifier",
      "title": "string - Document title",
      "chapter": "string - Chapter name",
      "section": "string - Section within chapter",
      "url_path": "string - URL path in textbook",
      "word_count": "number - Number of words in document",
      "updated_at": "string - ISO 8601 timestamp"
    }
  ],
  "total_count": "number - Total number of documents matching query",
  "has_more": "boolean - Whether more results are available"
}
```

#### GET /documents/search
Search for documents by content or metadata.

**Query Parameters:**
- `q` (required): Search query
- `chapter` (optional): Limit search to specific chapter
- `limit` (optional): Number of results to return (default: 10, max: 50)

**Response (200):**
```json
{
  "results": [
    {
      "document_id": "string - Unique document identifier",
      "title": "string - Document title",
      "section": "string - Section within chapter",
      "url_path": "string - URL path in textbook",
      "relevance_score": "number - Relevance score (0.0-1.0)",
      "preview": "string - Brief preview of content"
    }
  ]
}
```

### 5.4 Health and Monitoring

#### GET /health
Check the health status of the API and its dependencies.

**Response (200):**
```json
{
  "status": "string - Overall health status (ok/degraded/unavailable)",
  "timestamp": "string - ISO 8601 timestamp",
  "services": {
    "api": {
      "status": "string - API service status",
      "version": "string - API version"
    },
    "qdrant": {
      "status": "string - Vector database status",
      "available": "boolean - Whether Qdrant is accessible"
    },
    "postgres": {
      "status": "string - Database status",
      "available": "boolean - Whether Postgres is accessible"
    }
  }
}
```

#### GET /stats
Get usage statistics and performance metrics.

**Response (200):**
```json
{
  "stats": {
    "total_queries": "number - Total number of queries processed",
    "avg_response_time_ms": "number - Average response time in milliseconds",
    "queries_per_minute": "number - Recent queries per minute",
    "active_sessions": "number - Currently active sessions",
    "content_coverage": "number - Percentage of textbook content indexed (0.0-1.0)"
  },
  "timestamp": "string - ISO 8601 timestamp"
}
```

## 6. Rate Limiting

All endpoints are subject to rate limiting:
- **Authenticated users**: 100 requests per minute per API key
- **Anonymous access**: 10 requests per minute per IP address

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: The maximum number of requests allowed
- `X-RateLimit-Remaining`: The number of requests remaining
- `X-RateLimit-Reset`: The time when the rate limit resets (Unix timestamp)

## 7. Request/Response Examples

### Example 1: Chat Query
**Request:**
```
POST /chat/ask
Authorization: Bearer my-api-key
Content-Type: application/json

{
  "question": "Explain the difference between forward and inverse kinematics",
  "page_context": "/foundational-concepts/kinematics"
}
```

**Response:**
```
200 OK
{
  "response_id": "resp_abc123",
  "answer": "Forward kinematics calculates the position of the end effector given joint angles, while inverse kinematics calculates the required joint angles to achieve a desired end effector position.",
  "sources": [
    {
      "document_id": "doc_kinematics_001",
      "title": "Kinematics Fundamentals",
      "url": "/foundational-concepts/kinematics"
    }
  ],
  "confidence_score": 0.95,
  "mode": "normal",
  "timestamp": "2025-12-10T15:30:00Z"
}
```

### Example 2: Content Embedding
**Request:**
```
POST /embed/chunk-and-store
Authorization: Bearer my-api-key
Content-Type: application/json

{
  "content": "Forward kinematics is the process of calculating the position and orientation of the end effector given the joint angles of a robotic manipulator...",
  "document_id": "kinematics-section-1",
  "chapter_id": "foundational-concepts",
  "section_title": "Forward Kinematics"
}
```

**Response:**
```
201 Created
{
  "status": "success",
  "document_id": "kinematics-section-1",
  "chunks_processed": 3,
  "embedding_time_ms": 1250
}
```

## 8. Security Considerations

- All sensitive data transmission must use HTTPS
- API keys should be treated as secrets and not exposed in client-side code
- Input validation is performed on all endpoints to prevent injection attacks
- Rate limiting prevents abuse of the service
- No personally identifiable information is stored unless explicitly provided by the user