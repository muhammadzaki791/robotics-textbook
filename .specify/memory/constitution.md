<!--
Sync Impact Report:
Version change: 1.1.0 -> 1.2.0
Modified principles: All principles updated to reflect RAG chatbot integration while maintaining educational focus.
Added sections: New principles for RAG architecture, retrieval accuracy, and chatbot behavior.
Removed sections: None.
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
- .specify/templates/commands/*.md ⚠ pending
- README.md ⚠ pending
- docs/quickstart.md ⚠ pending
Follow-up TODOs: None.
-->
# Integrated RAG Chatbot for Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

### I. Technical Accuracy and Retrieval Integrity
The chatbot MUST provide responses strictly grounded in the textbook content stored in Qdrant, with no hallucination or external knowledge injection unless explicitly marked as general knowledge support.

### II. Educational Clarity and Accessibility
All chatbot responses MUST maintain the same beginner-to-intermediate clarity as the textbook, suitable for students with no robotics background, with strong conceptual grounding before complex engineering details.

### III. Progressive Learning Support
The chatbot MUST support the textbook's progressive learning flow: theory → simulation → physical implementation, guiding students through concepts in appropriate sequence.

### IV. Strict Content Grounding
The chatbot MUST only use content retrieved from the vector database for answers; no web access or external information sources are permitted, ensuring consistency with textbook material.

### V. Selected-Text Priority Mode
When users highlight specific text, the chatbot MUST restrict its responses strictly to the selected content, providing focused explanations and context based solely on that selection.

### VI. Reliable Architecture and Performance
The RAG system MUST utilize free-tier-compatible architecture (Qdrant Cloud Free Tier, Neon Serverless Postgres) with minimal latency, ensuring fast vector search and efficient API responses.

### VII. Privacy and Safety Compliance
The system MUST prioritize privacy and safety: no logging of sensitive user data, no storing full conversation history unless necessary for functionality.

## Key Standards

- All responses must cite retrieved sections internally (not user-facing citations) for traceability.
- Chatbot MUST respond with "Not found in book" when content is not available in the vector database.
- Backend architecture MUST use FastAPI with well-documented, typed, and tested endpoints.
- Database schema (Neon) MUST store metadata cleanly: document IDs, chapter mapping, timestamps, embedding vector references.
- Qdrant collections MUST be organized by chapter or section for targeted retrieval.
- The system MUST support user-selected-text mode with strict content restriction to selected text.
- Integration MUST be seamless into the Docusaurus site without layout or script errors.
- All services MUST be deployable on low-cost or serverless hosting platforms.

## Architecture Requirements

The RAG pipeline MUST include: text chunking → embeddings → vector search → context assembly → controlled generation, with proper error handling and fallback responses.

## Governance

- Entire system MUST be developed through Spec-Kit Plus workflow (specify → plan → tasks → implement).
- Implementation MUST be performed through Claude Code with appropriate human oversight.
- System MUST integrate seamlessly with the existing Docusaurus textbook deployment.
- The RAG chatbot MUST enhance the educational value of the textbook without compromising accuracy.
- API endpoints MUST function reliably under load and without errors.
- Database and Qdrant embeddings MUST remain consistent and updatable.
- Chatbot behavior MUST match the pedagogical tone and accuracy required for the textbook.

**Version**: 1.2.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-10
