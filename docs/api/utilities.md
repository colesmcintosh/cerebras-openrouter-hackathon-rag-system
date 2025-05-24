# Utilities

This document describes the utility functions and scripts included with the Cerebras RAG system.

## populate_vectordb.py

The main utility for setting up and populating the Pinecone vector database with Cerebras documentation.

### Overview

This script handles:
- Downloading and processing Cerebras documentation
- Chunking documents for optimal retrieval  
- Generating embeddings using Cohere
- Uploading to Pinecone vector database
- Index management and configuration

### Usage

```bash
# From the project root
python -m src.cerebras_rag.utils.populate_vectordb

# Or directly
python src/cerebras_rag/utils/populate_vectordb.py
```

### Prerequisites

Before running the population script, ensure you have:

1. **API Keys configured** in your `.env` file:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key
   COHERE_API_KEY=your_cohere_api_key
   ```

2. **Required dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

### Process Flow

The script follows this process:

1. **Initialize Services**
   - Connect to Pinecone
   - Initialize Cohere embeddings
   - Validate API connections

2. **Document Collection**
   - Download/locate Cerebras documentation
   - Parse and clean document content
   - Extract metadata (titles, sources, etc.)

3. **Document Processing**
   - Split documents into chunks for optimal retrieval
   - Generate embeddings for each chunk
   - Prepare metadata for indexing

4. **Vector Database Population**
   - Create Pinecone index if needed
   - Upload document chunks with embeddings
   - Verify successful upload

### Configuration

The script uses several configuration parameters:

```python
# Index configuration
INDEX_NAME = "cerebras-docs"
DIMENSION = 1024  # Cohere embed-english-v3.0 dimension
METRIC = "cosine"

# Document processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

### Output

The script provides detailed progress information:

```
🚀 Starting Cerebras Documentation Population
══════════════════════════════════════════════

📝 Initializing services...
✅ Pinecone connected
✅ Cohere embeddings initialized

📚 Processing documents...
✅ Found 42 documentation files
✅ Generated 1,247 document chunks

🔗 Uploading to vector database...
✅ Index 'cerebras-docs' created
✅ Uploaded 1,247 vectors
✅ Population completed successfully!

Summary:
- Documents processed: 42
- Chunks generated: 1,247  
- Upload time: 2m 14s
```

### Error Handling

The script handles common issues:

- **Missing API keys**: Clear error messages with setup instructions
- **Network issues**: Retry logic for upload failures
- **Index conflicts**: Options to recreate or update existing indexes
- **Memory issues**: Batch processing for large document sets

### Supported Document Formats

The utility can process various document formats:

- **Markdown** (`.md`) - Primary format for documentation
- **Text** (`.txt`) - Plain text documents  
- **HTML** (`.html`) - Web documentation
- **PDF** (`.pdf`) - With text extraction

### Document Metadata

Each processed document includes metadata:

```python
{
    "source": "path/to/document.md",
    "title": "Document Title",
    "section": "Chapter/Section Name",
    "doc_type": "markdown",
    "chunk_index": 0,
    "total_chunks": 5
}
```

### Chunking Strategy

Documents are split using intelligent chunking:

- **Respect boundaries**: Avoid splitting mid-sentence or mid-paragraph
- **Preserve context**: Include overlap between chunks
- **Optimize size**: Balance retrieval relevance and context length
- **Maintain metadata**: Preserve source information for citations

### Example Usage in Code

```python
from src.cerebras_rag.utils.populate_vectordb import populate_vector_database

# Programmatic usage
result = populate_vector_database(
    index_name="cerebras-docs",
    doc_directory="./cerebras_docs/",
    force_recreate=False
)

if result["success"]:
    print(f"Successfully populated {result['vector_count']} vectors")
else:
    print(f"Error: {result['error']}")
```

### Command Line Options

The script supports various command line options:

```bash
# Recreate index from scratch
python populate_vectordb.py --force-recreate

# Use custom index name
python populate_vectordb.py --index-name my-custom-index

# Process specific directory
python populate_vectordb.py --docs-dir /path/to/docs

# Verbose output
python populate_vectordb.py --verbose

# Help
python populate_vectordb.py --help
```

### Performance Considerations

- **Batch uploads**: Processes documents in batches to optimize API usage
- **Rate limiting**: Respects API rate limits with backoff strategies
- **Memory management**: Processes large document sets efficiently
- **Parallel processing**: Uses threading for embedding generation

### Troubleshooting

Common issues and solutions:

#### "Index already exists" error
```bash
# Force recreate the index
python populate_vectordb.py --force-recreate
```

#### "No documents found" error
- Verify document directory path
- Check file permissions
- Ensure supported file formats

#### "API key invalid" error  
- Verify API keys in `.env` file
- Check API key permissions
- Validate account status

#### "Upload failed" error
- Check network connectivity
- Verify Pinecone index configuration
- Review batch size settings

### Integration with Main System

Once populated, the vector database is automatically used by the main RAG system:

```python
from cerebras_rag import get_agent

agent = get_agent()

# This will connect to the populated database
vs_ok, msg = agent.initialize_vector_store()
if vs_ok:
    print("Connected to populated vector store")
``` 