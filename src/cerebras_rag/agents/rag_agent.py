"""
Core RAG agent implementation for Cerebras documentation system.

This module contains the main CerebrasRAGAgent class that handles:
- Vector database interactions with Pinecone
- LLM conversations using Cerebras models
- Citation generation and document retrieval
- Conversation memory management with LangGraph
"""

import os
import re
from typing import List

from langchain_openai import ChatOpenAI
from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState
from langchain_community.vectorstores import FAISS
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from pinecone import Pinecone
from dotenv import load_dotenv

from .models import Citation, QuotedAnswer

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = "cerebras-docs"


class CerebrasRAGAgent:
    """
    Main agent class for Cerebras documentation RAG system.
    
    This agent provides intelligent access to Cerebras documentation with features including:
    - Semantic search through documentation using Pinecone vector database
    - Citation-backed responses using Cohere embeddings and reranking
    - Conversation memory using LangGraph
    - Streaming responses with real-time citation tracking
    
    Attributes:
        vector_store: Pinecone vector store for document retrieval
        llm: ChatOpenAI instance configured for Cerebras models
        graph: LangGraph instance for conversation management
        memory: MemorySaver for persistent conversation storage
    """
    
    def __init__(self):
        """Initialize the RAG agent with default configuration."""
        self.vector_store = None
        self.llm = None
        self.graph = None
        self.memory = None
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the Language Learning Model with Cerebras configuration."""
        self.llm = ChatOpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL"), 
            api_key=os.getenv("OPENROUTER_API_KEY"), 
            model="qwen/qwen3-32b",
            extra_body={
                "provider": {
                    "only": ["cerebras"]
                }
            }
        )
    
    def check_prerequisites(self):
        """
        Check if all required API keys are available.
        
        Returns:
            tuple: (bool, list) - Success status and list of missing keys
        """
        missing_keys = []
        
        if not os.getenv("OPENROUTER_API_KEY"):
            missing_keys.append("OPENROUTER_API_KEY (for Qwen)")
        
        if not os.getenv("PINECONE_API_KEY"):
            missing_keys.append("PINECONE_API_KEY (for vector database)")
        
        if not os.getenv("COHERE_API_KEY"):
            missing_keys.append("COHERE_API_KEY (for embeddings)")
        
        if missing_keys:
            return False, missing_keys
        
        return True, []
    
    def initialize_vector_store(self):
        """
        Initialize connection to Pinecone vector store.
        
        Returns:
            tuple: (bool, str) - Success status and status message
        """
        if self.vector_store is not None:
            return True, "Already initialized"
            
        # Initialize Pinecone client
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Get the index
        if not pc.has_index(INDEX_NAME):
            return False, f"Pinecone index '{INDEX_NAME}' not found! Please run populate_vectordb.py first."
        
        index = pc.Index(INDEX_NAME)
        
        # Check if index has data
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)
        
        if vector_count == 0:
            return False, f"Pinecone index '{INDEX_NAME}' is empty! Please run populate_vectordb.py first."
        
        # Initialize Cohere embeddings
        embeddings = CohereEmbeddings(
            model="embed-english-v3.0",
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        
        # Create vector store with Pinecone
        self.vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        
        return True, f"Connected successfully with {vector_count:,} vectors"
    
    def initialize_graph(self):
        """Initialize the LangGraph conversation graph for memory management."""
        if self.graph is not None:
            return
            
        # Build the graph
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("call_model", self._call_model)
        graph_builder.add_edge(START, "call_model")
        
        # Compile graph with memory
        self.memory = MemorySaver()
        self.graph = graph_builder.compile(checkpointer=self.memory)
    
    def _clean(self, text: str) -> str:
        """
        Normalize messy document snippets for better readability.
        
        Args:
            text: Raw text from document
            
        Returns:
            str: Cleaned and normalized text
        """
        # Join spaced‑out words
        text = re.sub(r'(?:\b[A-Za-z]\s){2,}\b[A-Za-z]', lambda m: m.group(0).replace(' ', ''), text)
        # Drop sequences of 3+ underscores
        text = re.sub(r'\s*_+\s*', ' ', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        # Tidy punctuation spacing
        text = re.sub(r'\(\s+', '(', text)
        text = re.sub(r'\s+\)', ')', text)
        text = re.sub(r'\s*([:;,.\$])\s*', r'\1 ', text)
        # Remove stray backslashes
        text = text.replace('\\', '')
        return text.strip()
    
    def format_docs_with_id(self, docs: List[Document]) -> str:
        """
        Format documents with source IDs for citation tracking.
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            str: Formatted document text with source IDs
        """
        parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown source")
            title = doc.metadata.get("title", "Untitled")
            snippet = self._clean(doc.page_content)
            
            parts.append(
                f"Source ID: {i}\n"
                f"Document Title: {title}\n"
                f"Source: {source}\n"
                f"Content: {snippet}"
            )
        return "\n\n---\n\n".join(parts)
    
    def is_conversation_history_question(self, question: str) -> bool:
        """
        Detect if the user is asking about their conversation history.
        
        Args:
            question: User's question text
            
        Returns:
            bool: True if question is about conversation history
        """
        history_patterns = [
            r'\bfirst message\b',
            r'\bearlier\b',
            r'\bprevious\b',
            r'\bwhat did i (say|ask|tell)\b',
            r'\bmy (first|last|previous) (message|question)\b',
            r'\bour conversation\b',
            r'\bhistory\b',
            r'\bbefore\b',
            r'\bremember when\b',
            r'\bi (said|asked|told)\b',
            r'\byou (said|told|answered)\b'
        ]
        
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in history_patterns)
    
    def retrieve_with_citations(self, question: str, k: int = 6, use_reranking: bool = False) -> List[Document]:
        """
        Enhanced retrieval function with optional reranking.
        
        Args:
            question: User's question
            k: Number of documents to retrieve
            use_reranking: Whether to use Cohere reranking
            
        Returns:
            List[Document]: Retrieved and optionally reranked documents
        """
        try:
            # Get initial documents from Pinecone
            retrieved_docs = self.vector_store.similarity_search(question, k=k)
            
            if use_reranking and os.getenv("COHERE_API_KEY"):
                try:
                    # Initialize Cohere reranker
                    reranker = CohereRerank(
                        cohere_api_key=os.getenv("COHERE_API_KEY"),
                        model="rerank-english-v3.0",
                        top_n=4
                    )
                    
                    # Create compression retriever with reranking
                    compression_retriever = ContextualCompressionRetriever(
                        base_compressor=reranker,
                        base_retriever=self.vector_store.as_retriever(search_kwargs={"k": k})
                    )
                    
                    # Get reranked results
                    reranked_docs = compression_retriever.invoke(question)
                    return reranked_docs
                    
                except Exception as e:
                    print(f"Warning: Reranking failed, using regular retrieval: {e}")
                    return retrieved_docs
            
            return retrieved_docs
            
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

    def generate_with_citations(self, question: str, documents: List[Document], use_structured_output: bool = True):
        """
        Generate answer with citations using LLM.
        
        Args:
            question: User's question
            documents: Retrieved documents
            use_structured_output: Whether to use structured Pydantic output
            
        Returns:
            QuotedAnswer or dict: Response with citations
        """
        context = self.format_docs_with_id(documents)
        
        if use_structured_output:
            llm_with_structure = self.llm.with_structured_output(QuotedAnswer)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert assistant for Cerebras inference documentation. 
Your job is to answer questions based ONLY on the provided documentation sources.

CITATION REQUIREMENTS:
- You MUST cite specific sources for each claim using the exact Source ID numbers provided
- Include VERBATIM quotes from the sources to support your answer
- If multiple sources support a point, cite all relevant ones
- NEVER make claims without proper citations

ANSWER REQUIREMENTS:
- Answer based ONLY on the provided sources - do not use external knowledge
- If the sources don't contain enough information, say so explicitly
- Be thorough but concise
- Use clear, professional language

Sources:
{context}"""),
            ("human", "{question}")
        ])
        
        chain = prompt | (llm_with_structure if use_structured_output else self.llm)
        
        try:
            response = chain.invoke({
                "context": context,
                "question": question
            })
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback to basic response
            if use_structured_output:
                return QuotedAnswer(
                    answer=f"I encountered an error generating a response: {str(e)}",
                    citations=[]
                )
            else:
                return {"answer": f"I encountered an error generating a response: {str(e)}"}

    def _call_model(self, state: MessagesState):
        """
        Internal method for LangGraph to call the model.
        
        Args:
            state: Current conversation state
            
        Returns:
            dict: Updated state with new message
        """
        # Pass messages directly to the LLM without trimming
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}
    
    def get_conversation_history(self, config: dict = {"configurable": {"thread_id": "1"}}):
        """
        Get the conversation history for a specific thread.
        
        Args:
            config: LangGraph configuration with thread_id
            
        Returns:
            list: List of conversation messages
        """
        if not self.graph:
            return []
        
        try:
            # Get the current state
            current_state = self.graph.get_state(config)
            if current_state and "messages" in current_state.values:
                return current_state.values["messages"]
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
        
        return []
    
    def stream_response_with_citations(self, question: str, use_citations: bool = True, 
                                     use_reranking: bool = False, config: dict = None):
        """
        Stream response with citations in real-time.
        
        Args:
            question: User's question
            use_citations: Whether to include citations
            use_reranking: Whether to use document reranking
            config: LangGraph configuration
            
        Yields:
            dict: Streaming response chunks
        """
        if config is None:
            config = {"configurable": {"thread_id": "1"}}
        
        try:
            # Check if it's a conversation history question
            if self.is_conversation_history_question(question):
                yield from self._handle_history_question(question, config)
                return
            
            # Retrieve documents
            if use_citations:
                yield {"type": "status", "message": "🔍 Retrieving relevant documentation..."}
                documents = self.retrieve_with_citations(question, use_reranking=use_reranking)
                
                if not documents:
                    yield {
                        "type": "error", 
                        "message": "No relevant documents found. Please check if the vector database is populated."
                    }
                    return
                
                yield {"type": "status", "message": f"📄 Retrieved {len(documents)} relevant documents"}
                yield {"type": "status", "message": "📝 Generating response with citations..."}
                
                # Generate response with citations
                response = self.generate_with_citations(question, documents)
                
                # Stream the response
                yield {"type": "answer", "content": response.answer}
                
                if response.citations:
                    yield {"type": "citations_header"}
                    for citation in response.citations:
                        if citation.source_id < len(documents):
                            doc = documents[citation.source_id]
                            source_url = doc.metadata.get("source", "Unknown source")
                            title = doc.metadata.get("title", "Untitled")
                            
                            yield {
                                "type": "citation",
                                "source_id": citation.source_id,
                                "quote": citation.quote,
                                "title": title,
                                "url": source_url
                            }
                
                # Add to conversation memory
                if self.graph:
                    try:
                        self.graph.invoke({
                            "messages": [
                                HumanMessage(content=question),
                                AIMessage(content=response.answer)
                            ]
                        }, config=config)
                    except Exception as e:
                        yield {"type": "warning", "message": f"Failed to save to memory: {e}"}
            
            else:
                # Direct LLM response without citations
                yield {"type": "status", "message": "🤖 Generating response..."}
                
                if self.graph:
                    # Use conversation graph for memory
                    for chunk in self.graph.stream({
                        "messages": [HumanMessage(content=question)]
                    }, config=config, stream_mode="values"):
                        if "messages" in chunk and chunk["messages"]:
                            last_message = chunk["messages"][-1]
                            if isinstance(last_message, AIMessage):
                                yield {"type": "answer", "content": last_message.content}
                else:
                    # Fallback to direct LLM
                    response = self.llm.invoke([HumanMessage(content=question)])
                    yield {"type": "answer", "content": response.content}
        
        except Exception as e:
            yield {"type": "error", "message": f"An error occurred: {str(e)}"}

    def _handle_history_question(self, question: str, config: dict):
        """
        Handle questions about conversation history.
        
        Args:
            question: User's question about history
            config: LangGraph configuration
            
        Yields:
            dict: Response chunks for history questions
        """
        yield {"type": "status", "message": "🔍 Searching conversation history..."}
        
        history = self.get_conversation_history(config)
        
        if not history:
            yield {
                "type": "answer", 
                "content": "I don't have any conversation history to reference. This appears to be the start of our conversation."
            }
            return
        
        # Format history for LLM
        history_text = "\n".join([
            f"{'Human' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in history
        ])
        
        # Use LLM to answer based on history
        prompt = f"""Based on our conversation history, please answer this question: {question}

Conversation History:
{history_text}"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        yield {"type": "answer", "content": response.content}
        
        # Save this interaction to memory
        if self.graph:
            try:
                self.graph.invoke({
                    "messages": [
                        HumanMessage(content=question),
                        AIMessage(content=response.content)
                    ]
                }, config=config)
            except Exception as e:
                yield {"type": "warning", "message": f"Failed to save to memory: {e}"}

    def ask_question(self, question: str, use_citations: bool = True, use_reranking: bool = False, 
                    config: dict = None) -> QuotedAnswer:
        """
        Ask a question and get a complete response with citations.
        
        Args:
            question: User's question
            use_citations: Whether to include citations
            use_reranking: Whether to use document reranking
            config: LangGraph configuration
            
        Returns:
            QuotedAnswer: Complete response with answer and citations
        """
        if config is None:
            config = {"configurable": {"thread_id": "1"}}
        
        try:
            # Check if it's a conversation history question
            if self.is_conversation_history_question(question):
                history = self.get_conversation_history(config)
                if not history:
                    return QuotedAnswer(
                        answer="I don't have any conversation history to reference. This appears to be the start of our conversation.",
                        citations=[]
                    )
                
                # Format and process history question
                history_text = "\n".join([
                    f"{'Human' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                    for msg in history
                ])
                
                prompt = f"Based on our conversation history, please answer this question: {question}\n\nConversation History:\n{history_text}"
                response = self.llm.invoke([HumanMessage(content=prompt)])
                
                result = QuotedAnswer(answer=response.content, citations=[])
                
                # Save to memory
                if self.graph:
                    self.graph.invoke({
                        "messages": [
                            HumanMessage(content=question),
                            AIMessage(content=response.content)
                        ]
                    }, config=config)
                
                return result
            
            # Regular question processing
            if use_citations:
                documents = self.retrieve_with_citations(question, use_reranking=use_reranking)
                if not documents:
                    return QuotedAnswer(
                        answer="No relevant documents found. Please check if the vector database is populated.",
                        citations=[]
                    )
                
                response = self.generate_with_citations(question, documents)
                
                # Add to conversation memory
                if self.graph:
                    self.graph.invoke({
                        "messages": [
                            HumanMessage(content=question),
                            AIMessage(content=response.answer)
                        ]
                    }, config=config)
                
                return response
            
            else:
                # Direct LLM response without citations
                if self.graph:
                    result = self.graph.invoke({
                        "messages": [HumanMessage(content=question)]
                    }, config=config)
                    last_message = result["messages"][-1]
                    return QuotedAnswer(answer=last_message.content, citations=[])
                else:
                    response = self.llm.invoke([HumanMessage(content=question)])
                    return QuotedAnswer(answer=response.content, citations=[])
        
        except Exception as e:
            return QuotedAnswer(
                answer=f"An error occurred while processing your question: {str(e)}",
                citations=[]
            )


def get_agent() -> CerebrasRAGAgent:
    """
    Factory function to get a CerebrasRAGAgent instance.
    
    Returns:
        CerebrasRAGAgent: Configured agent instance
    """
    return CerebrasRAGAgent() 