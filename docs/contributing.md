# Contributing Guide

Thank you for your interest in contributing to the Cerebras Documentation RAG System! This guide will help you get started with development and contributions.

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/colesmcintosh/cerebras-openrouter-hackathon.git
   cd cerebras-openrouter-hackathon
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Add your API keys for testing
   nano .env
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   flake8 src/
   
   # Run type checking
   mypy src/
   ```

### Project Structure

```
cerebras-openrouter-hackathon/
├── src/cerebras_rag/           # Main package
│   ├── agents/                 # Core agent logic
│   │   ├── rag_agent.py       # Main RAG agent
│   │   └── models.py          # Data models
│   ├── interfaces/            # User interfaces
│   │   └── cli.py             # Command-line interface
│   └── utils/                 # Utilities
│       └── populate_vectordb.py
├── examples/                  # Usage examples
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Dependencies
├── setup.py                   # Package configuration
└── README.md                  # Project overview
```

## Development Guidelines

### Code Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (instead of 79)
- **Quotes**: Use double quotes for strings
- **Imports**: Use absolute imports when possible

#### Formatting Tools

```bash
# Format code with black
black src/ tests/ examples/

# Sort imports with isort
isort src/ tests/ examples/

# Check style with flake8
flake8 src/ tests/ examples/
```

#### Pre-commit Configuration

The project uses pre-commit hooks to enforce code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Optional, Tuple

def ask_question(
    self, 
    question: str, 
    use_citations: bool = True,
    config: Optional[dict] = None
) -> QuotedAnswer:
    """Ask a question and return structured response."""
    ...
```

### Documentation

#### Docstrings

Use Google-style docstrings:

```python
def retrieve_with_citations(
    self, 
    question: str, 
    k: int = 6, 
    use_reranking: bool = False
) -> List[Document]:
    """
    Retrieve relevant documents with optional reranking.
    
    Args:
        question: Query for document retrieval
        k: Number of documents to retrieve
        use_reranking: Whether to use Cohere reranking
        
    Returns:
        List of relevant documents with metadata
        
    Raises:
        ConnectionError: If vector store is not initialized
        ValueError: If k is less than 1
        
    Example:
        >>> agent = get_agent()
        >>> docs = agent.retrieve_with_citations("How to authenticate?", k=3)
        >>> print(f"Found {len(docs)} documents")
    """
    ...
```

#### Code Comments

- Use comments sparingly, prefer self-documenting code
- Explain **why**, not **what**
- Add comments for complex algorithms or business logic

```python
# Use structured output to ensure citations are properly formatted
response = self.llm.with_structured_output(QuotedAnswer).invoke(prompt)

# Validate citation source IDs match retrieved documents
validated_citations = self._validate_citations(response.citations, docs)
```

## Testing

### Test Structure

```
tests/
├── unit/                      # Unit tests
│   ├── test_rag_agent.py     # Test main agent
│   ├── test_models.py        # Test data models
│   └── test_cli.py           # Test CLI interface
├── integration/               # Integration tests
│   ├── test_vector_store.py  # Test vector database
│   └── test_end_to_end.py    # Full system tests
└── conftest.py               # Pytest configuration
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from cerebras_rag.agents.rag_agent import CerebrasRAGAgent
from cerebras_rag.agents.models import QuotedAnswer, Citation

class TestCerebrasRAGAgent:
    """Test cases for the main RAG agent."""
    
    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = CerebrasRAGAgent()
        assert agent.vector_store is None
        assert agent.llm is not None
        
    def test_check_prerequisites_missing_keys(self):
        """Test prerequisites check with missing API keys."""
        agent = CerebrasRAGAgent()
        
        with patch.dict('os.environ', {}, clear=True):
            success, missing = agent.check_prerequisites()
            assert not success
            assert len(missing) > 0
            
    @patch('cerebras_rag.agents.rag_agent.Pinecone')
    def test_vector_store_initialization(self, mock_pinecone):
        """Test vector store initialization."""
        # Setup mocks
        mock_index = Mock()
        mock_index.describe_index_stats.return_value = {'total_vector_count': 100}
        mock_pinecone.return_value.Index.return_value = mock_index
        
        agent = CerebrasRAGAgent()
        success, message = agent.initialize_vector_store()
        
        assert success
        assert "100" in message
```

