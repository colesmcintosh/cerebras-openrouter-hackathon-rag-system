# Frequently Asked Questions (FAQ)

## General Questions

### What is the Cerebras Documentation RAG System?

The Cerebras Documentation RAG System is an advanced retrieval-augmented generation system that provides intelligent access to Cerebras inference documentation. It combines semantic search, conversation memory, and citation-backed responses using Cerebras's fast inference capabilities.

**Key Features:**
- **Smart Search**: Semantic search through documentation using vector embeddings
- **Citations**: Get exact quotes and source references for all answers
- **Conversation Memory**: Context-aware multi-turn conversations
- **Fast Responses**: Powered by Cerebras inference for high-speed generation
- **Multiple Interfaces**: CLI and programmatic API access

### How does it work?

1. **Document Processing**: Cerebras documentation is chunked and embedded using Cohere
2. **Vector Storage**: Embeddings are stored in Pinecone for fast retrieval
3. **Query Processing**: User questions are embedded and matched against stored documents
4. **Generation**: Qwen3-32B via Cerebras generates responses with citations
5. **Memory**: LangGraph maintains conversation context across interactions

### What makes this different from regular chatbots?

- **Citations**: Every answer includes exact quotes from source documents
- **Accuracy**: Responses are grounded in actual documentation, not hallucinated
- **Context**: Maintains conversation history for follow-up questions
- **Speed**: Uses Cerebras inference for sub-second response times
- **Transparency**: Shows exactly where information comes from

## Setup and Installation

### What are the system requirements?

**Minimum Requirements:**
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection

**Recommended:**
- Python 3.11+
- 8GB RAM
- SSD storage
- Stable internet connection

### What API keys do I need?

You need three API keys:

