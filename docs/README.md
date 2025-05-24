# Cerebras RAG Documentation

This directory contains comprehensive documentation for the Cerebras Documentation RAG System.

## Quick Navigation

- [API Reference](api/) - Detailed API documentation
- [Examples](examples/) - Usage examples and tutorials
- [Architecture](architecture.md) - System architecture and design
- [Configuration](configuration.md) - Configuration options and environment setup
- [Deployment](deployment.md) - Deployment guides and best practices
- [Contributing](contributing.md) - Guidelines for contributing to the project

## Overview

The Cerebras Documentation RAG System is an advanced retrieval-augmented generation system that provides intelligent access to Cerebras inference documentation with citations, conversation memory, and multiple interfaces.

### Key Features

- **Advanced RAG Pipeline**: Semantic search through Cerebras documentation using Pinecone + Cohere
- **Citation Support**: Get exact quotes and source references for all answers
- **Multiple Interfaces**: CLI or programmatic API access
- **Conversation Memory**: Maintains context across interactions using LangGraph
- **Document Reranking**: Optional Cohere reranking for improved relevance
- **Streaming Responses**: Real-time response generation with live citation tracking
- **Powered by Cerebras**: Uses Qwen3-32B through Cerebras inference for fast, high-quality responses

## Getting Started

1. **Installation**: See the main README.md for installation instructions
2. **Configuration**: Follow the [Configuration Guide](configuration.md)
3. **Examples**: Check out the [Examples](examples/) directory
4. **API Reference**: Explore the [API Documentation](api/)

## Architecture

The system is built with a modular architecture:

```
src/cerebras_rag/
├── agents/          # Core RAG agent logic
├── interfaces/      # User interfaces (CLI)
├── utils/           # Utilities and tools
└── __init__.py      # Package initialization
```

For detailed architecture information, see [Architecture Documentation](architecture.md).

## Support

- Check the [FAQ](faq.md) for common questions
- See [Troubleshooting](troubleshooting.md) for common issues
- Review [Examples](examples/) for usage patterns 