# Gemini File Search Examples

Python examples for integrating Gemini File Search with SuperClaude.

## Prerequisites

```bash
# Install dependencies
pip install google-genai

# Set API key
export GEMINI_API_KEY='your-api-key-here'
```

## Examples

### 1. Documentation RAG (`superclaude_rag.py`)

Index and search SuperClaude documentation using semantic search.

**Index all documentation:**
```bash
python superclaude_rag.py --index
```

**Query documentation:**
```bash
python superclaude_rag.py --query "How do I use personas in SuperClaude?"
```

**Query with citations:**
```bash
python superclaude_rag.py --query "What are MCP servers?" --verbose
```

**List indexed documents:**
```bash
python superclaude_rag.py --list
```

### 2. Codebase RAG (`codebase_rag.py`)

Index and analyze codebase using semantic search.

**Index entire codebase:**
```bash
python codebase_rag.py --index
```

**Index specific language:**
```bash
python codebase_rag.py --index --language python
```

**Query codebase:**
```bash
python codebase_rag.py --query "How does authentication work?"
```

**Find functions:**
```bash
python codebase_rag.py --find-function "handles user login"
```

**Explain patterns:**
```bash
python codebase_rag.py --explain-pattern "dependency injection" --language python
```

**Analyze dependencies:**
```bash
python codebase_rag.py --analyze-deps "src/auth/login.py"
```

**List languages:**
```bash
python codebase_rag.py --list-languages
```

## Features

### Documentation RAG
- ✅ Automatic documentation indexing
- ✅ Semantic search across all docs
- ✅ Citation support
- ✅ Multiple file format support (MD, TXT, RST, YAML)
- ✅ Metadata filtering

### Codebase RAG
- ✅ Multi-language support (Python, JavaScript, TypeScript, Java, Go, Rust, etc.)
- ✅ Automatic language detection
- ✅ Function/method finding
- ✅ Pattern explanation
- ✅ Dependency analysis
- ✅ Code search with context

## File Search Stores

Both examples create persistent file search stores:
- `superclaude-docs` - Documentation store
- `superclaude-codebase` - Codebase store

Stores are kept indefinitely and only need to be created once.

## Customization

### Change Store Name

```bash
python superclaude_rag.py --index --store-name "my-custom-store"
```

### Change Model

```bash
python superclaude_rag.py --query "question" --model "gemini-2.5-pro"
```

### Custom Documentation Path

```bash
python superclaude_rag.py --index --docs-path "/path/to/docs"
```

## Advanced Usage

### Multi-turn Conversations

Modify the scripts to maintain conversation history for context-aware queries:

```python
conversation = []

# First query
query1 = "What are personas?"
conversation.append({"role": "user", "parts": [query1]})
response1 = rag.query(query1)
conversation.append({"role": "model", "parts": [response1['answer']]})

# Follow-up query
query2 = "Can you show me an example?"
conversation.append({"role": "user", "parts": [query2]})
response2 = rag.query(query2)
```

### Metadata Filtering

Add custom metadata during indexing and filter during queries:

```python
# In index_documentation or index_codebase
custom_metadata=[
    {"key": "category", "string_value": "backend"},
    {"key": "priority", "numeric_value": 1},
    {"key": "author", "string_value": "team-name"}
]

# Filter during query
metadata_filter='category="backend" AND priority=1'
```

## Troubleshooting

**Error: GEMINI_API_KEY not found**
```bash
# Set API key
export GEMINI_API_KEY='your-api-key-here'

# Or add to .env file
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

**Error: File too large**
- Files larger than 100MB are not supported
- Large files are automatically skipped during indexing

**Error: Rate limit exceeded**
- The scripts include automatic rate limiting (1-2s delay between uploads)
- If you hit limits, wait a few minutes and retry

**Poor search results**
- Try more specific queries
- Use verbose mode to see what was retrieved
- Consider adjusting chunking configuration
- Use gemini-2.5-pro for better understanding

## Cost Estimation

**Indexing (one-time cost):**
- $0.15 per 1M tokens
- Average project (~500 files, 10MB total) ≈ $0.05

**Storage:**
- Free

**Queries:**
- gemini-2.5-flash: $0.000002/token (very cheap)
- gemini-2.5-pro: $0.00001/token (more expensive but better quality)

## Learn More

- [Gemini File Search Guide](../../GEMINI_FILE_SEARCH.md)
- [Official Documentation](https://ai.google.dev/gemini-api/docs/file-search)
- [SuperClaude MCP Setup](../../MCP_SETUP.md)
