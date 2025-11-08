# SuperClaude Quick Start Guide

Get SuperClaude up and running in 5 minutes!

---

## 🚀 Quick Deploy

### Option 1: Automated Deployment (Recommended)

```bash
# Run the deployment script
./deploy.sh
```

This will:
- ✅ Check Python environment
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up configuration files
- ✅ Run validation tests

### Option 2: Manual Deployment

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r examples/gemini-file-search/requirements.txt
pip install -r examples/tv3-integration/requirements.txt

# 3. Configure environment
cp .env.example .env
cp claude_mcp_config.example.json claude_mcp_config.json

# 4. Edit .env and add your API keys
nano .env
```

---

## 🧪 Test Without API Keys (Demo Mode)

Run the demo test to verify everything is working:

```bash
python3 examples/demo/demo_test.py
```

This will test:
- ✅ All 4 Python scripts
- ✅ Module imports
- ✅ File structure
- ✅ MCP configuration
- ✅ Documentation completeness

**No API keys required!** This is perfect for:
- Testing the installation
- Understanding the structure
- Exploring features
- Demo presentations

---

## 🔑 Get API Keys

### Required: Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Copy your key
4. Add to `.env`:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

**Free tier:** 15 requests per minute (perfect for testing!)

### Optional: Supabase (For TV3 Features)

1. Visit [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to Settings → API
4. Copy URL and anon/service_role key
5. Add to `.env`:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

---

## 📖 Usage Examples

### 1. Search SuperClaude Documentation

```bash
# Index all documentation
python3 examples/gemini-file-search/superclaude_rag.py --index

# Ask questions
python3 examples/gemini-file-search/superclaude_rag.py --query "How do I use MCP servers?"

# List indexed files
python3 examples/gemini-file-search/superclaude_rag.py --list
```

**Example output:**
```
📄 Indexing: CLAUDE.md (45.2KB)
📄 Indexing: MCP_SETUP.md (32.1KB)
✅ Indexed 12 documentation files

Query: How do I use MCP servers?
Answer: MCP servers are configured in claude_mcp_config.json...
Citations: MCP_SETUP.md, .claude/shared/superclaude-mcp.yml
```

### 2. Analyze Your Codebase

```bash
# Index codebase
python3 examples/gemini-file-search/codebase_rag.py --index

# Find functions
python3 examples/gemini-file-search/codebase_rag.py --find "user authentication"

# Get architecture overview
python3 examples/gemini-file-search/codebase_rag.py --overview

# Search specific language
python3 examples/gemini-file-search/codebase_rag.py --search "database connection" --language python
```

**Supported languages:** Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, C#, Ruby, PHP, Swift, Kotlin, and 16 more!

### 3. TV3 News Integration (Requires Supabase)

```bash
# Initialize news archive
python3 examples/tv3-integration/news_archive_rag.py --init

# Index recent articles (last 7 days)
python3 examples/tv3-integration/news_archive_rag.py --index-recent --days 7

# Search articles
python3 examples/tv3-integration/news_archive_rag.py --search "politične novice"

# Search with filters
python3 examples/tv3-integration/news_archive_rag.py --search "gospodarstvo" --category economy --date-from 2024-11-01
```

### 4. Generate News Bulletins

```bash
# Generate topic bulletin (2 minutes)
python3 examples/tv3-integration/smart_bulletin_generator.py --topic "tehnologija" --duration 2

# Generate daily bulletin (5 minutes, all categories)
python3 examples/tv3-integration/smart_bulletin_generator.py --daily --duration 5

# Find trending topics
python3 examples/tv3-integration/smart_bulletin_generator.py --trending --days 7

# Get topic suggestions
python3 examples/tv3-integration/smart_bulletin_generator.py --suggest-topics

# Save bulletin to file
python3 examples/tv3-integration/smart_bulletin_generator.py --topic "šport" --duration 3 --save
```

**Output format:**
```
═══════════════════════════════════════════════════════
TV3 NOVICE - DNEVNI BILTEN
Trajanje: 5 minut
═══════════════════════════════════════════════════════

