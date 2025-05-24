# Enhanced RAG Chatbot with Citation Support

This enhanced version of the Cerebras Documentation RAG Chatbot includes advanced citation tracking and document reranking capabilities inspired by modern RAG best practices.

## 🆕 New Features

### 📚 Citation Tracking
- **Structured Citations**: Responses now include specific source citations with exact quotes
- **Source ID Tracking**: Each document is assigned a unique ID for precise referencing
- **Verbatim Quotes**: Citations include exact text snippets that support the answer
- **Citation Validation**: Structured output ensures proper citation format

### 🔄 Document Reranking
- **Cohere Reranking**: Optional use of Cohere's rerank-english-v3.0 model
- **Improved Relevance**: Better document selection through semantic reranking
- **Flexible Configuration**: Can be enabled/disabled per query

### 🧹 Enhanced Document Processing
- **Text Cleaning**: Advanced text normalization for better readability
- **Metadata Preservation**: Maintains source information and document titles
- **Formatted Output**: Clean, structured document presentation

## 🛠️ Usage

### Basic Citation Mode
```python
from agent import stream_with_citations

# Get response with citations
response = stream_with_citations(
    "How do I authenticate with Cerebras API?",
    use_citations=True,
    use_reranking=False
)
```

### With Reranking
```python
# Enhanced retrieval with reranking
response = stream_with_citations(
    "What models are available on Cerebras?",
    use_citations=True,
    use_reranking=True  # Uses more API calls but better results
)
```

### Interactive Commands
When running the chatbot interactively, you can use these commands:

- `citations on/off` - Toggle citation mode
- `reranking on/off` - Toggle document reranking
- `status` - Show current configuration
- `history` - View conversation history

## 📊 Response Format

### With Citations Enabled
```
🤖 Assistant: Cerebras provides authentication through API keys that you need to include in your requests.

📚 Sources:
   [1] Source 0: "Authentication is handled via API keys that must be included in the Authorization header"
   [2] Source 2: "You can obtain your API key from the Cerebras dashboard under the API section"
```

### Citation Data Structure
```python
class Citation(BaseModel):
    source_id: int  # ID of the source document
    quote: str      # Exact quote from the source

class QuotedAnswer(BaseModel):
    answer: str              # The main response
    citations: List[Citation] # Supporting citations
```

## 🔧 Configuration

### Environment Variables
Ensure you have these API keys in your `.env` file:

```bash
OPENROUTER_API_KEY=your_openrouter_key
PINECONE_API_KEY=your_pinecone_key
COHERE_API_KEY=your_cohere_key  # Required for reranking
```

### Performance Considerations

#### Citation Mode
- **Pros**: Verifiable sources, structured output, better trustworthiness
- **Cons**: Slightly slower response generation, more complex output parsing

#### Reranking Mode
- **Pros**: Better document relevance, improved answer quality
- **Cons**: Additional API calls to Cohere, increased latency and cost

## 🧪 Testing

Run the test script to verify citation functionality:

```bash
python test_citations.py
```

This will test:
- Basic citation retrieval
- Document reranking
- Interactive citation mode

## 📈 Performance Comparison

| Mode | Speed | Accuracy | API Calls | Cost |
|------|-------|----------|-----------|------|
| Standard | Fast | Good | Low | Low |
| Citations | Medium | Better | Medium | Medium |
| Citations + Reranking | Slower | Best | High | Higher |

## 🔍 How It Works

### 1. Document Retrieval
```python
# Standard retrieval from Pinecone
docs = vector_store.similarity_search(question, k=6)

# Optional reranking with Cohere
if use_reranking:
    reranked_docs = contextual_compression_retriever.invoke(question)
```

### 2. Document Formatting
```python
# Add source IDs and clean text
formatted_docs = format_docs_with_id(documents)
```

### 3. Structured Generation
```python
# Generate response with citations
structured_llm = llm.with_structured_output(QuotedAnswer)
response = structured_llm.invoke(prompt_with_context)
```

## 🎯 Use Cases

### High-Trust Applications
Enable citations for applications requiring source verification:
- Research assistance
- Technical documentation
- Compliance queries
- Fact-checking scenarios

### Performance-Critical Applications
Disable citations for faster responses:
- Real-time chat
- High-volume queries
- Simple Q&A scenarios

## 🔮 Future Enhancements

Potential improvements for the citation system:
- **PDF Upload Support**: Process user-uploaded documents
- **Citation Confidence Scores**: Rate citation reliability
- **Multi-source Aggregation**: Combine information from multiple sources
- **Citation Chain Tracking**: Follow citation relationships
- **Export Citations**: Generate bibliography formats

## 🐛 Troubleshooting

### Common Issues

1. **No Citations Generated**
   - Check that documents were retrieved successfully
   - Verify Cohere API key is set
   - Try lowering the citation requirements

2. **Reranking Failures**
   - Ensure Cohere API key is valid
   - Check network connectivity
   - Falls back to standard retrieval automatically

3. **Structured Output Errors**
   - Model may not support structured output well
   - Automatically falls back to regular response
   - Check model compatibility

### Debug Mode
Enable debug output by modifying the retrieval functions to print intermediate results.

## 📝 License

This enhanced citation system maintains the same license as the original project. 