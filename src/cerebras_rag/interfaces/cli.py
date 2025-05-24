"""
Command-line interface for the Cerebras RAG system.

This module provides a professional CLI for interacting with the Cerebras documentation
RAG system, featuring:
- Interactive question-answering with citations
- Live configuration (citations, reranking)
- Conversation history tracking
- Professional terminal interface with color coding
- Session management and command help
"""

import os
import asyncio
from typing import Dict, Any
import sys

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.markdown import Markdown
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")

# Import the agent from the new package structure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.cerebras_rag.agents.rag_agent import get_agent
from src.cerebras_rag.agents.models import QuotedAnswer


class CerebrasRAGCLI:
    """
    Professional command-line interface for the Cerebras RAG system.
    
    Provides an interactive terminal interface with rich formatting,
    conversation management, and real-time configuration options.
    """
    
    def __init__(self):
        """Initialize the CLI with default settings."""
        self.console = Console() if RICH_AVAILABLE else None
        self.agent = get_agent()
        self.citations_enabled = True
        self.reranking_enabled = False
        self.session_config = {"configurable": {"thread_id": "cli_session"}}
        self.conversation_history = []
        self.running = True
        
    def display_header(self):
        """Display the application header."""
        if not RICH_AVAILABLE:
            print("=" * 60)
            print("CEREBRAS DOCUMENTATION RAG SYSTEM")
            print("=" * 60)
            return
            
        header_text = Text("Cerebras Documentation RAG System", style="bold blue")
        subtitle = Text("Intelligent documentation assistant with citations", style="italic")
        
        panel = Panel.fit(
            f"{header_text}\n{subtitle}",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        
    def display_status(self):
        """Display current system status and configuration."""
        if not RICH_AVAILABLE:
            print(f"Citations: {'ON' if self.citations_enabled else 'OFF'}")
            print(f"Reranking: {'ON' if self.reranking_enabled else 'OFF'}")
            return
            
        table = Table(title="System Status", show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Status", style="green" if self.citations_enabled else "red")
        
        table.add_row("Citations", "✅ ON" if self.citations_enabled else "❌ OFF")
        table.add_row("Reranking", "✅ ON" if self.reranking_enabled else "❌ OFF")
        table.add_row("Conversation", f"💬 {len(self.conversation_history)} messages")
        
        self.console.print(table)
        
    def display_help(self):
        """Display available commands and usage instructions."""
        if not RICH_AVAILABLE:
            print("\nAvailable Commands:")
            print("help - Show this help message")
            print("citations on/off - Toggle citation mode")
            print("reranking on/off - Toggle document reranking")
            print("status - Show system status")
            print("history - Display conversation history")
            print("quit/exit - Exit application")
            return
            
        help_text = """
## Available Commands

- `help` - Show this help message
- `citations on/off` - Toggle citation mode
- `reranking on/off` - Toggle document reranking  
- `status` - Show system status
- `history` - Display conversation history
- `quit` or `exit` - Exit application

## Tips

- Citations provide source references for answers
- Reranking improves relevance but uses additional API calls
- Type your questions naturally - the system understands context
- Use conversation history to reference previous interactions
        """
        
        self.console.print(Panel(Markdown(help_text), title="Help", border_style="green"))
        
    def display_conversation_history(self):
        """Display the conversation history."""
        if not self.conversation_history:
            if RICH_AVAILABLE:
                self.console.print("[yellow]No conversation history yet.[/yellow]")
            else:
                print("No conversation history yet.")
            return
            
        if not RICH_AVAILABLE:
            print("\nConversation History:")
            for i, entry in enumerate(self.conversation_history, 1):
                print(f"{i}. Q: {entry['question'][:100]}...")
                print(f"   A: {entry['answer'][:100]}...")
            return
            
        self.console.print(Rule("Conversation History"))
        
        for i, entry in enumerate(self.conversation_history, 1):
            # Question
            self.console.print(f"[bold cyan]Q{i}:[/bold cyan] {entry['question']}")
            
            # Answer (truncated)
            answer_preview = entry['answer'][:200] + "..." if len(entry['answer']) > 200 else entry['answer']
            self.console.print(f"[bold green]A{i}:[/bold green] {answer_preview}")
            
            # Citations count
            citation_count = len(entry.get('citations', []))
            if citation_count > 0:
                self.console.print(f"[dim]📚 {citation_count} citation(s)[/dim]")
                
            self.console.print()
    
    def handle_command(self, user_input: str) -> bool:
        """
        Handle special commands.
        
        Args:
            user_input: User's input string
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit']:
            self.running = False
            if RICH_AVAILABLE:
                self.console.print("[yellow]Goodbye! 👋[/yellow]")
            else:
                print("Goodbye!")
            return True
            
        elif command == 'help':
            self.display_help()
            return True
            
        elif command == 'status':
            self.display_status()
            return True
            
        elif command == 'history':
            self.display_conversation_history()
            return True
            
        elif command in ['citations on', 'citations off']:
            self.citations_enabled = command.endswith('on')
            status = "enabled" if self.citations_enabled else "disabled"
            if RICH_AVAILABLE:
                self.console.print(f"[green]Citations {status}[/green]")
            else:
                print(f"Citations {status}")
            return True
            
        elif command in ['reranking on', 'reranking off']:
            self.reranking_enabled = command.endswith('on')
            status = "enabled" if self.reranking_enabled else "disabled"
            if RICH_AVAILABLE:
                self.console.print(f"[green]Reranking {status}[/green]")
            else:
                print(f"Reranking {status}")
            return True
            
        return False
    
    def stream_response(self, question: str):
        """
        Stream and display the response for a question.
        
        Args:
            question: User's question
        """
        try:
            response_chunks = []
            current_answer = ""
            citations = []
            
            # Stream the response
            for chunk in self.agent.stream_response_with_citations(
                question, 
                use_citations=self.citations_enabled,
                use_reranking=self.reranking_enabled,
                config=self.session_config
            ):
                if chunk["type"] == "status":
                    if RICH_AVAILABLE:
                        self.console.print(f"[dim]{chunk['message']}[/dim]")
                    else:
                        print(chunk['message'])
                        
                elif chunk["type"] == "answer":
                    current_answer = chunk["content"]
                    if RICH_AVAILABLE:
                        self.console.print(f"\n[bold green]🤖 Assistant:[/bold green]")
                        self.console.print(current_answer)
                    else:
                        print(f"\n🤖 Assistant: {current_answer}")
                        
                elif chunk["type"] == "citations_header":
                    if RICH_AVAILABLE:
                        self.console.print(f"\n[bold blue]📚 Sources:[/bold blue]")
                    else:
                        print(f"\n📚 Sources:")
                        
                elif chunk["type"] == "citation":
                    citation = {
                        'source_id': chunk['source_id'],
                        'quote': chunk['quote'],
                        'title': chunk['title'],
                        'url': chunk['url']
                    }
                    citations.append(citation)
                    
                    if RICH_AVAILABLE:
                        self.console.print(f"[cyan]Source {chunk['source_id']}:[/cyan] {chunk['title']}")
                        self.console.print(f"[dim]Quote:[/dim] \"{chunk['quote'][:150]}...\"")
                        self.console.print(f"[dim]URL:[/dim] {chunk['url']}")
                        self.console.print()
                    else:
                        print(f"Source {chunk['source_id']}: {chunk['title']}")
                        print(f"Quote: \"{chunk['quote'][:150]}...\"")
                        print(f"URL: {chunk['url']}")
                        print()
                        
                elif chunk["type"] == "error":
                    if RICH_AVAILABLE:
                        self.console.print(f"[red]❌ {chunk['message']}[/red]")
                    else:
                        print(f"❌ {chunk['message']}")
                    return
                    
                elif chunk["type"] == "warning":
                    if RICH_AVAILABLE:
                        self.console.print(f"[yellow]⚠️ {chunk['message']}[/yellow]")
                    else:
                        print(f"⚠️ {chunk['message']}")
            
            # Save to conversation history
            if current_answer:
                self.conversation_history.append({
                    'question': question,
                    'answer': current_answer,
                    'citations': citations
                })
                
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(f"[red]Error: {str(e)}[/red]")
            else:
                print(f"Error: {str(e)}")
    
    def initialize_system(self):
        """Initialize the RAG system components."""
        if RICH_AVAILABLE:
            self.console.print("[yellow]🔧 Initializing system...[/yellow]")
        else:
            print("🔧 Initializing system...")
        
        # Check prerequisites
        prereq_ok, missing_keys = self.agent.check_prerequisites()
        if not prereq_ok:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Missing API keys: {', '.join(missing_keys)}[/red]")
                self.console.print("[yellow]Please set the required environment variables in your .env file[/yellow]")
            else:
                print(f"❌ Missing API keys: {', '.join(missing_keys)}")
                print("Please set the required environment variables in your .env file")
            return False
        
        # Initialize vector store
        vs_ok, vs_msg = self.agent.initialize_vector_store()
        if not vs_ok:
            if RICH_AVAILABLE:
                self.console.print(f"[red]❌ Vector store error: {vs_msg}[/red]")
            else:
                print(f"❌ Vector store error: {vs_msg}")
            return False
        
        # Initialize conversation graph
        self.agent.initialize_graph()
        
        if RICH_AVAILABLE:
            self.console.print(f"[green]✅ System initialized: {vs_msg}[/green]")
        else:
            print(f"✅ System initialized: {vs_msg}")
        return True
    
    def run(self):
        """Run the interactive CLI."""
        self.display_header()
        
        if not self.initialize_system():
            return
        
        if RICH_AVAILABLE:
            self.console.print("\n[dim]Type 'help' for commands, or ask a question about Cerebras documentation.[/dim]")
            self.console.print("[dim]Use 'quit' or 'exit' to end the session.[/dim]\n")
        else:
            print("\nType 'help' for commands, or ask a question about Cerebras documentation.")
            print("Use 'quit' or 'exit' to end the session.\n")
        
        while self.running:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("[bold blue]You[/bold blue]")
                else:
                    user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_command(user_input):
                    continue
                
                # Process question
                self.stream_response(user_input)
                
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    self.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                else:
                    print("\nGoodbye!")
                break
            except EOFError:
                break


def main():
    """Main entry point for the CLI."""
    cli = CerebrasRAGCLI()
    cli.run()


if __name__ == "__main__":
    main() 