# Troubleshooting Guide

This guide helps resolve common issues encountered when using the Cerebras Documentation RAG System.

## Quick Diagnostics

Run this script to quickly identify common issues:

```python
#!/usr/bin/env python3
"""
Quick diagnostic script for Cerebras RAG system
"""
import os
from dotenv import load_dotenv

def run_diagnostics():
    print("🔍 Cerebras RAG System Diagnostics")
    print("=" * 40)
    
    # Check environment file
    if os.path.exists('.env'):
        print("✅ .env file found")
        load_dotenv()
    else:
        print("❌ .env file not found")
        return
    
    # Check API keys
    api_keys = {
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY'),
        'COHERE_API_KEY': os.getenv('COHERE_API_KEY')
    }
    
    for key, value in api_keys.items():
        if value:
            print(f"✅ {key} is set")
        else:
            print(f"❌ {key} is missing")
    
    # Test imports
    try:
        from cerebras_rag import get_agent
        print("✅ Package imports work")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test agent initialization
    try:
        agent = get_agent()
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return
    
    # Test prerequisites
    try:
        prereq_ok, missing = agent.check_prerequisites()
        if prereq_ok:
            print("✅ All prerequisites met")
        else:
            print(f"❌ Missing prerequisites: {missing}")
    except Exception as e:
        print(f"❌ Prerequisites check failed: {e}")
    
    # Test vector store
    try:
        vs_ok, msg = agent.initialize_vector_store()
        if vs_ok:
            print(f"✅ Vector store: {msg}")
        else:
            print(f"❌ Vector store error: {msg}")
    except Exception as e:
        print(f"❌ Vector store connection failed: {e}")

if __name__ == "__main__":
    run_diagnostics()
```

## Common Issues

### 1. Installation Problems

#### "Package not found" or Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'cerebras_rag'
ImportError: cannot import name 'get_agent'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   # Check if package is installed
   pip list | grep cerebras-rag
   
   # Reinstall in development mode
   pip install -e .
   ```

2. **Check Python path:**
   ```python
   import sys
   print(sys.path)
   # Ensure your project directory is in the path
   ```

3. **Virtual environment issues:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   
   # Verify you're in the right environment
   which python
   ```

4. **Dependency conflicts:**
   ```bash
   # Create fresh environment
   python -m venv fresh_env
   source fresh_env/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

#### Requirements Installation Failures

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
Building wheel for package failed
```

**Solutions:**

1. **Update pip and setuptools:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Use specific Python version:**
   ```bash
   # Ensure Python 3.8+
   python --version
   
   # Use specific Python version
   python3.11 -m venv .venv
   ```

3. **Install with no cache:**
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Platform-specific issues:**
   ```bash
   # For M1 Macs
   export ARCHFLAGS="-arch arm64"
   pip install -r requirements.txt
   
   # For Windows with long paths
   git config --system core.longpaths true
   ```

### 2. API Key Issues

#### Missing or Invalid API Keys

**Symptoms:**
```
❌ Missing API keys: ['OPENROUTER_API_KEY', 'PINECONE_API_KEY']
401 Unauthorized
Invalid API key provided
```

**Solutions:**

1. **Check .env file:**
   ```bash
   # Verify .env exists and has correct format
   cat .env
   
   # Should look like:
   # OPENROUTER_API_KEY=sk-or-v1-xxxxx
   # PINECONE_API_KEY=your-pinecone-key
   # COHERE_API_KEY=your-cohere-key
   ```

2. **Verify environment loading:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   print("OPENROUTER_API_KEY:", bool(os.getenv('OPENROUTER_API_KEY')))
   ```

3. **Test API keys individually:**
   ```python
   # Test OpenRouter
   import requests
   headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
   response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
   print("OpenRouter status:", response.status_code)
   
   # Test Pinecone
   from pinecone import Pinecone
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
   print("Pinecone indexes:", pc.list_indexes())
   ```

4. **API key format issues:**
   ```bash
   # Remove quotes, spaces, or newlines
   # Correct: OPENROUTER_API_KEY=sk-or-v1-xxxxx
   # Wrong: OPENROUTER_API_KEY="sk-or-v1-xxxxx"
   # Wrong: OPENROUTER_API_KEY=sk-or-v1-xxxxx 
   ```

### 3. Vector Database Issues

#### "Index not found" Error

**Symptoms:**
```
❌ Pinecone index 'cerebras-docs' not found! Please run populate_vectordb.py first.
```

**Solutions:**

1. **Run population script:**
   ```bash
   python -m src.cerebras_rag.utils.populate_vectordb
   ```

2. **Check index exists:**
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
   print("Available indexes:", [idx.name for idx in pc.list_indexes()])
   ```

