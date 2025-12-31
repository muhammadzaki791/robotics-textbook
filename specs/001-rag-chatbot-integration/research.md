# Research Findings & Technical Decisions: RAG Chatbot Integration

## 1. Embedding Model Selection

### Options Considered:
- **OpenAI Embeddings (text-embedding-ada-002)**: High quality, consistent performance, but higher cost
- **gmini embeddings**: Lower cost, potentially sufficient quality for textbook content
- **Open-source alternatives**: SentenceTransformers, but require self-hosting

### Decision Required:
Select embedding model based on:
- Free-tier usage constraints
- Quality requirements for textbook content
- Performance benchmarks for retrieval accuracy

### Research Needed:
- Compare embedding quality for technical textbook content
- Calculate token usage costs within free-tier limits
- Test retrieval performance with different models

## 2. Text Chunking Strategy

### Options Considered:
- **Fixed-size chunks**: Simple but may break semantic context
- **Semantic chunks**: Preserve context but more complex
- **Sentence-boundary chunks**: Balance between simplicity and context

### Decision Required:
Determine optimal chunk size and strategy to:
- Maximize retrieval relevance
- Minimize context fragmentation
- Work within token limits

### Research Needed:
- Test different chunk sizes (256, 512, 1024 tokens)
- Evaluate retrieval quality with various strategies
- Balance between precision and recall

## 3. Qdrant Collection Structure

### Options Considered:
- **Single collection**: All textbook content in one index
- **Per-chapter collections**: Separate collections for each chapter
- **Hybrid approach**: Main collection with chapter metadata

### Decision Required:
Structure that optimizes:
- Retrieval speed and accuracy
- Management and update operations
- Free-tier resource usage

### Research Needed:
- Compare performance of different collection structures
- Evaluate query complexity and resource usage
- Test scalability with full textbook content

## 4. Retrieval Strategy

### Options Considered:
- **Top-k similarity**: Simple k-nearest neighbor search
- **MMR (Maximum Marginal Relevance)**: Balances relevance and diversity
- **Hybrid search**: Combines semantic and keyword search

### Decision Required:
Select approach that provides:
- High precision for textbook content
- Fast response times within free-tier limits
- Proper handling of selected-text mode

### Research Needed:
- Test different retrieval algorithms with textbook queries
- Benchmark response times under various loads
- Evaluate selected-text mode effectiveness

## 5. Selected-Text Mode Implementation

### Technical Considerations:
- Text selection detection in Docusaurus
- Context restriction at the API level
- UI feedback for selected-text mode activation

### Research Needed:
- JavaScript text selection APIs compatibility
- Performance impact of context restriction
- User experience validation

## 6. Caching Strategy

### Options Considered:
- **Response caching**: Cache common queries and responses
- **Vector caching**: Cache frequently accessed embeddings
- **No caching**: Rely on Qdrant performance

### Decision Required:
Balance between:
- Response speed and resource usage
- Freshness of content vs. performance
- Free-tier limitations

### Research Needed:
- Analyze query patterns in educational context
- Test caching solutions within free-tier constraints
- Evaluate cache invalidation strategies

## 7. Rate Limiting and Security

### Requirements:
- Prevent abuse of free-tier resources
- Protect against prompt injection
- Handle concurrent users effectively

### Research Needed:
- Determine appropriate rate limits for educational use
- Test security measures against injection attacks
- Validate performance under concurrent load

## 8. Deployment Platform Selection

### Options Considered:
- **Railway**: Good for Python/FastAPI applications
- **Fly.io**: Global deployment options
- **Vercel**: Serverless functions for API

### Decision Required:
Platform that provides:
- Free-tier compatibility
- Good performance for RAG operations
- Easy integration with Qdrant and Neon

### Research Needed:
- Compare costs and performance of different platforms
- Test deployment workflows
- Validate free-tier limitations and capabilities

## 9. Frontend Integration Method

### Options Considered:
- **Iframe embedding**: Isolated component, easier security
- **Direct React component**: Better integration, potential conflicts
- **Standalone script**: Minimal footprint, maximum compatibility

### Decision Required:
Method that ensures:
- Seamless Docusaurus integration
- Minimal impact on site performance
- Proper text selection detection

### Research Needed:
- Test different integration methods with Docusaurus
- Evaluate performance impact
- Validate cross-browser compatibility

## 10. Monitoring and Observability

### Requirements:
- Track retrieval accuracy
- Monitor response times
- Log usage within privacy constraints

### Research Needed:
- Identify privacy-compliant monitoring solutions
- Determine key metrics for RAG performance
- Plan alerting for service degradation