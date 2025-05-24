#!/usr/bin/env python3
"""
Entry point script for running the Cerebras RAG CLI interface.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.cerebras_rag.interfaces.cli import main

if __name__ == "__main__":
    main() 