3. **Force recreate index:**
   ```bash
   python -m src.cerebras_rag.utils.populate_vectordb --force-recreate
   ```

#### "Index is empty" Error

**Symptoms:**
```
❌ Pinecone index 'cerebras-docs' is empty! Please run populate_vectordb.py first.
```

**Solutions:**

1. **Check index stats:**
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
   index = pc.Index('cerebras-docs')
   stats = index.describe_index_stats()
   print("Vector count:", stats.get('total_vector_count', 0))
   ```

2. **Repopulate with verbose output:**
   ```bash
   python -m src.cerebras_rag.utils.populate_vectordb --verbose
   ```

3. **Check document directory:**
   ```bash
   # Ensure documents exist in expected location
   ls -la cerebras_docs/  # or your docs directory
   ```

### 4. Network and API Issues

#### Connection Timeouts

**Symptoms:**
```
ReadTimeoutError: HTTPSConnectionPool
requests.exceptions.ConnectionError
```

**Solutions:**

1. **Check internet connectivity:**
   ```bash
   # Test basic connectivity
   ping openrouter.ai
   ping api.pinecone.io
   ```

2. **Configure timeouts:**
   ```python
   # Increase timeout in your code
   agent.llm.request_timeout = 60  # seconds
   ```

3. **Proxy configuration:**
   ```bash
   # If behind corporate proxy
   export HTTPS_PROXY=http://proxy.company.com:8080
   export HTTP_PROXY=http://proxy.company.com:8080
   ```

#### Rate Limiting

**Symptoms:**
```
429 Too Many Requests
Rate limit exceeded
```

**Solutions:**

1. **Implement backoff:**
   ```python
   import time
   import random
   
   def retry_with_backoff(func, max_retries=3):
       for i in range(max_retries):
           try:
               return func()
           except Exception as e:
               if "429" in str(e) and i < max_retries - 1:
                   time.sleep(2 ** i + random.uniform(0, 1))
                   continue
               raise
   ```

2. **Reduce request frequency:**
   ```python
   # Disable reranking to reduce API calls
   response = agent.ask_question(question, use_reranking=False)
   ```

### 5. Performance Issues

#### Slow Response Times

**Symptoms:**
- Responses take > 30 seconds
- CLI appears to hang
- Timeouts in applications

**Solutions:**

1. **Enable streaming:**
   ```python
   # Use streaming for better perceived performance
   for chunk in agent.stream_response_with_citations(question):
       if chunk["type"] == "answer":
           print(chunk["content"], end="", flush=True)
   ```

2. **Optimize retrieval:**
   ```python
   # Reduce document count
   docs = agent.retrieve_with_citations(question, k=3)  # instead of 6
   
   # Disable reranking
   response = agent.ask_question(question, use_reranking=False)
   ```

3. **Check system resources:**
   ```bash
   # Monitor system usage
   top
   free -h
   df -h
   ```

#### Memory Issues

**Symptoms:**
```
MemoryError
Process killed
Out of memory
```

**Solutions:**

1. **Reduce batch sizes:**
   ```python
   # In populate_vectordb.py, reduce batch size
   BATCH_SIZE = 10  # instead of 100
   ```

2. **Monitor memory usage:**
   ```python
   import psutil
   print(f"Memory usage: {psutil.virtual_memory().percent}%")
   ```

3. **Use garbage collection:**
   ```python
   import gc
   
   # Force garbage collection after large operations
   gc.collect()
   ```

### 6. CLI-Specific Issues

#### Rich Terminal Formatting Issues

**Symptoms:**
- Garbled output in terminal
- Missing colors or formatting
- CLI crashes on startup

**Solutions:**

1. **Install Rich:**
   ```bash
   pip install rich
   ```

2. **Fallback mode:**
   ```python
   # The CLI automatically falls back to basic text if Rich is unavailable
   # Check the warning message at startup
   ```

3. **Terminal compatibility:**
   ```bash
   # Use compatible terminal
   export TERM=xterm-256color
   
   # Or force basic output
   python -m src.cerebras_rag.interfaces.cli --no-rich
   ```

#### CLI Hangs or Freezes

**Solutions:**

1. **Check for input waiting:**
   - Press Ctrl+C to interrupt
   - Check if CLI is waiting for input

2. **Restart with verbose mode:**
   ```bash
   python -m src.cerebras_rag.interfaces.cli --verbose
   ```

3. **Clear terminal state:**
   ```bash
   reset
   clear
   ```

### 7. Configuration Issues

#### Wrong Model or Provider

**Symptoms:**
```
Model not found
Provider not available
Unexpected response format
```

**Solutions:**

1. **Verify model name:**
   ```python
   # Check available models
   import requests
   headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
   response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
   models = [model["id"] for model in response.json()["data"]]
   print("Available models:", models)
   ```

2. **Check provider configuration:**
   ```python
   # Ensure Cerebras provider is specified
   llm = ChatOpenAI(
       model="qwen/qwen3-32b",
       extra_body={"provider": {"only": ["cerebras"]}}
   )
   ```

## Debugging Techniques

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Specific logger for LangChain
logging.getLogger("langchain").setLevel(logging.DEBUG)
```