1. **OpenRouter API Key** - For accessing Qwen3-32B via Cerebras
   - Sign up at [openrouter.ai](https://openrouter.ai)
   - Ensure Cerebras provider access

2. **Pinecone API Key** - For vector database storage
   - Sign up at [pinecone.io](https://pinecone.io)
   - Free tier available

3. **Cohere API Key** - For embeddings and optional reranking
   - Sign up at [cohere.com](https://cohere.com)
   - Free tier available

### How much does it cost to run?

**API Costs (approximate):**
- **OpenRouter/Cerebras**: ~$0.60 per 1M tokens
- **Cohere Embeddings**: ~$0.10 per 1M tokens
- **Pinecone**: Free tier: 1 index, 100K vectors; Paid: $70/month for 1M vectors

**Typical Usage:**
- Single question: ~$0.001-0.005
- Heavy daily use: ~$5-20/month
- Enterprise use: $50-200/month

### Can I run this locally without cloud APIs?

Currently, the system requires cloud APIs for:
- **LLM Generation**: Cerebras/OpenRouter for fast inference
- **Embeddings**: Cohere for high-quality embeddings
- **Vector Storage**: Pinecone for managed vector database

**Future Plans:**
- Local embedding models support
- Local vector storage options (FAISS/Chroma)
- Local LLM integration

### Why can't I use other models like GPT-4 or Claude?

The system is specifically designed for Cerebras inference to showcase:
- **Speed**: Sub-second response times
- **Cost-effectiveness**: Competitive pricing
- **Quality**: Excellent instruction following

However, the architecture is modular and could be adapted for other providers.

## Usage Questions

### How do I ask good questions?

**Best Practices:**
- Be specific: "How do I authenticate with API keys?" vs "How do I login?"
- Use technical terms: "rate limits" vs "speed limits"
- Ask follow-ups: "What about error handling?" after getting authentication info

**Examples of Good Questions:**
- "How do I set up streaming requests with the Cerebras API?"
- "What are the rate limits for different model tiers?"
- "How do I handle authentication errors in my application?"

### Why are some responses slow?

**Common Causes:**
- **First query**: Cold start initialization
- **Complex questions**: Require more document retrieval
- **Reranking enabled**: Additional API call to Cohere
- **Network latency**: Distance to API endpoints

**Solutions:**
- Use streaming responses for better perceived performance
- Disable reranking for faster responses
- Check your internet connection
- Consider response caching for repeated queries

### How accurate are the citations?

Citations are designed to be highly accurate:
- **Verbatim quotes**: Exact text from source documents
- **Source tracking**: Each citation linked to specific document
- **Validation**: Citation source IDs validated against retrieved documents

**However:**
- LLM may occasionally hallucinate citations
- Always verify important information from original sources
- Report any citation accuracy issues

### Can I use this for my own documentation?

Yes! The system is designed to be adaptable:

1. **Replace documents**: Update the `populate_vectordb.py` script
2. **Custom loaders**: Add support for your document formats
3. **Index management**: Create separate Pinecone indexes for different doc sets

**Example:**
```bash
# Populate with your documents
python -m src.cerebras_rag.utils.populate_vectordb --docs-dir /path/to/your/docs --index-name my-docs
```

### How do I handle conversation context?

The system automatically maintains context using thread IDs:

```python
# Same conversation thread
config = {"configurable": {"thread_id": "user_session_123"}}

# First question
response1 = agent.ask_question("What is Cerebras?", config=config)

# Follow-up question (remembers context)
response2 = agent.ask_question("How fast is their inference?", config=config)

# Reference previous conversation
response3 = agent.ask_question("What was my first question?", config=config)
```

## Technical Questions

### How does the RAG pipeline work?

1. **Query Processing**: User question is received and processed
2. **Embedding**: Question is converted to vector using Cohere embeddings
3. **Retrieval**: Similar document chunks found using Pinecone similarity search
4. **Reranking** (optional): Cohere reranks results for better relevance
5. **Context Preparation**: Retrieved documents formatted with source IDs
6. **Generation**: Qwen3-32B generates response with citations
7. **Validation**: Citations validated against source documents
8. **Response**: Structured response returned with answer and citations

### What embedding model is used?

**Cohere embed-english-v3.0**
- **Dimensions**: 1024
- **Quality**: State-of-the-art for retrieval tasks
- **Speed**: Fast embedding generation
- **Cost**: Competitive pricing

### How does conversation memory work?

**LangGraph + MemorySaver**
- **State Management**: Conversation state stored in memory
- **Thread Isolation**: Each conversation has unique thread ID
- **Persistence**: Memory maintained across requests
- **Context Window**: Efficient context management for long conversations

### Can I customize the LLM parameters?

Yes, you can customize various parameters:

```python
agent = get_agent()

# Adjust LLM parameters
agent.llm.temperature = 0.1  # More deterministic (0.0-1.0)
agent.llm.max_tokens = 2000  # Longer responses
agent.llm.top_p = 0.9       # Nucleus sampling

# Adjust retrieval parameters
docs = agent.retrieve_with_citations(
    question="your question",
    k=10,  # More documents
    use_reranking=True  # Better relevance
)
```

### How is document chunking handled?

Documents are intelligently chunked to optimize retrieval:

- **Chunk Size**: ~1000 characters (configurable)
- **Overlap**: 200 characters between chunks
- **Boundary Respect**: Avoids splitting mid-sentence
- **Metadata Preservation**: Source information maintained
- **Context Preservation**: Related information kept together

## Troubleshooting

### "No module named 'cerebras_rag'" error

```bash
# Ensure package is installed
pip install -e .

# Check virtual environment
which python
source .venv/bin/activate

# Verify installation
python -c "from cerebras_rag import get_agent; print('OK')"
```

### "API key invalid" errors

```bash
# Check .env file format
cat .env
# Should be: OPENROUTER_API_KEY=sk-or-v1-xxxxx (no quotes)

# Test API key manually
curl -H "Authorization: Bearer YOUR_KEY" https://openrouter.ai/api/v1/models
```

### "Vector store not found" errors

```bash
# Populate the database
python -m src.cerebras_rag.utils.populate_vectordb

# Force recreate if needed
python -m src.cerebras_rag.utils.populate_vectordb --force-recreate
```

### CLI formatting issues

```bash
# Install Rich for better formatting
pip install rich

# Check terminal compatibility
export TERM=xterm-256color

# Use basic mode if needed
python -m src.cerebras_rag.interfaces.cli --no-rich
```

### Performance issues

**For slow responses:**
- Enable streaming: `agent.stream_response_with_citations()`
- Reduce document count: `k=3` instead of `k=6`
- Disable reranking: `use_reranking=False`

**For memory issues:**
- Reduce batch sizes in population script
- Use garbage collection: `import gc; gc.collect()`
- Monitor usage: `import psutil; print(psutil.virtual_memory())`

## Advanced Usage

### Can I integrate this into my application?

Yes! The system provides a clean Python API:

```python
from cerebras_rag import get_agent

# Initialize once
agent = get_agent()
agent.check_prerequisites()
agent.initialize_vector_store()
agent.initialize_graph()

# Use in your application
def get_documentation_answer(question: str) -> dict:
    response = agent.ask_question(question)
    return {
        "answer": response.answer,
        "sources": [{"id": c.source_id, "quote": c.quote} for c in response.citations]
    }
```

### How do I add custom document loaders?

```python
from typing import List
from langchain_core.documents import Document

class CustomLoader:
    def load_documents(self, source: str) -> List[Document]:
        # Your loading logic here
        docs = []
        # Process your documents
        for doc_data in your_data_source:
            doc = Document(
                page_content=doc_data["content"],
                metadata={
                    "source": doc_data["source"],
                    "title": doc_data["title"]
                }
            )
            docs.append(doc)
        return docs
```

### Can I deploy this as a web service?

Yes! Here's a basic FastAPI example:

```python
from fastapi import FastAPI
from cerebras_rag import get_agent

app = FastAPI()
agent = get_agent()

@app.post("/ask")
async def ask_question(question: str):
    response = agent.ask_question(question)
    return {
        "answer": response.answer,
        "citations": response.citations
    }

# Run with: uvicorn your_app:app --host 0.0.0.0 --port 8000
```

### How do I monitor usage and costs?

**API Usage Tracking:**
```python
import time
from functools import wraps

def track_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Log usage metrics
        print(f"Function: {func.__name__}")
        print(f"Duration: {end_time - start_time:.2f}s")
        print(f"Tokens: {estimate_tokens(result)}")
        
        return result
    return wrapper
```

**Cost Estimation:**
```python
def estimate_cost(question: str, response) -> float:
    # Rough cost estimation
    input_tokens = len(question.split()) * 1.3  # Rough estimate
    output_tokens = len(response.answer.split()) * 1.3
    
    # Cerebras pricing (approximate)
    cost_per_token = 0.0000006  # $0.60 per 1M tokens
    
    return (input_tokens + output_tokens) * cost_per_token
```

## Getting Help

### Where can I get more help?

1. **Documentation**: Check the full docs at `/docs`
2. **Examples**: Review `/examples` directory
3. **GitHub Issues**: Report bugs or request features
4. **Troubleshooting Guide**: See `/docs/troubleshooting.md`
5. **Contributing**: See `/docs/contributing.md` to contribute

### How do I report bugs?

1. **Check existing issues**: Search GitHub issues first
2. **Gather information**: Run the diagnostic script
3. **Create minimal reproduction**: Simplest code that shows the problem
4. **Include details**: System info, error messages, logs
5. **Submit issue**: Use the GitHub issue template

### How can I contribute?

We welcome contributions! See our [Contributing Guide](contributing.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

**Popular contribution areas:**
- Bug fixes and improvements
- New features and interfaces
- Documentation improvements
- Performance optimizations
- Integration examples

---

**Don't see your question here?** Check our [troubleshooting guide](troubleshooting.md) or create a GitHub issue! 