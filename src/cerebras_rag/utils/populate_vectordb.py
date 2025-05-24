"""
Vector database population utility for the Cerebras RAG system.

This module handles:
- Crawling Cerebras inference documentation
- Creating embeddings using Cohere
- Storing documents in Pinecone vector database
- Building a searchable knowledge base
"""

import os
import sys
from typing import List, Dict, Any
import time
from urllib.parse import urljoin, urlparse
import re

from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = "cerebras-docs"
EMBEDDING_DIMENSION = 1024  # Cohere embed-english-v3.0 dimensions


class CerebrasDocumentationCrawler:
    """
    Crawler for Cerebras documentation with smart content extraction.
    
    This class handles crawling the Cerebras inference documentation,
    extracting structured content, and preparing it for vector storage.
    """
    
    def __init__(self):
        """Initialize the crawler with required services."""
        self.firecrawl = None
        self.embeddings = None
        self.pinecone_client = None
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize external services (Firecrawl, Cohere, Pinecone)."""
        # Initialize Firecrawl
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        if firecrawl_key:
            self.firecrawl = FirecrawlApp(api_key=firecrawl_key)
        else:
            print("Warning: FIRECRAWL_API_KEY not found. Using alternative crawling method.")
        
        # Initialize Cohere embeddings
        cohere_key = os.getenv("COHERE_API_KEY")
        if not cohere_key:
            raise ValueError("COHERE_API_KEY is required for embeddings")
        
        self.embeddings = CohereEmbeddings(
            model="embed-english-v3.0",
            cohere_api_key=cohere_key
        )
        
        # Initialize Pinecone
        pinecone_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_key:
            raise ValueError("PINECONE_API_KEY is required for vector storage")
        
        self.pinecone_client = Pinecone(api_key=pinecone_key)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove navigation elements and common patterns
        text = re.sub(r'Skip to main content', '', text)
        text = re.sub(r'Table of contents?', '', text, flags=re.IGNORECASE)
        
        # Clean up code blocks and formatting
        text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).strip(), text)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'-{3,}', '---', text)
        
        return text.strip()
    
    def extract_page_metadata(self, url: str, content: str) -> Dict[str, Any]:
        """
        Extract metadata from a documentation page.
        
        Args:
            url: Page URL
            content: Page content
            
        Returns:
            dict: Extracted metadata
        """
        metadata = {
            'source': url,
            'url': url
        }
        
        # Extract title from content
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        else:
            # Fallback to URL-based title
            path = urlparse(url).path
            title = path.strip('/').split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            metadata['title'] = title or "Cerebras Documentation"
        
        # Extract section information
        if '/api/' in url:
            metadata['section'] = 'API Reference'
        elif '/guide/' in url or '/tutorial/' in url:
            metadata['section'] = 'Guides'
        elif '/example/' in url:
            metadata['section'] = 'Examples'
        else:
            metadata['section'] = 'Documentation'
        
        # Estimate content type
        if 'curl' in content.lower() or 'api' in content.lower():
            metadata['content_type'] = 'api'
        elif 'example' in content.lower() or 'tutorial' in content.lower():
            metadata['content_type'] = 'tutorial'
        else:
            metadata['content_type'] = 'documentation'
        
        return metadata
    
    def crawl_with_firecrawl(self, base_url: str) -> List[Document]:
        """
        Crawl documentation using Firecrawl service.
        
        Args:
            base_url: Base URL to crawl
            
        Returns:
            List[Document]: Crawled documents
        """
        if not self.firecrawl:
            return []
        
        print(f"🔄 Starting crawl of {base_url} with Firecrawl...")
        
        try:
            # Configure crawl parameters
            crawl_params = {
                'limit': 50,  # Limit to prevent overwhelming
                'scrapeOptions': {
                    'formats': ['markdown'],
                    'onlyMainContent': True,
                    'waitFor': 2000
                }
            }
            
            # Start crawl
            crawl_result = self.firecrawl.crawl_url(base_url, crawl_params)
            
            if not crawl_result.get('success'):
                print(f"❌ Crawl failed: {crawl_result.get('error', 'Unknown error')}")
                return []
            
            documents = []
            crawl_data = crawl_result.get('data', [])
            
            print(f"📄 Processing {len(crawl_data)} crawled pages...")
            
            for i, page_data in enumerate(crawl_data):
                url = page_data.get('url', '')
                content = page_data.get('markdown', '')
                
                if not content or len(content.strip()) < 100:
                    continue
                
                # Clean content
                cleaned_content = self.clean_text(content)
                
                # Extract metadata
                metadata = self.extract_page_metadata(url, cleaned_content)
                
                # Create document
                doc = Document(
                    page_content=cleaned_content,
                    metadata=metadata
                )
                
                documents.append(doc)
                print(f"✅ Processed: {metadata.get('title', 'Unknown')} ({len(cleaned_content)} chars)")
            
            print(f"🎉 Successfully crawled {len(documents)} documents")
            return documents
            
        except Exception as e:
            print(f"❌ Firecrawl error: {str(e)}")
            return []
    
    def crawl_fallback(self, urls: List[str]) -> List[Document]:
        """
        Fallback crawling method using requests/BeautifulSoup.
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List[Document]: Crawled documents
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("❌ Fallback crawling requires 'requests' and 'beautifulsoup4'")
            return []
        
        print(f"🔄 Using fallback crawling for {len(urls)} URLs...")
        
        documents = []
        
        for url in urls:
            try:
                print(f"📄 Crawling: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove navigation and footer elements
                for element in soup.find_all(['nav', 'footer', 'aside']):
                    element.decompose()
                
                # Extract main content
                main_content = soup.find('main') or soup.find('article') or soup.body
                
                if main_content:
                    text = main_content.get_text(separator='\n', strip=True)
                    cleaned_text = self.clean_text(text)
                    
                    if len(cleaned_text) > 100:  # Only include substantial content
                        metadata = self.extract_page_metadata(url, cleaned_text)
                        
                        doc = Document(
                            page_content=cleaned_text,
                            metadata=metadata
                        )
                        
                        documents.append(doc)
                        print(f"✅ Processed: {metadata.get('title', 'Unknown')}")
                
                # Add delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Failed to crawl {url}: {str(e)}")
                continue
        
        print(f"🎉 Fallback crawling completed: {len(documents)} documents")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List[Document]: Chunked documents
        """
        print(f"✂️ Chunking {len(documents)} documents...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunked_docs = []
        
        for doc in documents:
            chunks = text_splitter.split_documents([doc])
            
            # Add chunk index to metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
                chunked_docs.append(chunk)
        
        print(f"📚 Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
    
    def setup_pinecone_index(self):
        """Set up the Pinecone index for storing embeddings."""
        print(f"🔧 Setting up Pinecone index: {INDEX_NAME}")
        
        # Check if index exists
        existing_indexes = self.pinecone_client.list_indexes()
        index_names = [idx['name'] for idx in existing_indexes]
        
        if INDEX_NAME in index_names:
            print(f"📋 Index '{INDEX_NAME}' already exists")
            return self.pinecone_client.Index(INDEX_NAME)
        
        # Create new index
        print(f"🆕 Creating new index: {INDEX_NAME}")
        
        self.pinecone_client.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        
        # Wait for index to be ready
        while not self.pinecone_client.describe_index(INDEX_NAME).status['ready']:
            print("⏳ Waiting for index to be ready...")
            time.sleep(5)
        
        print(f"✅ Index '{INDEX_NAME}' created successfully")
        return self.pinecone_client.Index(INDEX_NAME)
    
    def populate_index(self, documents: List[Document]):
        """
        Populate the Pinecone index with document embeddings.
        
        Args:
            documents: List of documents to embed and store
        """
        if not documents:
            print("❌ No documents to populate")
            return
        
        print(f"🚀 Populating index with {len(documents)} documents...")
        
        # Set up index
        index = self.setup_pinecone_index()
        
        # Process documents in batches
        batch_size = 10
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"🔄 Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            try:
                # Create embeddings for batch
                texts = [doc.page_content for doc in batch]
                embeddings = self.embeddings.embed_documents(texts)
                
                # Prepare vectors for upsert
                vectors = []
                for j, (doc, embedding) in enumerate(zip(batch, embeddings)):
                    vector_id = f"doc_{i + j}"
                    
                    # Prepare metadata (Pinecone has size limits)
                    metadata = {
                        'text': doc.page_content[:1000],  # Limit text size
                        'title': doc.metadata.get('title', '')[:100],
                        'source': doc.metadata.get('source', '')[:200],
                        'section': doc.metadata.get('section', ''),
                        'content_type': doc.metadata.get('content_type', ''),
                        'chunk_index': doc.metadata.get('chunk_index', 0)
                    }
                    
                    vectors.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': metadata
                    })
                
                # Upsert to Pinecone
                index.upsert(vectors=vectors)
                print(f"✅ Uploaded batch {i//batch_size + 1}")
                
                # Add delay to respect rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing batch {i//batch_size + 1}: {str(e)}")
                continue
        
        # Verify upload
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)
        print(f"🎉 Successfully populated index with {vector_count:,} vectors")


def main():
    """Main function to populate the vector database."""
    print("🚀 Starting Cerebras Documentation Vector Database Population")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ['COHERE_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return
    
    try:
        # Initialize crawler
        crawler = CerebrasDocumentationCrawler()
        
        # URLs to crawl (customize as needed)
        base_urls = [
            "https://inference-docs.cerebras.ai/",
        ]
        
        # Alternative URLs if the main site structure changes
        fallback_urls = [
            "https://inference-docs.cerebras.ai/introduction",
            "https://inference-docs.cerebras.ai/quickstart",
            "https://inference-docs.cerebras.ai/api-reference",
            "https://inference-docs.cerebras.ai/guides",
        ]
        
        all_documents = []
        
        # Try Firecrawl first
        for base_url in base_urls:
            docs = crawler.crawl_with_firecrawl(base_url)
            all_documents.extend(docs)
        
        # If Firecrawl didn't work or got few results, try fallback
        if len(all_documents) < 5:
            print("🔄 Using fallback crawling method...")
            fallback_docs = crawler.crawl_fallback(fallback_urls)
            all_documents.extend(fallback_docs)
        
        if not all_documents:
            print("❌ No documents were successfully crawled")
            return
        
        # Chunk documents
        chunked_documents = crawler.chunk_documents(all_documents)
        
        # Populate vector database
        crawler.populate_index(chunked_documents)
        
        print("\n🎉 Vector database population completed successfully!")
        print(f"📊 Total documents processed: {len(all_documents)}")
        print(f"📊 Total chunks created: {len(chunked_documents)}")
        
    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        raise


if __name__ == "__main__":
    main() 