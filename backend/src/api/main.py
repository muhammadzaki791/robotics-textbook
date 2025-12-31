from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os

from src.api.routes import chat, embed, documents, health
from src.config.settings import settings
from src.services.ingestion_service import ingestion_service
from src.services.qdrant_service import qdrant_service
from src.models.document import DocumentChunk

# Create FastAPI app instance
app = FastAPI(
    title="RAG Chatbot API for Physical AI & Humanoid Robotics Textbook",
    description="API for the RAG (Retrieval Augmented Generation) chatbot integrated with the Physical AI & Humanoid Robotics textbook",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global flag to track if ingestion has been performed
ingestion_performed = False

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers for rate limit information
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Event handler to load textbook content on startup
@app.on_event("startup")
async def startup_event():
    global ingestion_performed
    if not ingestion_performed:
        print("Loading textbook content into vector database on startup...")
        try:
            # Load textbook chunks from the JSON file
            chunks_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "textbook_chunks.json")
            if os.path.exists(chunks_file):
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    textbook_data = json.load(f)

                # Convert to DocumentChunk objects
                document_chunks = []
                for item in textbook_data:
                    chunk = DocumentChunk(
                        id=item['id'],
                        content=item['content'],
                        document_id=item['document_id'],
                        chapter=item['chapter'],
                        section_title=item['section_title'],
                        position=item['position'],
                        token_count=item.get('token_count'),
                        metadata=item.get('metadata', {})
                    )
                    document_chunks.append(chunk)

                print(f"Found {len(document_chunks)} textbook chunks to ingest")

                # Try to ingest the chunks, but handle rate limiting gracefully
                try:
                    result = await ingestion_service.ingest_document_chunks(document_chunks)
                    print(f"Ingestion completed: {result}")
                except Exception as ingest_error:
                    print(f"Ingestion failed due to API rate limits or other error: {ingest_error}")
                    print("Note: Content may already be in the database from a previous run.")
                    # Continue anyway as the persistent storage may already have the data

                ingestion_performed = True
            else:
                print(f"Warning: Textbook chunks file not found at {chunks_file}")
        except Exception as e:
            print(f"Error during startup ingestion: {e}")
            import traceback
            traceback.print_exc()

# Include API routes
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(embed.router, prefix="/embed", tags=["embedding"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API for Physical AI & Humanoid Robotics Textbook"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )