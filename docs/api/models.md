# Data Models

This document describes the Pydantic models used for structured data validation and output in the Cerebras RAG system.

## Citation

```python
class Citation(BaseModel):
    """A citation referencing a specific source document."""
    
    source_id: int = Field(
        ...,
        description="The integer ID of a SPECIFIC source which justifies the answer.",
    )
    quote: str = Field(
        ...,
        description="The VERBATIM quote from the specified source that justifies the answer.",
    )
```

Represents a citation from a source document.

### Fields

- **`source_id`** (int): Integer ID of the source document
- **`quote`** (str): Verbatim quote from the source that supports the answer

### Example

```python
citation = Citation(
    source_id=0,
    quote="To authenticate with the Cerebras API, you need to set your API key in the request headers."
)

print(f"Source {citation.source_id}: {citation.quote}")
```

## QuotedAnswer

```python
class QuotedAnswer(BaseModel):
    """A response that includes citations from source documents."""
    
    answer: str = Field(
        ...,
        description="The answer to the user question, which is based only on the given sources.",
    )
    citations: List[Citation] = Field(
        ..., 
        description="Citations from the given sources that justify the answer."
    )
```

Represents a complete response with answer and supporting citations.

### Fields

- **`answer`** (str): The complete answer to the user's question
- **`citations`** (List[Citation]): List of citations that support the answer

### Example

```python
from cerebras_rag.agents.models import QuotedAnswer, Citation

response = QuotedAnswer(
    answer="To authenticate with the Cerebras API, include your API key in the Authorization header.",
    citations=[
        Citation(
            source_id=0,
            quote="Authentication is handled via API keys in the Authorization header"
        ),
        Citation(
            source_id=1, 
            quote="Set the header as 'Authorization: Bearer YOUR_API_KEY'"
        )
    ]
)

print(f"Answer: {response.answer}")
print(f"Number of citations: {len(response.citations)}")

for i, citation in enumerate(response.citations, 1):
    print(f"Citation {i} (Source {citation.source_id}): {citation.quote}")
```

## Usage in API

These models are used throughout the API to ensure structured, validated responses:

### In CerebrasRAGAgent

```python
# ask_question returns a QuotedAnswer
response = agent.ask_question("How do I authenticate?")
# response is a QuotedAnswer object with answer and citations

# Each citation in response.citations is a Citation object
for citation in response.citations:
    print(f"Source {citation.source_id}: {citation.quote}")
```

### In Streaming Responses

When streaming responses, citations are provided as individual chunks:

```python
for chunk in agent.stream_response_with_citations("What models are available?"):
    if chunk["type"] == "citation":
        # Citation data is provided in the chunk
        source_id = chunk["source_id"]
        quote = chunk["quote"] 
        title = chunk["title"]
```

## Validation

Both models use Pydantic for automatic validation:

- **Required fields**: All fields are required and must be provided
- **Type checking**: Field types are automatically validated
- **Serialization**: Models can be easily converted to/from JSON

### Example Validation

```python
# This will raise a ValidationError
try:
    invalid_citation = Citation(source_id="not_an_integer")
except ValidationError as e:
    print(f"Validation error: {e}")

# This will also raise a ValidationError  
try:
    incomplete_answer = QuotedAnswer(answer="Just an answer")  # Missing citations
except ValidationError as e:
    print(f"Validation error: {e}")
```

## JSON Serialization

Models can be easily serialized to JSON:

```python
response = QuotedAnswer(
    answer="The answer",
    citations=[Citation(source_id=0, quote="Supporting quote")]
)

# Convert to JSON
json_data = response.model_dump()
print(json_data)
# Output: {'answer': 'The answer', 'citations': [{'source_id': 0, 'quote': 'Supporting quote'}]}

# Convert to JSON string
json_string = response.model_dump_json()
print(json_string)
``` 