---
id: 1
title: Update constitution for RAG chatbot integration
stage: constitution
date: 2025-12-10
model: sonnet
feature: null
branch: 001-robotics-textbook
user:
command: /sp.constitution
labels: ["constitution", "rag", "chatbot", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
---

# Update constitution for RAG chatbot integration

## User Prompt

```
Project: Integrated RAG Chatbot for the Physical AI & Humanoid Robotics Textbook

Core principles:
- High accuracy through retrieval-only responses (no hallucination, no outside knowledge unless explicitly allowed)
- Strict grounding in the textbook's content stored in Qdrant and indexed through RAG
- Clear, safe, student-friendly answers suitable for educational use
- Consistent behavior: prioritize selected text when user highlights content
- Reliable backend architecture using FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier
- Privacy and safety: no logging of sensitive user data, no storing full conversation history unless necessary

Key standards:
- All answers must cite retrieved sections internally (not user-facing citations)
- Chatbot must never answer beyond the content available in the vector database unless marked as "general knowledge support"
- Retrieval pipeline must include: text chunking → embeddings → vector search → context assembly → controlled generation
- Must support user-selected-text mode: when selection is present, retrieval is restricted strictly to selected text
- Must integrate with the OpenAI Agents / ChatKit SDKs for stable production-grade inference
- FastAPI service endpoints must be well-documented, typed, and tested
- Database schema (Neon) must store metadata cleanly: document IDs, chapter mapping, timestamps, embedding vector references
- Qdrant collections must be organized by chapter or section for targeted retrieval
- UI/UX must seamlessly embed the chatbot into the published Docusaurus book

Constraints:
- Only Qdrant-stored content may be used for retrieval; no web access
- Use only free-tier-compatible architectures (Qdrant Cloud Free Tier, Neon Free Tier)
- Must work inside a static Docusaurus site (frontend integration only)
- All backend services must be deployable on low-cost or serverless hosting
- Latency should remain minimal (fast vector search + efficient API)
- Chatbot must avoid speculative answers; respond with "Not found in book" when necessary

Success criteria:
- Chatbot successfully answers user questions using relevant book content
- Chatbot can answer questions based solely on the user's highlighted text
- Retrieval and ranking pipeline consistently returns the correct sections
- API endpoints function reliably under load and without errors
- Full integration into the Docusaurus site without layout or script errors
- Database and Qdrant embeddings remain consistent and updatable
- Chatbot behavior matches the pedagogical tone and accuracy required for the textbook
```

## Response Summary

Updated the project constitution to reflect the new scope: "Integrated RAG Chatbot for Physical AI & Humanoid Robotics Textbook". The changes include:

- Updated core principles to focus on RAG architecture, retrieval accuracy, and chatbot behavior while maintaining educational focus
- Added new principles for technical accuracy, content grounding, selected-text priority mode, and reliable architecture
- Maintained educational clarity and accessibility requirements
- Added specific standards for the RAG system architecture and integration
- Updated governance requirements to match the new project scope
- Version incremented from 1.1.0 to 1.2.0 with appropriate sync impact report

The updated constitution ensures the RAG chatbot will maintain the same educational quality and technical accuracy as the original textbook while adding requirements for retrieval-based responses, privacy compliance, and seamless integration.