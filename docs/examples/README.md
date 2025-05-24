# Examples

This directory contains comprehensive examples demonstrating how to use the Cerebras RAG system effectively.

## Available Examples

- [Basic Usage](basic_usage.md) - Complete example showing core functionality
- [Streaming Responses](streaming.md) - Real-time response streaming examples
- [Conversation Memory](conversation.md) - Multi-turn conversation examples
- [Advanced Configuration](advanced.md) - Custom configuration and optimization

## Quick Start

The simplest way to get started is with the basic usage example:

```python
from cerebras_rag import get_agent

# Initialize and configure
agent = get_agent()
agent.check_prerequisites()
agent.initialize_vector_store()
agent.initialize_graph()

# Ask a question
response = agent.ask_question("How do I authenticate with Cerebras?")
print(f"Answer: {response.answer}")
```

## Running Examples

All examples can be run directly from the project root:

```bash
# Run the basic usage example
python examples/basic_usage.py

# Or from the project root with module syntax
python -m examples.basic_usage
```

### Prerequisites

Before running examples, ensure:

1. **Environment Setup**: Copy `.env.example` to `.env` and configure API keys
2. **Dependencies**: Install requirements with `pip install -r requirements.txt`  
3. **Vector Database**: Populate the database with `python -m src.cerebras_rag.utils.populate_vectordb`

## Example Categories

### 1. Basic Examples
- Simple question-answering
- Citation handling
- Error management

### 2. Streaming Examples  
- Real-time response processing
- Progress tracking
- Live citation updates

### 3. Conversation Examples
- Multi-turn conversations
- Context preservation
- History retrieval

### 4. Advanced Examples
- Custom configurations
- Performance optimization
- Integration patterns

## Common Patterns

### Error Handling

```python
try:
    # Check prerequisites first
    prereq_ok, missing_keys = agent.check_prerequisites()
    if not prereq_ok:
        print(f"Missing API keys: {', '.join(missing_keys)}")
        return
    
    # Initialize vector store
    vs_ok, vs_msg = agent.initialize_vector_store()
    if not vs_ok:
        print(f"Vector store error: {vs_msg}")
        return
        
    # Your code here
    response = agent.ask_question("Your question")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

### Configuration Management

```python
# Session-specific configuration
config = {"configurable": {"thread_id": "my_session"}}

response = agent.ask_question(
    question="What models are available?",
    use_citations=True,
    use_reranking=True,
    config=config
)
```

### Response Processing

```python
response = agent.ask_question("How do I get started?")

print(f"Answer: {response.answer}")
print(f"Citation count: {len(response.citations)}")

for i, citation in enumerate(response.citations, 1):
    print(f"Source {i}: {citation.quote[:100]}...")
```

## Next Steps

1. **Start with Basic Usage**: Review [basic_usage.md](basic_usage.md) for a complete walkthrough
2. **Explore Streaming**: See [streaming.md](streaming.md) for real-time responses  
3. **Try Conversations**: Check [conversation.md](conversation.md) for multi-turn examples
4. **Advanced Features**: Review [advanced.md](advanced.md) for optimization techniques

## Tips for Success

- **Always check prerequisites** before making queries
- **Handle errors gracefully** with try-catch blocks
- **Use conversation memory** for better context awareness
- **Enable reranking** for improved relevance (at cost of speed)
- **Stream responses** for better user experience with long answers 