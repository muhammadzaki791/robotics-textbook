# Data Model: RAG Chatbot Integration

## 1. Entity Overview

The data model for the RAG chatbot consists of entities that support:
- Document storage and retrieval from Qdrant vector database
- Metadata management in Neon Serverless Postgres
- Chat session tracking and user interactions
- Textbook content organization and mapping

## 2. Core Entities

### 2.1 DocumentChunk

Represents a segment of textbook content processed and stored in the vector database with associated metadata.

```python
class DocumentChunk:
    id: UUID
    content: str                 # The actual text content of the chunk
    document_id: str            # Reference to the source document (chapter/file)
    chapter_id: str             # Chapter identifier for organization
    section_title: str          # Section title for context
    position: int               # Position in the document sequence
    embedding_vector: List[float] # The embedding vector for semantic search
    metadata: Dict[str, Any]    # Additional metadata (source, timestamp, etc.)
    created_at: datetime        # Creation timestamp
    updated_at: datetime        # Last update timestamp
```

**Database Storage**: Primarily stored in Qdrant as vectors with metadata; key identifiers stored in Postgres.

**Relationships**:
- Belongs to one Document/Chapter
- Referenced by multiple ChatQueries for retrieval

### 2.2 ChatQuery

Represents a user's question and associated context, including the question text, selected text (if any), and user session information.

```python
class ChatQuery:
    id: UUID
    session_id: str             # Session identifier
    question: str               # The user's original question
    selected_text: Optional[str] # Text highlighted by user (if any)
    mode: str                   # 'normal' or 'selected-text'
    retrieved_context: List[str] # Retrieved document chunks
    embedding: List[float]      # Embedding of the question
    timestamp: datetime         # When the query was made
    source_page: Optional[str]  # Page where query originated (for context)
```

**Database Storage**: Stored in Postgres for session management and analytics.

**Relationships**:
- Belongs to one UserSession
- References multiple DocumentChunks (through retrieval)

### 2.3 ChatResponse

Represents the system's response to a user query, including the answer text, source references, and confidence level.

```python
class ChatResponse:
    id: UUID
    query_id: UUID              # Reference to the original query
    content: str                # The response content
    sources: List[str]          # Source document references
    confidence_score: float     # Confidence in the response (0.0-1.0)
    timestamp: datetime         # When the response was generated
    grounding_validation: bool  # Whether response is properly grounded
    tokens_used: int            # Number of tokens in the response
```

**Database Storage**: Stored in Postgres for conversation history and quality tracking.

**Relationships**:
- Belongs to one ChatQuery
- References multiple DocumentChunks that informed the response

### 2.4 UserSession

Represents a user's interaction session with the chatbot, tracking conversation history while respecting privacy requirements.

```python
class UserSession:
    id: str                     # Session identifier
    user_id: Optional[str]      # Anonymous user identifier (if available)
    start_time: datetime        # Session start time
    last_activity: datetime     # Last interaction time
    conversation_history: List[Dict] # Limited conversation history
    page_context: Optional[str] # Current page context
    metadata: Dict[str, Any]    # Additional session metadata
```

**Database Storage**: Stored in Postgres with privacy-conscious retention policies.

**Relationships**:
- Contains multiple ChatQueries
- Contains multiple ChatResponses

### 2.5 DocumentMetadata

Represents metadata about textbook documents, chapters, and sections for proper mapping and organization.

```python
class DocumentMetadata:
    id: UUID
    document_id: str            # Unique document identifier
    title: str                  # Document title
    chapter: str                # Chapter name/number
    section: str                # Section within chapter
    page_reference: str         # Page number or location reference
    url_path: str               # URL path in the textbook
    word_count: int             # Number of words in document
    embedding_status: str       # Status of embedding process (pending/completed)
    created_at: datetime        # Creation timestamp
    updated_at: datetime        # Last update timestamp
    checksum: str               # Content checksum for update detection
```

**Database Storage**: Stored in Postgres for document management and tracking.

**Relationships**:
- Links to multiple DocumentChunks
- Used for document mapping and update tracking

## 3. Database Schema (PostgreSQL)

### 3.1 chat_queries table
```sql
CREATE TABLE chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    selected_text TEXT,
    mode VARCHAR(20) NOT NULL DEFAULT 'normal',
    retrieved_context JSONB,
    embedding VECTOR(1536),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_page VARCHAR(500)
);

CREATE INDEX idx_chat_queries_session_id ON chat_queries(session_id);
CREATE INDEX idx_chat_queries_timestamp ON chat_queries(timestamp);
```

### 3.2 chat_responses table
```sql
CREATE TABLE chat_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES chat_queries(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sources JSONB,
    confidence_score DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    grounding_validation BOOLEAN DEFAULT true,
    tokens_used INTEGER
);

CREATE INDEX idx_chat_responses_query_id ON chat_responses(query_id);
CREATE INDEX idx_chat_responses_timestamp ON chat_responses(timestamp);
```

### 3.3 user_sessions table
```sql
CREATE TABLE user_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    conversation_history JSONB,
    page_context VARCHAR(500),
    metadata JSONB
);

CREATE INDEX idx_user_sessions_last_activity ON user_sessions(last_activity);
```

### 3.4 document_metadata table
```sql
CREATE TABLE document_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    chapter VARCHAR(255),
    section VARCHAR(255),
    page_reference VARCHAR(100),
    url_path VARCHAR(500),
    word_count INTEGER,
    embedding_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(64)
);

CREATE INDEX idx_document_metadata_chapter ON document_metadata(chapter);
CREATE INDEX idx_document_metadata_embedding_status ON document_metadata(embedding_status);
```

## 4. Qdrant Collection Schema

### 4.1 textbook_content collection
```json
{
  "vector_params": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "content": {
      "data_type": "text",
      "is_indexed": true
    },
    "document_id": {
      "data_type": "keyword",
      "is_indexed": true
    },
    "chapter_id": {
      "data_type": "keyword",
      "is_indexed": true
    },
    "section_title": {
      "data_type": "text",
      "is_indexed": true
    },
    "position": {
      "data_type": "integer",
      "is_indexed": true
    },
    "metadata": {
      "data_type": "keyword",
      "is_indexed": false
    }
  }
}
```

## 5. Relationships and Constraints

### 5.1 Foreign Key Relationships
- `chat_responses.query_id` → `chat_queries.id`
- All relationships are designed to maintain referential integrity

### 5.2 Indexing Strategy
- Frequently queried fields are indexed for performance
- Text search indexes on content fields
- Time-based indexes for time-series queries

### 5.3 Privacy Considerations
- User sessions use anonymous identifiers
- Conversation history is limited and eventually purged
- No personal information is stored unless explicitly provided

## 6. Data Lifecycle

### 6.1 Document Ingestion
1. Textbook content is parsed and chunked
2. DocumentMetadata is created/updated in Postgres
3. Chunks are embedded and stored in Qdrant
4. Embedding status is updated in Postgres

### 6.2 Query Processing
1. User query is received and stored as ChatQuery
2. Embedding is generated for semantic search
3. Relevant chunks retrieved from Qdrant
4. Response is generated and stored as ChatResponse

### 6.3 Session Management
1. User session is created or updated
2. Conversation history is maintained within privacy limits
3. Session data is periodically cleaned based on retention policy