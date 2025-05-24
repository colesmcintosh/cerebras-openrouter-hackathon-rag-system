# Deployment Guide

This guide covers installation, configuration, and deployment of the Cerebras Documentation RAG System.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/colesmcintosh/cerebras-openrouter-hackathon.git
cd cerebras-openrouter-hackathon

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables:**

```env
# OpenRouter/Cerebras API
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key

# Cohere Embeddings
COHERE_API_KEY=your_cohere_api_key
```

### 3. Database Setup

```bash
# Populate the vector database
python -m src.cerebras_rag.utils.populate_vectordb

# Verify setup
python -c "from cerebras_rag import get_agent; agent = get_agent(); print(agent.check_prerequisites())"
```

### 4. Test Installation

```bash
# Run basic example
python examples/basic_usage.py

# Or start CLI
python -m src.cerebras_rag.interfaces.cli
```

## Detailed Installation

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies and vector data
- **Network**: Internet connection for API access

### Dependencies

Core dependencies are managed in `requirements.txt`:

```txt
# Core framework
langchain>=0.3.25
langchain-community>=0.3.24
langchain-core>=0.3.61
langchain-openai>=0.3.18
langchain-cohere>=0.4.4
langchain-pinecone>=0.2.6
langgraph>=0.4.7

# Vector database & embeddings
pinecone>=6.0.2
cohere>=5.15.0

# Utilities
python-dotenv>=1.1.0
pydantic>=2.11.5
rich>=14.0.0
```

Install specific versions for reproducibility:

```bash
pip install -r requirements.txt --no-deps
```

### Development Installation

For development and contribution:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## API Key Setup

### 1. OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Create an account and navigate to "API Keys"
3. Generate a new API key
4. Add to `.env`: `OPENROUTER_API_KEY=your_key`

**Note**: Ensure your OpenRouter account has access to Cerebras models.

### 2. Pinecone API Key

1. Visit [Pinecone](https://www.pinecone.io/)
2. Create account and go to "API Keys" section
3. Copy your API key
4. Add to `.env`: `PINECONE_API_KEY=your_key`

### 3. Cohere API Key

1. Visit [Cohere](https://cohere.com/)
2. Sign up and navigate to "API Keys"
3. Generate a new API key
4. Add to `.env`: `COHERE_API_KEY=your_key`

## Vector Database Setup

### Initial Population

The system requires a populated Pinecone index with Cerebras documentation:

```bash
# Run the population script
python -m src.cerebras_rag.utils.populate_vectordb

# Expected output:
# 🚀 Starting Cerebras Documentation Population
# ✅ Pinecone connected
# ✅ Generated 1,247 document chunks
# ✅ Population completed successfully!
```

### Custom Document Sources

To populate with custom documents:

```bash
# Specify custom directory
python -m src.cerebras_rag.utils.populate_vectordb --docs-dir /path/to/your/docs

# Force recreate index
python -m src.cerebras_rag.utils.populate_vectordb --force-recreate
```

### Verify Setup

```python
from cerebras_rag import get_agent

agent = get_agent()

# Check prerequisites
prereq_ok, missing = agent.check_prerequisites()
print(f"Prerequisites OK: {prereq_ok}")

# Check vector store
vs_ok, msg = agent.initialize_vector_store()
print(f"Vector store: {msg}")
```

## Configuration Options

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key | - |
| `OPENROUTER_BASE_URL` | No | OpenRouter base URL | `https://openrouter.ai/api/v1` |
| `PINECONE_API_KEY` | Yes | Pinecone API key | - |
| `COHERE_API_KEY` | Yes | Cohere API key | - |
| `PINECONE_INDEX_NAME` | No | Pinecone index name | `cerebras-docs` |

### Performance Tuning

```python
# Custom configuration
agent = CerebrasRAGAgent()

# Adjust retrieval parameters
docs = agent.retrieve_with_citations(
    question="your question",
    k=10,  # Retrieve more documents
    use_reranking=True  # Better relevance
)

# Custom LLM parameters
agent.llm.temperature = 0.1  # More deterministic
agent.llm.max_tokens = 2000  # Longer responses
```

## Production Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ src/
COPY examples/ examples/
COPY .env .env

# Install application
RUN pip install -e .

# Expose port for web interface (if applicable)
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.cerebras_rag.interfaces.cli"]
```

Build and run:

```bash
# Build image
docker build -t cerebras-rag .

# Run container
docker run -it --env-file .env cerebras-rag
```

### Docker Compose

```yaml
version: '3.8'
services:
  cerebras-rag:
    build: .
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
```

### Cloud Deployment

#### Heroku

```bash
# Create Procfile
echo "web: python -m src.cerebras_rag.interfaces.cli" > Procfile

# Deploy
heroku create your-app-name
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set PINECONE_API_KEY=your_key
heroku config:set COHERE_API_KEY=your_key
git push heroku main
```

#### AWS Lambda

For serverless deployment, create a Lambda handler:

```python
import json
from cerebras_rag import get_agent

def lambda_handler(event, context):
    agent = get_agent()
    
    # Initialize if needed
    agent.initialize_vector_store()
    agent.initialize_graph()
    
    # Process query
    question = event.get('question', '')
    response = agent.ask_question(question)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'answer': response.answer,
            'citations': [
                {'source_id': c.source_id, 'quote': c.quote}
                for c in response.citations
            ]
        })
    }
