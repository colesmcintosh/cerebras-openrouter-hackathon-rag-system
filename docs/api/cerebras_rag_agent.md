# CerebrasRAGAgent

The main agent class for the Cerebras documentation RAG system.

## Class Overview

```python
class CerebrasRAGAgent:
    """
    Main agent class for Cerebras documentation RAG system.
    
    This agent provides intelligent access to Cerebras documentation with features including:
    - Semantic search through documentation using Pinecone vector database
    - Citation-backed responses using Cohere embeddings and reranking
    - Conversation memory using LangGraph
    - Streaming responses with real-time citation tracking
    """
```

## Initialization

### `__init__()`

```python
def __init__(self):
    """Initialize the RAG agent with default configuration."""
```

Creates a new instance of the CerebrasRAGAgent. Automatically initializes the LLM connection.

**Example:**
```python
from cerebras_rag import CerebrasRAGAgent

agent = CerebrasRAGAgent()
```

### `get_agent()`

```python
def get_agent() -> CerebrasRAGAgent:
    """Factory function to create a CerebrasRAGAgent instance."""
```

Convenience factory function to create and return a new agent instance.

**Returns:**
- `CerebrasRAGAgent`: A new agent instance

**Example:**
```python
from cerebras_rag import get_agent

agent = get_agent()
```

## Setup Methods

### `check_prerequisites()`

```python
def check_prerequisites(self) -> tuple[bool, list]:
    """
    Check if all required API keys are available.
    
    Returns:
        tuple: (bool, list) - Success status and list of missing keys
    """
```

Validates that all required environment variables are set.

**Returns:**
- `tuple[bool, list]`: Success status and list of missing API keys

**Required Environment Variables:**
- `OPENROUTER_API_KEY`: For Qwen model access
- `PINECONE_API_KEY`: For vector database
- `COHERE_API_KEY`: For embeddings and reranking

**Example:**
```python
prereq_ok, missing_keys = agent.check_prerequisites()
if not prereq_ok:
    print(f"Missing API keys: {', '.join(missing_keys)}")
```

### `initialize_vector_store()`

```python
def initialize_vector_store(self) -> tuple[bool, str]:
    """
    Initialize connection to Pinecone vector store.
    
    Returns:
        tuple: (bool, str) - Success status and status message
    """
```

Establishes connection to the Pinecone vector database and validates it contains data.

**Returns:**
- `tuple[bool, str]`: Success status and descriptive message

**Example:**
```python
vs_ok, vs_msg = agent.initialize_vector_store()
if not vs_ok:
    print(f"Vector store error: {vs_msg}")
    return
print(f"✅ {vs_msg}")
```

### `initialize_graph()`

```python
def initialize_graph(self):
    """Initialize the LangGraph conversation graph for memory management."""
```

Sets up the conversation memory system using LangGraph.

**Example:**
```python
agent.initialize_graph()
```

## Core Query Methods

### `ask_question()`

```python
def ask_question(
    self, 
    question: str, 
    use_citations: bool = True, 
    use_reranking: bool = False, 
    config: dict = None
) -> QuotedAnswer:
    """
    Ask a question and get an answer with citations.
    
    Args:
        question: The user's question
        use_citations: Whether to include source citations
        use_reranking: Whether to use Cohere reranking for better relevance
        config: LangGraph configuration for conversation threading
        
    Returns:
        QuotedAnswer: Response with answer and citations
    """
```

Main method for asking questions and receiving structured responses.

**Parameters:**
- `question` (str): The question to ask
- `use_citations` (bool, optional): Include citations in response. Default: True
- `use_reranking` (bool, optional): Use Cohere reranking. Default: False  
- `config` (dict, optional): LangGraph config for conversation threading

**Returns:**
- `QuotedAnswer`: Structured response with answer and citations

