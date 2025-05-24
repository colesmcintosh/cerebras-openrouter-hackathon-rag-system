# CLI Interface

The Cerebras RAG system includes a professional command-line interface for interactive question-answering with real-time configuration and conversation management.

## Overview

The CLI provides:
- Interactive question-answering with citations
- Live configuration (citations, reranking)
- Conversation history tracking
- Professional terminal interface with color coding
- Session management and command help

## Installation

The CLI requires the `rich` library for enhanced terminal formatting:

```bash
pip install rich
```

If `rich` is not installed, the CLI will fall back to basic text output.

## Usage

### Starting the CLI

```bash
# From the project root
python -m src.cerebras_rag.interfaces.cli

# Or if installed as a package
cerebras-rag-cli
```

### Basic Operation

1. **System Initialization**: The CLI automatically checks prerequisites and initializes the vector store
2. **Interactive Mode**: Enter questions naturally or use commands
3. **Real-time Responses**: Get streaming responses with citations
4. **Session Management**: Conversation history is maintained throughout the session

## Commands

### Help Commands

- **`help`** - Display available commands and usage instructions
- **`status`** - Show current system status and configuration

### Configuration Commands

- **`citations on`** - Enable citation mode (default)
- **`citations off`** - Disable citation mode
- **`reranking on`** - Enable document reranking for better relevance
- **`reranking off`** - Disable document reranking (default)

### History Commands

- **`history`** - Display conversation history for the current session

### Exit Commands

- **`quit`** - Exit the application
- **`exit`** - Exit the application

## Features

### Real-time Configuration

Change settings during your session:

```
> citations off
Citations disabled

> reranking on  
Reranking enabled

> status
┏━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Setting     ┃ Status  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Citations   │ ❌ OFF  │
│ Reranking   │ ✅ ON   │
│ Conversation│ 💬 3 messages │
└─────────────┴─────────┘
```

### Streaming Responses

Questions receive real-time streaming responses:

```
> How do I authenticate with the Cerebras API?

🔍 Retrieving relevant documents...
✅ Found 6 relevant documents
🤖 Generating response...

💬 To authenticate with the Cerebras API, you need to include your API key in the request headers...

📚 Sources:
  1. "Authentication is handled via API keys in the Authorization header" (cerebras-docs.md)
  2. "Set the header as 'Authorization: Bearer YOUR_API_KEY'" (api-reference.md)
```

### Conversation Memory

The system maintains conversation context:

```
> What models are available?
💬 Cerebras offers several models including llama3.1-8b, llama3.1-70b, and qwen3-32b...

> Which one is fastest?
💬 Based on our previous discussion about available models, the llama3.1-8b is typically the fastest...
```

### Error Handling

The CLI gracefully handles various error conditions:

- Missing API keys
- Vector store connection issues  
- Network timeouts
- Invalid commands

## CerebrasRAGCLI Class

The CLI is implemented in the `CerebrasRAGCLI` class with the following key methods:

### `__init__()`

```python
def __init__(self):
    """Initialize the CLI with default settings."""
```

Initializes the CLI with:
- Rich console for formatting (if available)
- RAG agent instance
- Default configuration (citations on, reranking off)
- Session configuration for conversation threading

### `display_header()`

```python
def display_header(self):
    """Display the application header."""
```

Shows the application title and subtitle with formatted panels.

### `display_status()`

```python
def display_status(self):
    """Display current system status and configuration."""
```

Shows current settings in a formatted table including:
- Citations status
- Reranking status  
- Conversation message count

### `display_help()`

```python
def display_help(self):
    """Display available commands and usage instructions."""
```

Shows comprehensive help information with all available commands and tips.

### `handle_command()`

```python
def handle_command(self, user_input: str) -> bool:
    """Handle special commands."""
```

Processes special commands and returns `True` if a command was handled.

### `stream_response()`

```python
def stream_response(self, question: str):
    """Stream the response with live updates."""
```

Handles real-time streaming of responses with status updates and citations.

### `run()`

```python
def run(self):
    """Main CLI loop."""
```

Main application loop that handles user input and processes questions/commands.

## Configuration

The CLI uses the same environment variables as the main agent:

- `OPENROUTER_API_KEY`: For Qwen model access
- `PINECONE_API_KEY`: For vector database
- `COHERE_API_KEY`: For embeddings and reranking

## Example Session

```
═══════════════════════════════════════════════════════════
Cerebras Documentation RAG System
Intelligent documentation assistant with citations
═══════════════════════════════════════════════════════════

🚀 Checking system prerequisites...
✅ All API keys found
🔗 Connecting to vector store...
✅ Connected successfully with 1,247 vectors
🧠 Initializing conversation memory...
✅ System ready!

Type 'help' for commands or ask a question about Cerebras.

> How do I get started with Cerebras inference?

🔍 Retrieving relevant documents...
✅ Found 6 relevant documents
🤖 Generating response...

💬 To get started with Cerebras inference, you need to...

📚 Sources:
  1. "Sign up for an account at cerebras.ai and get your API key" (getting-started.md)
  2. "Install the cerebras client library: pip install cerebras" (installation.md)

> citations off
Citations disabled

> What about rate limits?

🔍 Retrieving relevant documents...
🤖 Generating response...

💬 Cerebras has different rate limits depending on your subscription tier...

> quit
Goodbye! 👋 