[UVOD]
Dober večer in dobrodošli v osrednji izdaji TV3 novic...

[POLITIKA]
V ospredju političnih dogajanj je danes...

[GOSPODARSTVO]
Slovenska gospodarska rast...

[ŠPORT]
V športnih novicah...

[ZAKLJUČEK]
To je bilo vse za današnji pregled. Hvala za vašo pozornost...

═══════════════════════════════════════════════════════
```

---

## 🎯 Common Use Cases

### Use Case 1: Documentation Assistant

**Problem:** Hard to find information in large documentation
**Solution:** Index docs and ask questions in natural language

```bash
python3 examples/gemini-file-search/superclaude_rag.py --index
python3 examples/gemini-file-search/superclaude_rag.py --query "How do personas work?"
```

### Use Case 2: Code Understanding

**Problem:** New to a codebase, need to understand architecture
**Solution:** Semantic code search and analysis

```bash
python3 examples/gemini-file-search/codebase_rag.py --index
python3 examples/gemini-file-search/codebase_rag.py --overview
python3 examples/gemini-file-search/codebase_rag.py --find "authentication logic"
```

### Use Case 3: News Research

**Problem:** Need to find specific news articles from archive
**Solution:** Semantic search across all articles

```bash
python3 examples/tv3-integration/news_archive_rag.py --search "covid statistics" --date-from 2024-10-01
```

### Use Case 4: Bulletin Automation

**Problem:** Manual bulletin creation takes 30-60 minutes
**Solution:** AI-powered generation in 2-5 minutes

```bash
python3 examples/tv3-integration/smart_bulletin_generator.py --daily --duration 5 --save
```

**Time saved:** 85-90% (60 min → 5 min)

---

## 📊 Features Overview

### SuperClaude Documentation RAG
- ✅ Index .md, .txt, .rst, .yml files
- ✅ Semantic search with citations
- ✅ Store management
- ✅ Fast queries (<2 seconds)

### Codebase Analysis RAG
- ✅ 29 programming languages
- ✅ Find functions by description
- ✅ Explain design patterns
- ✅ Dependency analysis
- ✅ Architecture overview

### TV3 News Archive RAG
- ✅ Supabase integration
- ✅ Category filtering (politics, economy, sports, culture)
- ✅ Date range filtering
- ✅ Source tracking
- ✅ Semantic article search

### Smart Bulletin Generator
- ✅ Topic bulletins (2-5 minutes)
- ✅ Daily bulletins (5-10 minutes)
- ✅ Trending topics analysis
- ✅ Slovenian language output
- ✅ Professional TV format
- ✅ JSON export

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required for all RAG functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for TV3 integration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional - for MCP servers
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
BROWSERBASE_API_KEY=your_browserbase_api_key_here
REF_API_KEY=your_ref_api_key_here
```

### MCP Server Configuration

Edit `claude_mcp_config.json`:

```json
{
  "mcpServers": {
    "ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_REF_API_KEY_HERE"
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "YOUR_SUPABASE_ACCESS_TOKEN_HERE"]
    }
  }
}
```

See `MCP_SETUP.md` for complete configuration guide.

---

## 🐛 Troubleshooting

### Error: `GEMINI_API_KEY not found`

