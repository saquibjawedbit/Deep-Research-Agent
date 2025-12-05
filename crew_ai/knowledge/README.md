# Deep Research Agent - Knowledge Base

This directory contains knowledge sources that persist across research sessions.

## Purpose
The knowledge system helps maintain context and learnings from previous research queries, enabling:
- Cross-query learning and context retention
- Domain-specific knowledge accumulation
- Improved research quality over time

## How It Works
- Research findings are stored as text files
- CrewAI's vector database (ChromaDB) indexes this knowledge
- Agents can query past research to inform new investigations

## Storage Location
Vector embeddings are stored in: `~/.local/share/CrewAI/latest_ai_development/knowledge/`