### Step-by-Step Testing

```python
# Test each component individually
from cerebras_rag import get_agent

agent = get_agent()

# 1. Test prerequisites
print("1. Prerequisites:", agent.check_prerequisites())

# 2. Test vector store
print("2. Vector store:", agent.initialize_vector_store())

# 3. Test LLM connection
try:
    response = agent.llm.invoke("Hello")
    print("3. LLM test: OK")
except Exception as e:
    print(f"3. LLM test failed: {e}")

# 4. Test retrieval
try:
    docs = agent.retrieve_with_citations("test", k=1)
    print(f"4. Retrieval test: {len(docs)} docs")
except Exception as e:
    print(f"4. Retrieval test failed: {e}")
```

### Network Debugging

```python
import requests

def test_api_endpoints():
    """Test API endpoint connectivity"""
    endpoints = {
        "OpenRouter": "https://openrouter.ai/api/v1/models",
        "Cohere": "https://api.cohere.ai/v1/models",
        "Pinecone": "https://api.pinecone.io"
    }
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=10)
            print(f"{name}: {response.status_code}")
        except Exception as e:
            print(f"{name}: Failed - {e}")
```

## Getting Help

### Collect System Information

Before seeking help, collect this information:

```python
import sys
import platform
import pkg_resources

def collect_system_info():
    """Collect system information for debugging"""
    info = {
        "Python version": sys.version,
        "Platform": platform.platform(),
        "Architecture": platform.architecture(),
        "Package versions": {}
    }
    
    packages = ['langchain', 'pinecone', 'cohere', 'openai', 'rich']
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            info["Package versions"][package] = version
        except:
            info["Package versions"][package] = "Not installed"
    
    return info

print(collect_system_info())
```

### Create Minimal Reproduction

```python
"""
Minimal example to reproduce the issue
"""
from cerebras_rag import get_agent

try:
    agent = get_agent()
    prereq_ok, missing = agent.check_prerequisites()
    
    if not prereq_ok:
        print(f"Prerequisites failed: {missing}")
        exit(1)
    
    vs_ok, msg = agent.initialize_vector_store()
    if not vs_ok:
        print(f"Vector store failed: {msg}")
        exit(1)
    
    agent.initialize_graph()
    
    # The specific operation that fails
    response = agent.ask_question("test question")
    print("Success:", response.answer[:100])
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
```

### Where to Get Help

1. **GitHub Issues**: Report bugs and feature requests
2. **Documentation**: Check the full documentation
3. **Examples**: Review working examples
4. **Community**: Join discussions and ask questions

This troubleshooting guide should help resolve most common issues. If you encounter problems not covered here, please create a GitHub issue with your system information and a minimal reproduction example. 