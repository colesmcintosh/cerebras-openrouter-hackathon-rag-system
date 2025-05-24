"""
Cerebras Documentation RAG System

An advanced RAG (Retrieval-Augmented Generation) system that provides intelligent 
access to Cerebras inference documentation with citations, conversation memory, 
and multiple interfaces.
"""

__version__ = "1.0.0"
__author__ = "Cerebras RAG Team"

from .agents.rag_agent import CerebrasRAGAgent, get_agent
from .agents.models import Citation, QuotedAnswer

__all__ = [
    "CerebrasRAGAgent",
    "get_agent", 
    "Citation",
    "QuotedAnswer"
] 