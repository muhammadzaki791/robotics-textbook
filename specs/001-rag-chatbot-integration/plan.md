# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11, Node.js 18+, TypeScript
**Primary Dependencies**: FastAPI, OpenAI SDK, Qdrant Client, asyncpg, Pydantic, SQLAlchemy, Docusaurus, React
**Storage**: Qdrant Cloud Free Tier (vector database), Neon Serverless Postgres (metadata)
**Testing**: pytest, pytest-asyncio, testcontainers, integration testing
**Target Platform**: Linux server, serverless platforms (Railway/Fly.io/Vercel), static site hosting
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Sub-300ms response time, support 100+ concurrent users, optimized embedding efficiency
**Constraints**: Free-tier usage limits, no external web access, static site compatibility, privacy compliance
**Scale/Scope**: Single textbook (Physical AI & Humanoid Robotics), multiple concurrent users, full textbook content

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Technical Accuracy and Retrieval Integrity
✅ **PASS**: RAG system will provide responses strictly grounded in textbook content stored in Qdrant with no hallucination. FastAPI backend will validate all responses reference retrieved context internally before generation.

### II. Educational Clarity and Accessibility
✅ **PASS**: Chatbot responses will maintain beginner-to-intermediate clarity as specified in constitution. OpenAI Agents SDK will be configured with appropriate system prompts to match textbook's educational tone.

### III. Progressive Learning Support
✅ **PASS**: System will support textbook's progressive learning flow through contextual responses that guide students appropriately based on retrieved content structure.

### IV. Strict Content Grounding
✅ **PASS**: Architecture enforces content restriction - only Qdrant-stored content will be used for answers. No external information sources will be accessible to the system.

### V. Selected-Text Priority Mode
✅ **PASS**: Implementation includes logic to restrict responses to user-highlighted text when selection is present. API endpoints will support both normal and selected-text modes.

### VI. Reliable Architecture and Performance
✅ **PASS**: Architecture uses free-tier-compatible services (Qdrant Cloud Free Tier, Neon Serverless Postgres) with performance goals aligned to constitution requirements (<300ms response time).

### VII. Privacy and Safety Compliance
✅ **PASS**: System implements minimal logging practices and data retention policies as required. No sensitive user data will be stored beyond session requirements.

### Key Requirements Validation
- ✅ All responses cite retrieved sections internally for traceability
- ✅ System responds with "Not found in book" when content unavailable
- ✅ Backend uses FastAPI with typed, tested endpoints
- ✅ Database schema stores metadata cleanly (document IDs, chapter mapping, etc.)
- ✅ Qdrant collections organized by chapter/section for targeted retrieval
- ✅ User-selected-text mode supported with strict content restriction
- ✅ Integration seamless with Docusaurus site
- ✅ Services deployable on low-cost serverless platforms

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── chat.py              # ChatQuery, ChatResponse, UserSession entities
│   │   ├── document.py          # DocumentChunk entity and metadata models
│   │   └── database.py          # Database connection and session management
│   ├── services/
│   │   ├── embedding_service.py # Text chunking, embedding generation
│   │   ├── retrieval_service.py # Vector search and context assembly
│   │   ├── chat_service.py      # OpenAI Agent integration and response generation
│   │   ├── qdrant_service.py    # Qdrant client operations
│   │   └── postgres_service.py  # Neon Postgres operations
│   ├── api/
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── routes/
│   │   │   ├── chat.py          # /ask endpoint
│   │   │   ├── embed.py         # /embed, /update endpoints
│   │   │   ├── documents.py     # Document mapping endpoints
│   │   │   └── health.py        # Health check endpoints
│   │   └── middleware/
│   │       ├── auth.py          # Authentication middleware
│   │       └── rate_limit.py    # Rate limiting middleware
│   ├── config/
│   │   ├── settings.py          # Application settings and configuration
│   │   └── constants.py         # Application constants
│   └── utils/
│       ├── validation.py        # Input validation utilities
│       ├── logging.py           # Privacy-safe logging utilities
│       └── helpers.py           # General helper functions
└── tests/
    ├── unit/
    │   ├── test_embedding.py
    │   ├── test_retrieval.py
    │   ├── test_chat.py
    │   └── test_models.py
    ├── integration/
    │   ├── test_api.py
    │   ├── test_qdrant.py
    │   └── test_postgres.py
    └── fixtures/
        └── sample_data.py

frontend/
├── src/
│   ├── components/
│   │   ├── ChatbotWidget.jsx      # Main chatbot UI component
│   │   ├── Message.jsx            # Individual message display
│   │   ├── ChatInput.jsx          # Input field with selected-text detection
│   │   └── ChatHistory.jsx        # Conversation history display
│   ├── services/
│   │   ├── api.js                # API client for backend communication
│   │   └── textSelection.js      # Text selection detection utilities
│   ├── hooks/
│   │   ├── useChat.js            # Chat state management
│   │   └── useTextSelection.js   # Text selection state
│   └── styles/
│       └── chatbot.css           # Chatbot component styling
└── static/
    └── chatbot-embed.js          # Standalone script for Docusaurus integration
```

**Structure Decision**: Web application structure selected with separate backend (FastAPI) and frontend (React components) to support the RAG chatbot functionality. Backend handles all RAG pipeline operations, API endpoints, and integration with Qdrant and Neon Postgres. Frontend provides the chatbot UI widget that integrates seamlessly with the Docusaurus textbook site.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