```

## Monitoring and Logging

### Basic Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use in your application
logger = logging.getLogger(__name__)
logger.info("Starting Cerebras RAG system")
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Apply to methods
@monitor_performance
def ask_question(self, question):
    # Your implementation
    pass
```

### Health Checks

```python
def health_check():
    """Basic health check for deployment readiness"""
    try:
        agent = get_agent()
        
        # Check prerequisites
        prereq_ok, missing = agent.check_prerequisites()
        if not prereq_ok:
            return False, f"Missing API keys: {missing}"
        
        # Check vector store
        vs_ok, msg = agent.initialize_vector_store()
        if not vs_ok:
            return False, f"Vector store error: {msg}"
        
        # Test basic query
        response = agent.ask_question("test")
        if not response.answer:
            return False, "No response from LLM"
        
        return True, "All systems operational"
        
    except Exception as e:
        return False, f"Health check failed: {str(e)}"
```

## Troubleshooting Deployment

### Common Issues

#### "Module not found" errors
```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### "API key invalid" errors
```bash
# Verify environment variables
python -c "import os; print('Keys loaded:', bool(os.getenv('OPENROUTER_API_KEY')))"

# Test API connections
python -c "
from cerebras_rag import get_agent
agent = get_agent()
print(agent.check_prerequisites())
"
```

#### "Vector store not found" errors
```bash
# Repopulate database
python -m src.cerebras_rag.utils.populate_vectordb --force-recreate

# Check Pinecone connection
python -c "
from pinecone import Pinecone
pc = Pinecone(api_key='your_key')
print(pc.list_indexes())
"
```

### Performance Issues

#### Slow responses
- Enable response streaming
- Reduce document retrieval count
- Disable reranking for faster responses

#### Memory issues
- Reduce batch sizes in population script
- Use smaller embedding models
- Implement response caching

#### Rate limiting
- Implement exponential backoff
- Use multiple API keys (if permitted)
- Cache frequent queries

## Security Best Practices

### Environment Security

```bash
# Set proper file permissions
chmod 600 .env

# Use secrets management in production
# Don't commit .env to version control
echo ".env" >> .gitignore
```

### API Key Rotation

```python
# Support multiple API keys for rotation
def get_api_key():
    keys = [
        os.getenv('OPENROUTER_API_KEY_1'),
        os.getenv('OPENROUTER_API_KEY_2'),
    ]
    return random.choice([k for k in keys if k])
```

### Input Validation

```python
def validate_query(query: str) -> str:
    """Validate and sanitize user input"""
    if not query or len(query.strip()) == 0:
        raise ValueError("Query cannot be empty")
    
    if len(query) > 1000:
        raise ValueError("Query too long")
    
    return query.strip()
```

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple instances behind a load balancer
- Use Redis for shared caching
- Implement proper session management

### Vertical Scaling

- Increase memory allocation for embedding operations
- Use faster CPU/GPU instances
- Optimize vector database configuration

### Cost Optimization

- Cache frequent queries
- Use smaller models when appropriate
- Implement query throttling
- Monitor API usage and costs

This deployment guide should get you up and running with the Cerebras RAG system in various environments, from local development to production deployments. 