**Solution:** Add your API key to `.env` file:
```bash
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Error: `ModuleNotFoundError: No module named 'google'`

**Solution:** Install dependencies:
```bash
pip install google-genai
# Or run deployment script:
./deploy.sh
```

### Error: `Store not initialized`

**Solution:** Run initialization command first:
```bash
python3 examples/tv3-integration/news_archive_rag.py --init
```

### Slow indexing

**Normal behavior!** Indexing is a one-time operation:
- Small docs (100 files): 2-5 minutes
- Large codebase (1000 files): 10-20 minutes
- Queries are fast (<2 seconds)

### Poor search results

**Try these:**
1. Be more specific in your query
2. Use the Pro model: add `--model gemini-2.0-flash-exp` to query
3. Add more context to indexed files
4. Check that files were indexed correctly with `--list`

---

## 💰 Cost Estimation

### Gemini API Costs (Very Affordable!)

**Indexing (one-time):**
- 1000 files: ~$0.15
- 10,000 pages: ~$1.50

**Querying (ongoing):**
- Flash model: $0.001 per 1,000 queries
- Pro model: $0.008 per 1,000 queries

**Example monthly costs:**
- 1,000 queries/month: <$0.01
- 10,000 queries/month: <$0.10
- 100 bulletins/month: ~$0.80

**Total: Usually <$2/month for typical usage!**

---

## 📚 Documentation

### Complete Guides

| Document | Description | Lines |
|----------|-------------|-------|
| `GEMINI_FILE_SEARCH.md` | Complete File Search integration guide | 1,214 |
| `TV3_INTEGRATION_PLAN.md` | Full TV3 implementation roadmap | 1,378 |
| `MCP_SETUP.md` | MCP server configuration guide | 574 |
| `FUNCTIONAL_TEST_REPORT.md` | Comprehensive test results | 1,077 |
| `QUICK_START.md` | This guide | You're here! |

### Example READMEs

- `examples/gemini-file-search/README.md` - RAG systems guide
- `examples/tv3-integration/README.md` - TV3 integration guide

---

## 🎓 Learning Path

### Beginner (0-15 minutes)
1. ✅ Run `./deploy.sh`
2. ✅ Run `python3 examples/demo/demo_test.py`
3. ✅ Read `QUICK_START.md` (this file)
4. ✅ Get Gemini API key

### Intermediate (15-60 minutes)
1. ✅ Index SuperClaude documentation
2. ✅ Try different queries
3. ✅ Read `GEMINI_FILE_SEARCH.md`
4. ✅ Index your own codebase
5. ✅ Explore code analysis features

### Advanced (1+ hours)
1. ✅ Set up Supabase for TV3
2. ✅ Read `TV3_INTEGRATION_PLAN.md`
3. ✅ Configure all 6 MCP servers
4. ✅ Customize scripts for your needs
5. ✅ Deploy to production

---

## 🤝 Support

### Resources

- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory
- **Issues:** GitHub issue tracker
- **Discussions:** GitHub discussions

### Common Questions

**Q: Do I need all API keys?**
A: No! Only `GEMINI_API_KEY` is required. Others are optional for specific features.

**Q: Can I use this commercially?**
A: Check the license file. Generally yes, with attribution.

**Q: Does this work on Windows?**
A: Yes! Python scripts work on Windows, Mac, and Linux.

**Q: How long does indexing take?**
A: Depends on size. ~50-100 files per minute. It's a one-time operation.

**Q: Can I index private/proprietary code?**
A: Yes! All data is sent to Gemini API securely. Check Google's privacy policy.

**Q: What's the file size limit?**
A: Default is 10MB per file. Adjustable in code.

---

## 🚀 What's Next?

After following this guide, check out:

1. **GEMINI_FILE_SEARCH.md** - Deep dive into File Search capabilities
2. **TV3_INTEGRATION_PLAN.md** - Complete TV3 implementation guide
3. **FUNCTIONAL_TEST_REPORT.md** - See all test results
4. **MCP_SETUP.md** - Configure additional MCP servers

---

## ✨ Quick Command Reference

```bash
# Deployment
./deploy.sh                          # Automated setup
python3 examples/demo/demo_test.py   # Demo mode (no API keys)

# Documentation Search
python3 examples/gemini-file-search/superclaude_rag.py --index
python3 examples/gemini-file-search/superclaude_rag.py --query "question"

# Code Analysis
python3 examples/gemini-file-search/codebase_rag.py --index
python3 examples/gemini-file-search/codebase_rag.py --overview

# TV3 News (requires Supabase)
python3 examples/tv3-integration/news_archive_rag.py --init
python3 examples/tv3-integration/news_archive_rag.py --index-recent --days 7
python3 examples/tv3-integration/smart_bulletin_generator.py --daily --duration 5
```

---

**Ready to go? Start with:**
```bash
./deploy.sh
```

**Have fun exploring SuperClaude! 🎉**
