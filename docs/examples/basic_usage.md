# Basic Usage Example

This example demonstrates the core functionality of the Cerebras RAG system, including initialization, question-answering with citations, streaming responses, and conversation memory.

## Overview

The `examples/basic_usage.py` file provides a comprehensive demonstration of:

1. **System initialization** and prerequisite checking
2. **Simple question-answering** with citations
3. **Streaming responses** for real-time feedback
4. **Conversation memory** for context preservation

## Complete Example

```python
"""
Basic usage example for the Cerebras RAG system.

This example demonstrates how to:
1. Initialize the RAG agent
2. Ask questions with citations
3. Handle responses and citations
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.cerebras_rag import get_agent, CerebrasRAGAgent

def main():
    """Demonstrate basic usage of the Cerebras RAG system."""
    print("🚀 Cerebras RAG Basic Usage Example")
    print("=" * 50)
    
    # Initialize the agent
    print("📝 Initializing RAG agent...")
    agent = get_agent()
    
    # Check prerequisites
    prereq_ok, missing_keys = agent.check_prerequisites()
    if not prereq_ok:
        print(f"❌ Missing API keys: {', '.join(missing_keys)}")
        print("Please set the required environment variables in your .env file")
        return
    
    # Initialize vector store
    print("🔗 Connecting to vector store...")
    vs_ok, vs_msg = agent.initialize_vector_store()
    if not vs_ok:
        print(f"❌ Vector store error: {vs_msg}")
        return
    
    print(f"✅ {vs_msg}")
    
    # Initialize conversation graph
    print("🧠 Setting up conversation memory...")
    agent.initialize_graph()
    
    # Example questions
    questions = [
        "How do I authenticate with the Cerebras API?",
        "What models are available for inference?",
        "How do I make streaming requests?",
        "What are the rate limits?"
    ]
    
    print("\n🤖 Running example queries...")
    print("-" * 30)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📋 Question {i}: {question}")
        
        try:
            # Ask question with citations
            response = agent.ask_question(
                question=question,
                use_citations=True,
                use_reranking=False  # Set to True for better relevance
            )
            
            # Display answer
            print(f"💬 Answer: {response.answer}")
            
            # Display citations
            if response.citations:
                print("\n📚 Sources:")
                for j, citation in enumerate(response.citations, 1):
                    print(f"  {j}. \"{citation.quote[:100]}...\"")
            else:
                print("📚 No citations found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main()
```

## Step-by-Step Breakdown

### 1. System Initialization

```python
# Initialize the agent
agent = get_agent()
```

The `get_agent()` factory function creates a new `CerebrasRAGAgent` instance with default configuration.

### 2. Prerequisites Check

```python
prereq_ok, missing_keys = agent.check_prerequisites()
if not prereq_ok:
    print(f"❌ Missing API keys: {', '.join(missing_keys)}")
    return
```

**What it does:**
- Validates required environment variables are set
- Returns a tuple: (success_boolean, list_of_missing_keys)

**Required environment variables:**
- `OPENROUTER_API_KEY`: For Qwen model access via Cerebras
- `PINECONE_API_KEY`: For vector database connection
- `COHERE_API_KEY`: For embeddings and reranking

### 3. Vector Store Connection

```python
vs_ok, vs_msg = agent.initialize_vector_store()
if not vs_ok:
    print(f"❌ Vector store error: {vs_msg}")
    return
```

**What it does:**
- Connects to Pinecone vector database
- Validates the `cerebras-docs` index exists and has data
- Returns success status and descriptive message

**Common error messages:**
- "Pinecone index 'cerebras-docs' not found! Please run populate_vectordb.py first."
- "Pinecone index 'cerebras-docs' is empty! Please run populate_vectordb.py first."

### 4. Conversation Memory Setup

```python
agent.initialize_graph()
```

**What it does:**
- Initializes LangGraph for conversation memory
- Sets up the conversation state management
- Enables context-aware multi-turn conversations

### 5. Asking Questions

```python
response = agent.ask_question(
    question=question,
    use_citations=True,
    use_reranking=False
)
```

**Parameters:**
- `question` (str): The user's question
- `use_citations` (bool): Include source citations (default: True)
- `use_reranking` (bool): Use Cohere reranking for better relevance (default: False)

**Returns:**
- `QuotedAnswer` object with `answer` and `citations` fields

### 6. Processing Responses

```python
print(f"💬 Answer: {response.answer}")

if response.citations:
    print("\n📚 Sources:")
    for j, citation in enumerate(response.citations, 1):
        print(f"  {j}. \"{citation.quote[:100]}...\"")
```

**Response structure:**
- `response.answer`: The complete answer string
- `response.citations`: List of `Citation` objects
- Each citation has `source_id` and `quote` fields

## Expected Output

When run successfully, you should see output like:

```
🚀 Cerebras RAG Basic Usage Example
==================================================
📝 Initializing RAG agent...
🔗 Connecting to vector store...
✅ Connected successfully with 1,247 vectors
🧠 Setting up conversation memory...

🤖 Running example queries...
------------------------------

📋 Question 1: How do I authenticate with the Cerebras API?
💬 Answer: To authenticate with the Cerebras API, you need to include your API key in the Authorization header of your requests...

📚 Sources:
  1. "Authentication is handled via API keys in the Authorization header format: 'Authorization: Bearer YOUR_API_KEY'..."
  2. "You can obtain your API key from the Cerebras dashboard under the API Keys section..."

------------------------------

📋 Question 2: What models are available for inference?
💬 Answer: Cerebras offers several models for inference including llama3.1-8b, llama3.1-70b, and qwen3-32b...

📚 Sources:
  1. "Currently supported models include: llama3.1-8b for fast inference, llama3.1-70b for high quality..."

------------------------------
...
✅ Example completed!
```

## Customization Options

### Enable Reranking

For better relevance at the cost of speed:

```python
response = agent.ask_question(
    question=question,
    use_citations=True,
    use_reranking=True  # Enable Cohere reranking
)
```

### Custom Configuration

For conversation threading:

```python
config = {"configurable": {"thread_id": "my_custom_session"}}

response = agent.ask_question(
    question=question,
    use_citations=True,
    config=config
)
```

### Disable Citations

For faster responses without source references:

```python
response = agent.ask_question(
    question=question,
    use_citations=False
)
```

## Error Handling

The example includes comprehensive error handling:

```python
try:
    response = agent.ask_question(question=question)
    # Process response
except Exception as e:
    print(f"❌ Error: {str(e)}")
```

**Common errors:**
- Network connectivity issues
- API rate limit exceeded  
- Invalid API keys
- Vector store connection problems

## Running the Example

```bash
# From project root
python examples/basic_usage.py

# With verbose output
python examples/basic_usage.py --verbose

# With custom questions
python examples/basic_usage.py --questions "What is Cerebras?" "How fast is inference?"
```

## Next Steps

After running the basic example:

1. **Try streaming**: See [streaming.md](streaming.md) for real-time responses
2. **Explore conversations**: Check [conversation.md](conversation.md) for multi-turn examples  
3. **Advanced usage**: Review [advanced.md](advanced.md) for optimization techniques
4. **CLI interface**: Try the interactive CLI with `python -m src.cerebras_rag.interfaces.cli` 