#### Integration Tests

```python
import pytest
from cerebras_rag import get_agent

@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def agent(self):
        """Create configured agent for testing."""
        agent = get_agent()
        
        # Skip if no API keys configured
        prereq_ok, missing = agent.check_prerequisites()
        if not prereq_ok:
            pytest.skip(f"Missing API keys: {missing}")
            
        vs_ok, msg = agent.initialize_vector_store()
        if not vs_ok:
            pytest.skip(f"Vector store not available: {msg}")
            
        agent.initialize_graph()
        return agent
    
    def test_basic_question_answering(self, agent):
        """Test basic question answering works."""
        response = agent.ask_question("What is Cerebras?")
        
        assert response.answer
        assert len(response.answer) > 10
        assert isinstance(response.citations, list)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/cerebras_rag

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -m "not integration" # Skip integration tests

# Run specific test file
pytest tests/unit/test_rag_agent.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Configuration

```python
# conftest.py
import pytest
import os
from dotenv import load_dotenv

def pytest_configure():
    """Configure pytest."""
    load_dotenv()
    
@pytest.fixture(scope="session")
def api_keys_available():
    """Check if API keys are available for testing."""
    required_keys = [
        'OPENROUTER_API_KEY',
        'PINECONE_API_KEY', 
        'COHERE_API_KEY'
    ]
    
    missing = [key for key in required_keys if not os.getenv(key)]
    return len(missing) == 0, missing

@pytest.mark.integration
def pytest_collection_modifyitems(config, items):
    """Skip integration tests if API keys not available."""
    api_keys_available, missing = api_keys_available()
    
    if not api_keys_available:
        skip_integration = pytest.mark.skip(
            reason=f"Missing API keys for integration tests: {missing}"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
```

## Contributing Process

### Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   flake8 src/
   
   # Run type checking
   mypy src/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: descriptive commit message"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Commit Message Guidelines

Use conventional commits format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add streaming response support
fix(cli): handle keyboard interrupt gracefully
docs(api): update CerebrasRAGAgent documentation
test(integration): add vector store connection tests
```

### Pull Request Guidelines

#### PR Title and Description

- Use clear, descriptive titles
- Reference relevant issues: "Fixes #123"
- Describe what changed and why
- Include testing instructions

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Development Areas

### High Priority Contributions

1. **Performance Optimization**
   - Response caching
   - Batch processing improvements
   - Memory usage optimization

2. **New Features**
   - Additional document loaders
   - Custom embedding models
   - Web interface
   - API server

3. **Testing**
   - Increase test coverage
   - Add performance benchmarks
   - Integration test improvements

4. **Documentation**
   - More examples
   - Video tutorials
   - API documentation improvements

### Code Areas

#### Adding New Document Loaders

```python
# src/cerebras_rag/utils/loaders.py
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class DocumentLoader(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    def load_documents(self, source: str) -> List[Document]:
        """Load documents from source."""
        pass

class CustomLoader(DocumentLoader):
    """Example custom document loader."""
    
    def load_documents(self, source: str) -> List[Document]:
        """Load documents from custom source."""
        # Your implementation here
        return documents
```

#### Adding New Interfaces

```python
# src/cerebras_rag/interfaces/web.py
from fastapi import FastAPI, HTTPException
from cerebras_rag import get_agent
from cerebras_rag.agents.models import QuotedAnswer

app = FastAPI(title="Cerebras RAG API")
agent = get_agent()

@app.post("/ask", response_model=QuotedAnswer)
async def ask_question(question: str):
    """Ask a question and get response with citations."""
    try:
        response = agent.ask_question(question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Release Process

### Version Management

We use semantic versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)  
- `PATCH`: Bug fixes

### Creating Releases

1. **Update Version**
   ```python
   # src/cerebras_rag/__init__.py
   __version__ = "1.1.0"
   ```

2. **Update Changelog**
   ```markdown
   # CHANGELOG.md
   ## [1.1.0] - 2024-01-15
   ### Added
   - New streaming response feature
   ### Fixed
   - Citation validation bug
   ```

3. **Create Release**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions
- **Discord/Slack**: Real-time discussions (if available)

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in project documentation

Thank you for contributing to the Cerebras Documentation RAG System! Your contributions help make this project better for everyone. 