# Cerebras Documentation RAG System

An advanced RAG (Retrieval-Augmented Generation) system that provides intelligent access to Cerebras inference documentation with citations, conversation memory, and multiple interfaces.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Advanced RAG Pipeline**: Semantic search through Cerebras documentation using Pinecone + Cohere
- **Citation Support**: Get exact quotes and source references for all answers
- **Multiple Interfaces**: CLI or programmatic API access
- **Conversation Memory**: Maintains context across interactions using LangGraph
- **Document Reranking**: Optional Cohere reranking for improved relevance
- **Streaming Responses**: Real-time response generation with live citation tracking
- **Powered by Cerebras**: Uses Qwen3-32B through Cerebras inference for fast, high-quality responses

## 📁 Project Structure

```
cerebras-openrouter-hackathon/
├── src/cerebras_rag/           # Main package
│   ├── agents/                 # Core RAG agent logic
│   │   ├── rag_agent.py       # Main CerebrasRAGAgent class
│   │   └── models.py          # Pydantic models for structured output
│   ├── interfaces/            # User interfaces
│   │   └── cli.py            # Professional CLI interface
│   └── utils/                 # Utilities and tools
│       └── populate_vectordb.py  # Vector database population
├── scripts/                   # Entry point scripts
│   ├── run_cli.py            # Run CLI interface
│   └── populate_vectordb.py  # Populate vector database
├── docs/                      # Comprehensive documentation
├── examples/                  # Usage examples
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── setup.py                  # Package installation
└── .env                      # API keys (create this file)
```

## 🛠️ Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd cerebras-openrouter-hackathon
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Or install as editable package
pip install -e .
```

### 3. Configure API Keys

Create a `.env` file with your API keys:

```env
# OpenRouter (for Cerebras inference)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Pinecone (for vector database)
PINECONE_API_KEY=your_pinecone_key_here

# Cohere (for embeddings and reranking)
COHERE_API_KEY=your_cohere_key_here

# Firecrawl (for enhanced web crawling)
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

**Get API Keys:**
- [OpenRouter](https://openrouter.ai/) - For Cerebras model access
- [Pinecone](https://www.pinecone.io/) - For vector database
- [Cohere](https://dashboard.cohere.ai/) - For embeddings and reranking
- [Firecrawl](https://firecrawl.dev/) - For enhanced web crawling (optional)

### 4. Populate Vector Database

```bash
python scripts/populate_vectordb.py
```

This will:
- Crawl Cerebras inference documentation
- Create embeddings using Cohere
- Store in Pinecone vector database
- Build searchable knowledge base

## 🎯 Usage

### Option 1: Command Line Interface (Recommended)

```bash
# Run the interactive CLI
python scripts/run_cli.py

# Or if installed as package
cerebras-rag-cli
```

**CLI Features:**
- Interactive question-answering with citations
- Live configuration (enable/disable citations, reranking)
- Conversation history tracking
- Professional terminal interface with color coding
- Session management and command help

**CLI Commands:**
- `help` - Show command reference
- `citations on/off` - Toggle source citations
- `reranking on/off` - Toggle document reranking
- `status` - Show system status
- `history` - Display conversation history
- `quit/exit` - Exit application

### Option 2: Programmatic API

```python
from src.cerebras_rag import get_agent

# Get agent instance
agent = get_agent()

# Initialize components
agent.initialize_vector_store()
agent.initialize_graph()

# Ask a question
response = agent.ask_question(
    "How do I authenticate with Cerebras API?",
    use_citations=True,
    use_reranking=False
)

print(f"Answer: {response.answer}")
for citation in response.citations:
    print(f"Source {citation.source_id}: {citation.quote}")
```

### Option 3: Streaming API

```python
# Stream responses in real-time
for chunk in agent.stream_response_with_citations(
    question="How do I get started with Cerebras?",
    use_citations=True
):
    if chunk["type"] == "answer":
        print(chunk["content"])
    elif chunk["type"] == "citation":
        print(f"Source: {chunk['title']}")
```

## 🧠 Architecture

### Core Components

1. **`CerebrasRAGAgent`** - The heart of the system
   - Document retrieval and reranking
   - Citation generation and structured output
   - Conversation memory management
   - LangGraph integration

2. **CLI Interface** - Professional command-line experience
   - Interactive question-answering
   - Real-time streaming responses
   - Configuration management
   - Session tracking

### Technical Stack

- **LLM**: Qwen3-32B via Cerebras inference (OpenRouter)
- **Embeddings**: Cohere embed-english-v3.0
- **Vector DB**: Pinecone with semantic search
- **Reranking**: Cohere rerank-english-v3.0 (optional)
- **Memory**: LangGraph with persistent checkpointing
- **Citations**: Structured output with source tracking

### Data Flow

1. **Question Input** → User asks a question
2. **Document Retrieval** → Semantic search in Pinecone
3. **Optional Reranking** → Cohere reranks for relevance
4. **Context Formation** → Documents formatted with source IDs
5. **LLM Generation** → Cerebras model generates cited response
6. **Memory Storage** → Conversation saved to LangGraph
7. **Response Output** → Structured answer with citations

## 📊 Examples

Check out the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Basic agent usage and citation handling
- More examples coming soon!

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Configuration Guide](docs/configuration.md) - Setup and configuration options
- [API Reference](docs/api/) - Detailed API documentation
- [Architecture](docs/architecture.md) - System architecture and design
- [Examples](docs/examples/) - Usage examples and tutorials

## 🔧 Development

### Installation for Development

```bash
# Clone repository
git clone <repository-url>
cd cerebras-openrouter-hackathon

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/cerebras_rag
```

### Code Quality

```bash
# Format code
black src/ scripts/ examples/

# Sort imports
isort src/ scripts/ examples/

# Lint code
flake8 src/ scripts/ examples/

# Type checking
mypy src/cerebras_rag
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Examples**: See [examples/](examples/) for usage patterns
- **Issues**: Report bugs and request features via GitHub issues

## 🙏 Acknowledgments

- **Cerebras**: For providing fast inference capabilities
- **OpenRouter**: For API access to Cerebras models
- **Pinecone**: For vector database services
- **Cohere**: For embeddings and reranking
- **LangChain & LangGraph**: For RAG framework and memory management 