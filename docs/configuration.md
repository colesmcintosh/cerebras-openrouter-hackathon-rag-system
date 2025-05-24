# Configuration Guide

This guide covers how to configure the Cerebras RAG system for optimal performance.

## Environment Variables

The system requires several API keys and configuration options. Create a `.env` file in your project root:

```env
# OpenRouter (for Cerebras inference)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Pinecone (for vector database)
PINECONE_API_KEY=your_pinecone_key_here

# Cohere (for embeddings and reranking)
COHERE_API_KEY=your_cohere_key_here

# Optional: Firecrawl (for enhanced web crawling)
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

## API Key Setup

### OpenRouter
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Generate an API key
4. Ensure you have access to Cerebras models

### Pinecone
1. Visit [Pinecone](https://www.pinecone.io/)
2. Create a free account
3. Generate an API key
4. Note your environment (used automatically)

### Cohere
1. Visit [Cohere](https://dashboard.cohere.ai/)
2. Sign up for an account
3. Generate an API key
4. Ensure access to embed-english-v3.0 and rerank-english-v3.0

### Firecrawl (Optional)
1. Visit [Firecrawl](https://firecrawl.dev/)
2. Sign up for an account
3. Generate an API key
4. This improves document crawling quality

## System Configuration

### Vector Database Settings

The system uses these default settings for Pinecone:

```python
INDEX_NAME = "cerebras-docs"
EMBEDDING_DIMENSION = 1024  # Cohere embed-english-v3.0
METRIC = "cosine"
```

### Model Configuration

Default LLM settings:

```python
MODEL = "qwen/qwen3-32b"
PROVIDER = "cerebras"
CONTEXT_WINDOW = 8000  # Conservative limit
```

### Retrieval Settings

Default retrieval parameters:

```python
DEFAULT_K = 6  # Number of documents to retrieve
CHUNK_SIZE = 1000  # Document chunk size
CHUNK_OVERLAP = 200  # Overlap between chunks
RERANK_TOP_N = 4  # Number of documents after reranking
```

## Advanced Configuration

### Custom Agent Configuration

You can customize the agent behavior:

```python
from src.cerebras_rag import CerebrasRAGAgent

agent = CerebrasRAGAgent()

# Initialize with custom settings
agent.initialize_vector_store()
agent.initialize_graph()

# Use custom retrieval parameters
documents = agent.retrieve_with_citations(
    question="Your question",
    k=10,  # Retrieve more documents
    use_reranking=True  # Enable reranking
)
```

### CLI Configuration

The CLI supports runtime configuration:

```bash
# Toggle citations
citations on/off

# Toggle reranking
reranking on/off

# Check status
status
```

## Performance Tuning

### Memory Management

For large conversations, the system automatically trims messages:

```python
# Adjust context window
MAX_TOKENS = 8000  # Increase for longer conversations
STRATEGY = "last"  # Keep most recent messages
```

### Rate Limiting

To respect API rate limits:

```python
# Add delays between requests
BATCH_SIZE = 10  # Process documents in batches
DELAY_BETWEEN_BATCHES = 1  # Seconds to wait
```

### Caching

The system uses LangGraph's built-in memory for conversation caching. For production use, consider:

- Redis for distributed caching
- PostgreSQL for persistent storage
- Custom checkpoint implementations

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```
   Error: Missing required environment variables
   ```
   Solution: Ensure all required API keys are set in `.env`

2. **Vector Store Not Found**
   ```
   Error: Pinecone index 'cerebras-docs' not found
   ```
   Solution: Run the population script: `python scripts/populate_vectordb.py`

3. **Rate Limit Errors**
   ```
   Error: Rate limit exceeded
   ```
   Solution: Reduce batch sizes or add delays

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **API Key Storage**: Never commit `.env` files to version control
2. **Environment Isolation**: Use virtual environments
3. **Access Control**: Limit API key permissions where possible
4. **Network Security**: Use HTTPS for all API calls

## Production Deployment

For production deployments, consider:

1. **Environment Variables**: Use secure secret management
2. **Monitoring**: Add application performance monitoring
3. **Scaling**: Use load balancers for high availability
4. **Backup**: Regular backups of vector database
5. **Updates**: Automated deployment pipelines 