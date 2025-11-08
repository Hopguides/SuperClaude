# Gemini File Search Integration Guide

**SuperClaude Advanced RAG Implementation**
**Version:** 2.0.1
**Last Updated:** November 2025

---

## Table of Contents

1. [Overview](#overview)
2. [What is File Search?](#what-is-file-search)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Advanced Usage](#advanced-usage)
7. [File Search Stores](#file-search-stores)
8. [Chunking Strategies](#chunking-strategies)
9. [Metadata & Filtering](#metadata--filtering)
10. [Citations & Verification](#citations--verification)
11. [Integration with SuperClaude](#integration-with-superclaude)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)
14. [Pricing & Limits](#pricing--limits)

---

## Overview

Gemini File Search enables **Retrieval Augmented Generation (RAG)** through semantic search capabilities. It allows you to:

- Upload and index documents for semantic search
- Ask questions about your documents
- Get AI-generated answers with citations
- Filter documents by custom metadata
- Manage multiple document collections

**Use Cases:**
- Documentation search and Q&A
- Codebase exploration and analysis
- Research paper analysis
- Knowledge base creation
- Technical documentation retrieval

---

## What is File Search?

File Search uses **semantic search** to find information relevant to user prompts. Unlike keyword-based search, it understands the **meaning and context** of queries.

### How It Works

1. **Create File Search Store** - Container for document embeddings
2. **Upload & Import Files** - Files are chunked, embedded, and indexed
3. **Query with File Search** - Semantic search finds relevant information
4. **Model Response** - Gemini uses retrieved context to generate accurate answers

```
Documents → Chunking → Embeddings → File Search Store
                                             ↓
User Query → Query Embedding → Semantic Search → Retrieved Chunks
                                                        ↓
                                        Gemini Model → Response with Citations
```

### Key Features

- **Semantic Understanding** - Meaning-based search, not just keywords
- **Automatic Chunking** - Documents split into optimal chunks
- **Persistent Storage** - File search stores kept indefinitely
- **Citation Support** - Know which documents were used
- **Metadata Filtering** - Search specific document subsets
- **Multiple File Types** - PDF, DOCX, TXT, MD, JSON, code files, and more

---

## Prerequisites

### System Requirements

```bash
# Python 3.8 or higher
python3 --version

# Google Generative AI SDK
pip install google-generativeai

# or using the newer google-genai package
pip install google-genai
```

### API Key Setup

1. Get your Gemini API key at: https://makersuite.google.com/app/apikey
2. Add to your `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Supported Models

- `gemini-2.5-pro`
- `gemini-2.5-flash` (recommended for speed)

---

## Installation

### Install Python SDK

```bash
# Install the Google Generative AI SDK
pip install google-genai

# Or install both SDKs for compatibility
pip install google-generativeai google-genai
```

### Verify Installation

```python
from google import genai

# Initialize client
client = genai.Client(api_key='YOUR_API_KEY')

# Test connection
print("Gemini File Search ready!")
```

---

## Quick Start

### Method 1: Direct Upload to File Search Store

This is the **fastest method** - uploads and indexes in one step:

```python
from google import genai
from google.genai import types
import time
import os

# Initialize client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# 1. Create file search store
file_search_store = client.file_search_stores.create(
    config={'display_name': 'my-documentation-store'}
)

# 2. Upload and import file in one step
operation = client.file_search_stores.upload_to_file_search_store(
    file='sample.txt',
    file_search_store_name=file_search_store.name,
    config={
        'display_name': 'sample-document',
    }
)

# 3. Wait for import to complete
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print(f"✅ File imported to {file_search_store.name}")

# 4. Query the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is this document about?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

### Method 2: Upload Then Import

Use this when you need more control over file management:

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# 1. Upload file to Files API (stored for 48 hours)
sample_file = client.files.upload(
    file='sample.txt',
    config={'name': 'sample-document'}
)

# 2. Create file search store
file_search_store = client.file_search_stores.create(
    config={'display_name': 'my-documentation-store'}
)

# 3. Import file into file search store
operation = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name
)

# 4. Wait for import
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print(f"✅ File imported to {file_search_store.name}")

# 5. Query the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Summarize this document",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

---

## Advanced Usage

### Batch Upload Multiple Files

```python
import os
from pathlib import Path

# Directory containing documents
docs_dir = Path("./documents")

# Create file search store
store = client.file_search_stores.create(
    config={'display_name': 'project-documentation'}
)

# Upload all files
for file_path in docs_dir.glob("**/*.{txt,md,pdf,docx}"):
    print(f"Uploading {file_path.name}...")

    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(file_path),
        file_search_store_name=store.name,
        config={'display_name': file_path.name}
    )

    # Wait for completion
    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    print(f"✅ {file_path.name} imported")

print(f"\n✅ All files imported to {store.name}")
```

### Query with Context

```python
# Multi-turn conversation with file search
conversation = []

# First query
query1 = "What are the main features of this system?"
conversation.append({"role": "user", "parts": [query1]})

response1 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=conversation,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

conversation.append({"role": "model", "parts": [response1.text]})
print(f"Response 1: {response1.text}\n")

# Follow-up query
query2 = "Can you provide code examples for these features?"
conversation.append({"role": "user", "parts": [query2]})

response2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=conversation,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(f"Response 2: {response2.text}")
```

---

## File Search Stores

### Create File Search Store

```python
# Create with display name
store = client.file_search_stores.create(
    config={'display_name': 'my-knowledge-base'}
)

print(f"Created store: {store.name}")
print(f"Display name: {store.display_name}")
```

### List All Stores

```python
# List all file search stores
for store in client.file_search_stores.list():
    print(f"Name: {store.name}")
    print(f"Display Name: {store.display_name}")
    print(f"Created: {store.create_time}")
    print("---")
```

### Get Specific Store

```python
# Get by name
store = client.file_search_stores.get(
    name='fileSearchStores/my-store-id'
)

print(f"Store: {store.display_name}")
```

### Delete File Search Store

```python
# Delete store (use force=True to delete non-empty stores)
client.file_search_stores.delete(
    name='fileSearchStores/my-store-id',
    config={'force': True}
)

print("✅ Store deleted")
```

### List Documents in Store

```python
# List all documents in a file search store
documents = client.file_search_stores.list_documents(
    file_search_store_name=store.name
)

for doc in documents:
    print(f"Document: {doc.display_name}")
    print(f"Size: {doc.size_bytes} bytes")
    print(f"Created: {doc.create_time}")
    print("---")
```

---

## Chunking Strategies

### Default Chunking

By default, files are automatically chunked with optimal settings. You can customize this:

```python
# Custom chunking configuration
operation = client.file_search_stores.upload_to_file_search_store(
    file='large_document.pdf',
    file_search_store_name=store.name,
    config={
        'display_name': 'large-doc',
        'chunking_config': {
            'white_space_config': {
                'max_tokens_per_chunk': 200,    # Maximum tokens per chunk
                'max_overlap_tokens': 20         # Overlap between chunks
            }
        }
    }
)
```

### Chunking Best Practices

**Small Chunks (100-200 tokens):**
- Better for precise information retrieval
- Good for Q&A systems
- Higher embedding costs

**Medium Chunks (300-500 tokens):**
- Balanced approach (recommended)
- Good for most use cases
- Maintains context while staying precise

**Large Chunks (500-1000 tokens):**
- Better for context-heavy queries
- Good for summarization
- Lower embedding costs

**Overlap:**
- 10-20% overlap recommended
- Prevents information loss at chunk boundaries
- Improves retrieval quality

---

## Metadata & Filtering

### Add Metadata to Files

```python
# Upload with custom metadata
operation = client.file_search_stores.import_file(
    file_search_store_name=store.name,
    file_name=sample_file.name,
    custom_metadata=[
        {"key": "author", "string_value": "John Doe"},
        {"key": "year", "numeric_value": 2024},
        {"key": "category", "string_value": "technical"},
        {"key": "version", "string_value": "1.0.0"}
    ]
)
```

### Filter by Metadata

```python
# Query only specific documents
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are the main features?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.name],
                    metadata_filter='author="John Doe" AND year=2024'
                )
            )
        ]
    )
)
```

### Metadata Filter Syntax

Based on [google.aip.dev/160](https://google.aip.dev/160):

```python
# String equality
metadata_filter='author="John Doe"'

# Numeric comparison
metadata_filter='year>=2020'
metadata_filter='year>2020 AND year<2025'

# Multiple conditions
metadata_filter='category="technical" AND year=2024'
metadata_filter='author="John Doe" OR author="Jane Smith"'

# Negation
metadata_filter='NOT category="draft"'

# Complex queries
metadata_filter='(author="John Doe" OR author="Jane Smith") AND year>=2024'
```

---

## Citations & Verification

### Access Citation Information

```python
# Generate response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What is the main topic?",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.name]
                )
            )
        ]
    )
)

# Print response
print("Response:", response.text)
print("\n--- Citations ---")

# Access grounding metadata
if response.candidates[0].grounding_metadata:
    metadata = response.candidates[0].grounding_metadata

    # Print grounding support
    print(f"Grounding Support: {metadata.grounding_support}")

    # Print search entry point (which stores were queried)
    if metadata.search_entry_point:
        print(f"Search Entry Point: {metadata.search_entry_point}")

    # Print grounding chunks (what was retrieved)
    if metadata.grounding_chunks:
        for i, chunk in enumerate(metadata.grounding_chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  Document: {chunk.source.document_name}")
            print(f"  Content: {chunk.content[:200]}...")
```

### Extract Specific Citations

```python
def extract_citations(response):
    """Extract and format citations from response"""
    citations = []

    if response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata

        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                citation = {
                    'document': chunk.source.document_name,
                    'content': chunk.content,
                    'uri': chunk.source.uri if hasattr(chunk.source, 'uri') else None
                }
                citations.append(citation)

    return citations

# Use it
response = client.models.generate_content(...)
citations = extract_citations(response)

for i, citation in enumerate(citations, 1):
    print(f"\n[{i}] {citation['document']}")
    print(f"    {citation['content'][:150]}...")
```

---

## Integration with SuperClaude

### Use Case 1: Project Documentation RAG

```python
"""
SuperClaude Project Documentation Search
Indexes all project documentation for semantic search
"""

import os
from pathlib import Path
from google import genai
from google.genai import types

class SuperClaudeRAG:
    def __init__(self, api_key=None):
        self.client = genai.Client(api_key=api_key or os.getenv('GEMINI_API_KEY'))
        self.store = None

    def initialize_store(self, store_name='superclaude-docs'):
        """Create or get file search store"""
        try:
            # Try to get existing store
            stores = list(self.client.file_search_stores.list())
            for store in stores:
                if store.display_name == store_name:
                    self.store = store
                    print(f"✅ Using existing store: {store.name}")
                    return

            # Create new store
            self.store = self.client.file_search_stores.create(
                config={'display_name': store_name}
            )
            print(f"✅ Created new store: {self.store.name}")

        except Exception as e:
            print(f"❌ Error initializing store: {e}")

    def index_documentation(self, docs_path='.'):
        """Index all documentation files"""
        docs_dir = Path(docs_path)

        # File extensions to index
        extensions = ['*.md', '*.txt', '*.rst', '*.yml', '*.yaml']

        indexed_count = 0
        for ext in extensions:
            for file_path in docs_dir.glob(f"**/{ext}"):
                # Skip hidden directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue

                try:
                    print(f"Indexing {file_path}...")

                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=str(file_path),
                        file_search_store_name=self.store.name,
                        config={
                            'display_name': str(file_path),
                            'chunking_config': {
                                'white_space_config': {
                                    'max_tokens_per_chunk': 400,
                                    'max_overlap_tokens': 40
                                }
                            }
                        },
                        custom_metadata=[
                            {"key": "file_type", "string_value": file_path.suffix},
                            {"key": "file_name", "string_value": file_path.name}
                        ]
                    )

                    # Wait for completion
                    import time
                    while not operation.done:
                        time.sleep(2)
                        operation = self.client.operations.get(operation)

                    indexed_count += 1
                    print(f"  ✅ Indexed")

                except Exception as e:
                    print(f"  ❌ Error: {e}")

        print(f"\n✅ Indexed {indexed_count} files")

    def query(self, question, model="gemini-2.5-flash"):
        """Query the documentation"""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.store.name]
                            )
                        )
                    ]
                )
            )

            return {
                'answer': response.text,
                'citations': self._extract_citations(response)
            }

        except Exception as e:
            return {
                'answer': None,
                'error': str(e)
            }

    def _extract_citations(self, response):
        """Extract citations from response"""
        citations = []

        if response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata

            if metadata.grounding_chunks:
                for chunk in metadata.grounding_chunks:
                    citations.append({
                        'document': chunk.source.document_name,
                        'content': chunk.content[:200]
                    })

        return citations

# Usage
if __name__ == "__main__":
    rag = SuperClaudeRAG()
    rag.initialize_store('superclaude-docs')

    # Index all documentation
    rag.index_documentation('.')

    # Query
    result = rag.query("How do I use personas in SuperClaude?")

    print("\n--- Answer ---")
    print(result['answer'])

    if result['citations']:
        print("\n--- Sources ---")
        for i, citation in enumerate(result['citations'], 1):
            print(f"[{i}] {citation['document']}")
```

### Use Case 2: Codebase Analysis

```python
"""
SuperClaude Codebase RAG
Index and search through codebase
"""

class CodebaseRAG(SuperClaudeRAG):
    def index_codebase(self, code_path='.'):
        """Index code files"""
        code_dir = Path(code_path)

        # Code file extensions
        extensions = [
            '*.py', '*.js', '*.ts', '*.jsx', '*.tsx',
            '*.java', '*.cpp', '*.c', '*.h', '*.cs',
            '*.go', '*.rs', '*.rb', '*.php', '*.swift'
        ]

        indexed_count = 0
        for ext in extensions:
            for file_path in code_dir.glob(f"**/{ext}"):
                # Skip hidden, node_modules, venv, etc.
                skip_dirs = {'.', 'node_modules', 'venv', '__pycache__', 'dist', 'build'}
                if any(part in skip_dirs for part in file_path.parts):
                    continue

                try:
                    print(f"Indexing {file_path}...")

                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=str(file_path),
                        file_search_store_name=self.store.name,
                        config={
                            'display_name': str(file_path),
                            'chunking_config': {
                                'white_space_config': {
                                    'max_tokens_per_chunk': 500,
                                    'max_overlap_tokens': 50
                                }
                            }
                        },
                        custom_metadata=[
                            {"key": "file_type", "string_value": file_path.suffix},
                            {"key": "language", "string_value": self._detect_language(file_path.suffix)},
                            {"key": "file_name", "string_value": file_path.name}
                        ]
                    )

                    import time
                    while not operation.done:
                        time.sleep(2)
                        operation = self.client.operations.get(operation)

                    indexed_count += 1
                    print(f"  ✅ Indexed")

                except Exception as e:
                    print(f"  ❌ Error: {e}")

        print(f"\n✅ Indexed {indexed_count} files")

    def _detect_language(self, extension):
        """Detect programming language from extension"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift'
        }
        return lang_map.get(extension, 'unknown')

    def find_function(self, function_description):
        """Find functions based on description"""
        query = f"Find code that: {function_description}. Show the function definition and explain how it works."
        return self.query(query)

    def explain_pattern(self, pattern_description):
        """Explain code patterns in the codebase"""
        query = f"Explain how this pattern is implemented in the codebase: {pattern_description}"
        return self.query(query)

# Usage
if __name__ == "__main__":
    code_rag = CodebaseRAG()
    code_rag.initialize_store('superclaude-codebase')

    # Index codebase
    code_rag.index_codebase('.')

    # Find functions
    result = code_rag.find_function("handles file uploads and validation")
    print(result['answer'])
```

---

## Best Practices

### 1. Store Organization

```python
# Use separate stores for different purposes
docs_store = client.file_search_stores.create(
    config={'display_name': 'documentation'}
)

code_store = client.file_search_stores.create(
    config={'display_name': 'codebase'}
)

research_store = client.file_search_stores.create(
    config={'display_name': 'research-papers'}
)
```

### 2. Metadata Strategy

```python
# Comprehensive metadata for better filtering
metadata = [
    {"key": "doc_type", "string_value": "api-reference"},
    {"key": "version", "string_value": "2.0.1"},
    {"key": "author", "string_value": "team-name"},
    {"key": "created_date", "string_value": "2024-11-08"},
    {"key": "priority", "numeric_value": 1},
    {"key": "category", "string_value": "backend"},
    {"key": "tags", "string_list_value": {"values": ["python", "api", "rest"]}}
]
```

### 3. Chunking for Different Content Types

```python
# Documentation - medium chunks
doc_chunking = {
    'white_space_config': {
        'max_tokens_per_chunk': 400,
        'max_overlap_tokens': 40
    }
}

# Code - larger chunks for context
code_chunking = {
    'white_space_config': {
        'max_tokens_per_chunk': 600,
        'max_overlap_tokens': 60
    }
}

# Q&A / FAQs - smaller chunks
qa_chunking = {
    'white_space_config': {
        'max_tokens_per_chunk': 200,
        'max_overlap_tokens': 20
    }
}
```

### 4. Query Optimization

```python
# Specific queries work better than vague ones
# ❌ Bad
query = "Tell me about this"

# ✅ Good
query = "What are the authentication methods supported in the API?"

# ✅ Better with context
query = """
Based on the API documentation, explain:
1. Supported authentication methods
2. Required headers
3. Example request with authentication
"""
```

### 5. Error Handling

```python
def safe_upload(file_path, store_name):
    """Upload with error handling and retry"""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store_name,
                config={'display_name': file_path.name}
            )

            import time
            timeout = 300  # 5 minutes
            elapsed = 0

            while not operation.done and elapsed < timeout:
                time.sleep(5)
                elapsed += 5
                operation = client.operations.get(operation)

            if operation.done:
                print(f"✅ {file_path.name} uploaded successfully")
                return True
            else:
                print(f"⏱️ Upload timeout for {file_path.name}")
                retry_count += 1

        except Exception as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
            retry_count += 1
            time.sleep(5 * retry_count)  # Exponential backoff

    return False
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Operation Never Completes

**Symptom:** Upload operation stuck in pending state

**Solution:**
```python
# Add timeout
import time

timeout = 300  # 5 minutes
elapsed = 0

while not operation.done and elapsed < timeout:
    time.sleep(5)
    elapsed += 5
    operation = client.operations.get(operation)
    print(f"Status: {operation.status} ({elapsed}s)")

if not operation.done:
    print("❌ Operation timeout - file may be too large")
```

#### Issue 2: File Too Large

**Symptom:** Error uploading large files

**Solution:**
```python
# Check file size before upload
import os

file_size = os.path.getsize(file_path)
max_size = 100 * 1024 * 1024  # 100 MB

if file_size > max_size:
    print(f"❌ File too large: {file_size / 1024 / 1024:.2f} MB")
    # Option 1: Split file
    # Option 2: Compress file
    # Option 3: Extract text only
else:
    # Upload
    pass
```

#### Issue 3: Poor Retrieval Quality

**Symptom:** Irrelevant results returned

**Solutions:**
```python
# 1. Adjust chunking
config = {
    'chunking_config': {
        'white_space_config': {
            'max_tokens_per_chunk': 300,  # Try different sizes
            'max_overlap_tokens': 30
        }
    }
}

# 2. Use more specific queries
query = "What is the exact syntax for authentication headers in the REST API?"

# 3. Filter by metadata
metadata_filter = 'doc_type="api-reference" AND version="2.0.1"'

# 4. Use gemini-2.5-pro for better understanding
model = "gemini-2.5-pro"
```

#### Issue 4: Rate Limits

**Symptom:** 429 errors during bulk uploads

**Solution:**
```python
import time

def bulk_upload_with_rate_limit(files, store_name, delay=2):
    """Upload multiple files with rate limiting"""
    for file_path in files:
        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store_name,
                config={'display_name': file_path.name}
            )

            # Wait for completion
            while not operation.done:
                time.sleep(2)
                operation = client.operations.get(operation)

            print(f"✅ {file_path.name}")

            # Rate limit delay
            time.sleep(delay)

        except Exception as e:
            if "429" in str(e):
                print(f"⏸️ Rate limit hit, waiting 60s...")
                time.sleep(60)
                # Retry this file
                continue
            else:
                print(f"❌ Error: {e}")
```

#### Issue 5: Storage Quota Exceeded

**Symptom:** Cannot upload more files

**Solution:**
```python
# Check and clean old stores
stores = list(client.file_search_stores.list())

print(f"Total stores: {len(stores)}")

for store in stores:
    print(f"\nStore: {store.display_name}")
    print(f"Name: {store.name}")

    # Delete old/unused stores
    # client.file_search_stores.delete(name=store.name, config={'force': True})
```

---

## Pricing & Limits

### Rate Limits

- **Maximum file size**: 100 MB per file
- **Total storage (Free tier)**: 1 GB
- **Total storage (Tier 1)**: 10 GB
- **Total storage (Tier 2)**: 100 GB
- **Total storage (Tier 3)**: 1 TB
- **Recommended store size**: Under 20 GB for optimal latency

### Pricing

**Indexing (Embedding Generation):**
- $0.15 per 1M tokens (using `gemini-embedding-001`)
- Charged once during file upload/import

**Storage:**
- Free of charge

**Query Embeddings:**
- Free of charge

**Retrieved Context:**
- Charged as regular context tokens
- `gemini-2.5-flash`: $0.000002 per token
- `gemini-2.5-pro`: $0.00001 per token

### Cost Estimation

```python
# Example: 100 documents, 10 pages each, 300 words per page
documents = 100
pages_per_doc = 10
words_per_page = 300
tokens_per_word = 1.3  # Average

total_tokens = documents * pages_per_doc * words_per_page * tokens_per_word
# = 100 * 10 * 300 * 1.3 = 390,000 tokens

# Indexing cost
indexing_cost = (total_tokens / 1_000_000) * 0.15
# = 0.39 * $0.15 = $0.0585

print(f"One-time indexing cost: ${indexing_cost:.4f}")

# Storage: Free
# Query costs: Depends on usage
```

---

## Supported File Types

### Application Files
- PDF (`application/pdf`)
- Word Documents (`application/msword`, `.docx`)
- Excel Spreadsheets (`.xlsx`, `.xls`)
- PowerPoint (`.pptx`)
- JSON (`application/json`)
- ZIP archives

### Text Files
- Plain text (`.txt`)
- Markdown (`.md`)
- HTML (`.html`)
- CSV (`.csv`)
- XML (`.xml`)
- YAML (`.yml`, `.yaml`)
- LaTeX (`.tex`)
- Rich Text Format (`.rtf`)

### Code Files
- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- Go (`.go`)
- Rust (`.rs`)
- Ruby (`.rb`)
- PHP (`.php`)
- Swift (`.swift`)
- Kotlin (`.kt`)
- And many more...

*See full list in [official documentation](https://ai.google.dev/gemini-api/docs/file-search#supported-file-types)*

---

## Additional Resources

### Official Documentation
- **File Search Guide**: https://ai.google.dev/gemini-api/docs/file-search
- **File Search Stores API**: https://ai.google.dev/api/file-search/file-search-stores
- **File Search Documents API**: https://ai.google.dev/api/file-search/documents
- **Embeddings**: https://ai.google.dev/gemini-api/docs/embeddings
- **Pricing**: https://ai.google.dev/gemini-api/docs/pricing

### Related SuperClaude Docs
- [MCP Setup Guide](MCP_SETUP.md)
- [SuperClaude Commands](COMMANDS.md)
- [README](README.md)

---

**Last Updated:** November 2025
**SuperClaude Version:** 2.0.1
**Gemini API Version:** v2.5

💡 **Pro Tip:** Combine File Search with MCP servers for maximum productivity:
- Use **Ref** for live documentation
- Use **File Search** for your custom knowledge base
- Use **Sequential** for complex analysis
- Use **OpenRouter** for multi-model comparison

---

*This integration guide is part of the SuperClaude framework. For questions or issues, visit [GitHub Issues](https://github.com/NomenAK/SuperClaude/issues)*
