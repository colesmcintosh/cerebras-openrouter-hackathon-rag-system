"""
Pydantic models for structured outputs and data validation.
"""

from typing import List
from pydantic import BaseModel, Field


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