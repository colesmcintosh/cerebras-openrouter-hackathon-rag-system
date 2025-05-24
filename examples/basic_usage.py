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


def streaming_example():
    """Demonstrate streaming responses."""
    print("\n🌊 Streaming Response Example")
    print("=" * 50)
    
    agent = get_agent()
    
    # Check and initialize
    prereq_ok, _ = agent.check_prerequisites()
    if not prereq_ok:
        print("❌ Prerequisites not met")
        return
    
    vs_ok, _ = agent.initialize_vector_store()
    if not vs_ok:
        print("❌ Vector store not available")
        return
    
    agent.initialize_graph()
    
    question = "How do I get started with Cerebras inference?"
    print(f"📋 Question: {question}")
    print("\n🔄 Streaming response:")
    
    # Stream the response
    for chunk in agent.stream_response_with_citations(
        question=question,
        use_citations=True,
        use_reranking=False
    ):
        if chunk["type"] == "status":
            print(f"ℹ️ {chunk['message']}")
        elif chunk["type"] == "answer":
            print(f"💬 {chunk['content']}")
        elif chunk["type"] == "citation":
            print(f"📚 Source {chunk['source_id']}: {chunk['title']}")
        elif chunk["type"] == "error":
            print(f"❌ {chunk['message']}")


def conversation_example():
    """Demonstrate conversation memory."""
    print("\n💭 Conversation Memory Example")
    print("=" * 50)
    
    agent = get_agent()
    
    # Check and initialize
    prereq_ok, _ = agent.check_prerequisites()
    if not prereq_ok:
        print("❌ Prerequisites not met")
        return
    
    vs_ok, _ = agent.initialize_vector_store()
    if not vs_ok:
        print("❌ Vector store not available")
        return
    
    agent.initialize_graph()
    
    # Conversation with memory
    conversation = [
        "What is Cerebras?",
        "How fast is their inference?",
        "What was my first question?"  # This tests memory
    ]
    
    config = {"configurable": {"thread_id": "example_conversation"}}
    
    for i, question in enumerate(conversation, 1):
        print(f"\n💬 Turn {i}: {question}")
        
        response = agent.ask_question(
            question=question,
            use_citations=True,
            config=config
        )
        
        print(f"🤖 Response: {response.answer[:200]}...")


if __name__ == "__main__":
    try:
        # Run basic example
        main()
        
        # Run streaming example
        streaming_example()
        
        # Run conversation example
        conversation_example()
        
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc() 