**Example:**
```python
response = agent.ask_question(
    question="How do I authenticate with the Cerebras API?",
    use_citations=True,
    use_reranking=True
)

print(f"Answer: {response.answer}")
for citation in response.citations:
    print(f"Citation: {citation.quote}")
```

### `stream_response_with_citations()`

```python
def stream_response_with_citations(
    self, 
    question: str, 
    use_citations: bool = True,
    use_reranking: bool = False, 
    config: dict = None
):
    """
    Stream the response with real-time citation tracking.
    
    Args:
        question: The user's question
        use_citations: Whether to include citations
        use_reranking: Whether to use Cohere reranking
        config: LangGraph configuration
        
    Yields:
        dict: Stream chunks with type and content
    """
```

Streams responses in real-time with progressive citation updates.

**Parameters:**
- Same as `ask_question()`

**Yields:**
- `dict`: Stream chunks with keys:
  - `type`: "status", "answer", "citation", or "error"
  - `content`/`message`: Content or status message
  - Additional fields based on type

**Example:**
```python
for chunk in agent.stream_response_with_citations(question="What models are available?"):
    if chunk["type"] == "status":
        print(f"Status: {chunk['message']}")
    elif chunk["type"] == "answer":
        print(f"Answer: {chunk['content']}")
    elif chunk["type"] == "citation":
        print(f"Citation: {chunk['title']}")
```

## Document Retrieval Methods

### `retrieve_with_citations()`

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
        List[Document]: Retrieved and optionally reranked documents
    """
```

Retrieves relevant documents from the vector store with optional reranking.

**Parameters:**
- `question` (str): Search query
- `k` (int, optional): Number of documents to retrieve. Default: 6
- `use_reranking` (bool, optional): Use Cohere reranking. Default: False

**Returns:**
- `List[Document]`: List of relevant documents

### `generate_with_citations()`

```python
def generate_with_citations(
    self, 
    question: str, 
    documents: List[Document], 
    use_structured_output: bool = True
):
    """
    Generate answer with citations from provided documents.
    
    Args:
        question: The user's question
        documents: List of source documents
        use_structured_output: Whether to use structured Pydantic output
        
    Returns:
        Response with answer and citations
    """
```

Generates a response with citations based on provided documents.

## Memory and Conversation Methods

### `get_conversation_history()`

```python
def get_conversation_history(
    self, 
    config: dict = {"configurable": {"thread_id": "1"}}
):
    """
    Retrieve conversation history for a given thread.
    
    Args:
        config: LangGraph configuration with thread_id
        
    Returns:
        List of conversation messages
    """
```

Retrieves the conversation history for a specific thread.

**Parameters:**
- `config` (dict): Configuration with thread_id

**Returns:**
- `List`: Conversation message history

### `is_conversation_history_question()`

```python
def is_conversation_history_question(self, question: str) -> bool:
    """
    Detect if the user is asking about their conversation history.
    
    Args:
        question: The user's question
        
    Returns:
        bool: True if asking about conversation history
    """
```

Determines if a question is asking about previous conversation history.

## Utility Methods

### `format_docs_with_id()`

```python
def format_docs_with_id(self, docs: List[Document]) -> str:
    """
    Format documents with source IDs for citation tracking.
    
    Args:
        docs: List of retrieved documents
        
    Returns:
        str: Formatted document text with source IDs
    """
```

Formats documents with source IDs for proper citation tracking.

## Configuration

The agent uses several environment variables:

- `OPENROUTER_API_KEY`: API key for OpenRouter/Cerebras access
- `OPENROUTER_BASE_URL`: Base URL for OpenRouter API
- `PINECONE_API_KEY`: API key for Pinecone vector database
- `COHERE_API_KEY`: API key for Cohere embeddings and reranking

The agent is configured to use:
- **Model**: `qwen/qwen3-32b` via Cerebras provider
- **Embeddings**: Cohere `embed-english-v3.0`
- **Vector Database**: Pinecone with index name `cerebras-docs`
- **Memory**: LangGraph with MemorySaver for conversation persistence 