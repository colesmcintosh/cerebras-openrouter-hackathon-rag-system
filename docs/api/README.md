# API Reference

This directory contains detailed API documentation for the Cerebras RAG system.

## Quick Navigation

- [CerebrasRAGAgent](cerebras_rag_agent.md) - Main RAG agent class
- [Models](models.md) - Data models and structures  
- [Utilities](utilities.md) - Utility functions and helpers
- [CLI Interface](cli.md) - Command-line interface

## Overview

The Cerebras RAG API provides programmatic access to an advanced retrieval-augmented generation system. The main entry point is the `CerebrasRAGAgent` class, which handles document retrieval, citation generation, and conversation management.

## Quick Start

```python
from cerebras_rag import get_agent

# Initialize the agent
agent = get_agent()

# Check prerequisites
prereq_ok, missing_keys = agent.check_prerequisites()
if not prereq_ok:
    print(f"Missing API keys: {', '.join(missing_keys)}")
    exit(1)

# Initialize vector store
vs_ok, vs_msg = agent.initialize_vector_store()
if not vs_ok:
    print(f"Vector store error: {vs_msg}")
    exit(1)

# Initialize conversation graph
agent.initialize_graph()

# Ask a question
response = agent.ask_question(
    question="How do I authenticate with the Cerebras API?",
    use_citations=True
)

print(f"Answer: {response.answer}")
for citation in response.citations:
    print(f"Source: {citation.quote}")
```

## Key Features

- **Document Retrieval**: Semantic search through Cerebras documentation
- **Citation Generation**: Exact quotes and source references
- **Conversation Memory**: Context-aware multi-turn conversations
- **Streaming Responses**: Real-time response generation
- **Reranking**: Optional Cohere reranking for improved relevance 