# TV3 AI NewsCaster - Integration Examples

Complete implementation examples for integrating MCP servers and Gemini File Search with TV3 AI NewsCaster project.

## 📚 Documentation

**Main Integration Plan:** [TV3_INTEGRATION_PLAN.md](../../TV3_INTEGRATION_PLAN.md)

This directory contains ready-to-use Python scripts for:
1. News archive RAG system
2. Smart bulletin generation
3. Article search and discovery

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install google-genai supabase python-dotenv

# Set environment variables
export GEMINI_API_KEY='your-gemini-api-key'
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-supabase-anon-key'
```

### Initialize

```bash
# 1. Initialize file search store
python news_archive_rag.py --init

# 2. Index recent articles (last 7 days)
python news_archive_rag.py --index-recent --days 7

# 3. Test search
python news_archive_rag.py --search "politične novice"
```

---

## 📖 Scripts

### 1. News Archive RAG (`news_archive_rag.py`)

Semantic search across all news articles.

**Features:**
- ✅ Index articles from Supabase
- ✅ Semantic search (not keyword-based)
- ✅ Category filtering
- ✅ Date range filtering
- ✅ Citation support

**Usage:**

```bash
# Initialize store
python news_archive_rag.py --init

# Index recent articles (last 7 days)
python news_archive_rag.py --index-recent --days 7

# Index all articles from last 30 days
python news_archive_rag.py --index-recent --days 30

# Search all articles
python news_archive_rag.py --search "Kaj se dogaja v politiki?"

# Search with category filter
python news_archive_rag.py --search "športne novice" --category sports

# Search with date filter
python news_archive_rag.py --search "novice" --date-from 2024-11-01

# Use Pro model for better quality
python news_archive_rag.py --search "analiza gospodarstva" --model gemini-2.5-pro
```

---

### 2. Smart Bulletin Generator (`smart_bulletin_generator.py`)

Generate AI-powered news bulletins using RAG.

**Features:**
- ✅ Topic-specific bulletins
- ✅ Daily comprehensive bulletins
- ✅ Trending topic analysis
- ✅ Topic suggestions
- ✅ Slovenian language output
- ✅ Professional TV news format

**Usage:**

```bash
# Generate 2-minute bulletin on politics
python smart_bulletin_generator.py --topic "politika" --duration 2

# Generate 3-minute sports bulletin
python smart_bulletin_generator.py --topic "šport" --duration 3

# Generate 5-minute daily bulletin
python smart_bulletin_generator.py --daily --duration 5

# Find trending topics (last 7 days)
python smart_bulletin_generator.py --trending --days 7

# Get bulletin topic suggestions
python smart_bulletin_generator.py --suggest-topics

# Save bulletin to file
python smart_bulletin_generator.py --topic "gospodarstvo" --duration 2 --save
```

**Example Output:**

```
TV3 NEWS BULLETIN
================================================================================

Topic: politika
Duration: 2 minutes
Word Count: 287 words
Generated: 2024-11-08T15:30:45

--------------------------------------------------------------------------------
SCRIPT:
--------------------------------------------------------------------------------

[OPENING - upbeat tone]

Dober večer in dobrodošli na TV3. V današnjem političnem pregledu vas čakajo
pomembne novice o...

[MAIN CONTENT]

Vlada je danes obravnavala predlog... [itd]

[CLOSING]

To je bil pregled najpomembnejših političnih novic. Hvala za vašo pozornost.

--------------------------------------------------------------------------------
SOURCES:
--------------------------------------------------------------------------------

[1] 2024-11-08 - Vlada obravnavala proračun
[2] 2024-11-07 - Parlamentarna razprava o...
```

---

## 🎯 Integration with TV3 Backend

### Supabase Edge Function

```typescript
// supabase/functions/generate-bulletin/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

serve(async (req) => {
  const { topic, duration } = await req.json()

  // Call Python script
  const cmd = `python3 scripts/smart_bulletin_generator.py generate "${topic}" --duration ${duration}`

  const { stdout } = await execAsync(cmd)
  const bulletin = JSON.parse(stdout)

  // Save to database
  const { data } = await supabase
    .from('bulletins')
    .insert({
      title: `${topic} - ${duration}min`,
      content: bulletin.script,
      metadata: bulletin
    })
    .select()
    .single()

  return new Response(JSON.stringify(bulletin))
})
```

### React Component

```tsx
// components/BulletinGenerator.tsx

export function BulletinGenerator() {
  const [topic, setTopic] = useState('')
  const [bulletin, setBulletin] = useState(null)

  async function generate() {
    const res = await fetch('/api/generate-bulletin', {
      method: 'POST',
      body: JSON.stringify({ topic, duration: 2 })
    })
    const data = await res.json()
    setBulletin(data)
  }

  return (
    <div>
      <Input
        placeholder="Tema oddaje..."
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />
      <Button onClick={generate}>Generiraj</Button>

      {bulletin && (
        <div>
          <h3>Skript</h3>
          <Textarea value={bulletin.script} rows={15} />
        </div>
      )}
    </div>
  )
}
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Gemini API
GEMINI_API_KEY=AIzaSy...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbG...

# Optional: For MCP servers
FIRECRAWL_API_KEY=fc-...
OPENROUTER_API_KEY=sk-or-...
BROWSERBASE_API_KEY=bb_live_...
```

### Database Schema

```sql
-- Articles table (must exist)
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT,
  url TEXT NOT NULL UNIQUE,
  published_at TIMESTAMP,
  category TEXT,
  source_id UUID REFERENCES rss_sources(id),
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- RSS Sources table
CREATE TABLE rss_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  category TEXT,
  active BOOLEAN DEFAULT true
);

-- Bulletins table
CREATE TABLE bulletins (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT,
  metadata JSONB,
  generated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 Features & Benefits

### News Archive RAG

**Traditional Search:**
```sql
SELECT * FROM articles WHERE title ILIKE '%politics%'
```
❌ Only finds exact keyword matches
❌ Misses related content
❌ No understanding of meaning

**Semantic Search (RAG):**
```python
rag.search_articles("Kaj se dogaja v politiki?")
```
✅ Understands meaning and context
✅ Finds related topics even without exact keywords
✅ Returns AI-generated summaries
✅ Includes source citations

### Smart Bulletin Generation

**Traditional Approach:**
1. Manually select articles
2. Read through each one
3. Write bulletin script
4. Edit and revise
⏱️ Time: 30-60 minutes

**AI-Powered Approach:**
1. Specify topic and duration
2. AI finds relevant articles
3. AI generates professional script
4. Review and adjust if needed
⏱️ Time: 2-5 minutes

---

## 💡 Use Cases

### 1. Quick Bulletin Creation

```bash
# Need a 2-minute politics bulletin?
python smart_bulletin_generator.py --topic "politika" --duration 2

# Done! Professional script ready in seconds
```

### 2. Daily News Overview

```bash
# Generate complete daily bulletin
python smart_bulletin_generator.py --daily --duration 5

# Covers: politics, economy, sports, culture
```

### 3. Topic Research

```bash
# What are people talking about?
python smart_bulletin_generator.py --trending --days 7

# Get trending topics with context
```

### 4. Article Discovery

```bash
# Find articles about specific topic
python news_archive_rag.py --search "volitve 2024" --category politics

# Get AI summary with sources
```

### 5. Content Planning

```bash
# Need bulletin topic ideas?
python smart_bulletin_generator.py --suggest-topics

# Get 5 newsworthy topic suggestions
```

---

## 🔍 How It Works

### Indexing Pipeline

```
Articles in Supabase
       ↓
Extract (title, content, metadata)
       ↓
Convert to text document
       ↓
Chunk into 400-token pieces
       ↓
Generate embeddings (Gemini)
       ↓
Store in File Search Store
       ↓
Ready for semantic search!
```

### Search Pipeline

```
User Query ("politične novice")
       ↓
Convert to embedding (Gemini)
       ↓
Vector similarity search
       ↓
Retrieve relevant chunks
       ↓
Gemini generates answer
       ↓
Return answer + citations
```

### Bulletin Generation Pipeline

```
User specifies topic + duration
       ↓
RAG search for relevant articles
       ↓
Gemini Pro analyzes and summarizes
       ↓
Generate professional script
       ↓
Format for TV broadcast
       ↓
Return with sources
```

---

## 🎓 Best Practices

### Indexing

1. **Index regularly** - Run daily to keep archive current
   ```bash
   # Cron job: every day at 2 AM
   0 2 * * * python news_archive_rag.py --index-recent --days 1
   ```

2. **Use appropriate metadata** - Helps with filtering
   ```python
   metadata=[
       {"key": "category", "string_value": "politics"},
       {"key": "published_date", "string_value": "2024-11-08"}
   ]
   ```

3. **Monitor storage** - Check file search store size
   ```python
   stores = list(client.file_search_stores.list())
   print(f"Total stores: {len(stores)}")
   ```

### Searching

1. **Be specific** - Better queries = better results
   ```bash
   # ❌ Vague
   python news_archive_rag.py --search "novice"

   # ✅ Specific
   python news_archive_rag.py --search "Kakšne so bile včerajšnje volitve?"
   ```

2. **Use filters** - Narrow down results
   ```bash
   # Filter by category and date
   python news_archive_rag.py --search "šport" --category sports --date-from 2024-11-01
   ```

3. **Choose right model**
   - `gemini-2.5-flash` - Fast, cheap, good quality (default)
   - `gemini-2.5-pro` - Slower, more expensive, best quality

### Bulletin Generation

1. **Appropriate duration** - Match content to time
   ```bash
   # Simple topic → short bulletin
   python smart_bulletin_generator.py --topic "nogomet" --duration 1

   # Complex topic → longer bulletin
   python smart_bulletin_generator.py --topic "gospodarska politika" --duration 3
   ```

2. **Review and edit** - AI is good but not perfect
   - Always review generated scripts
   - Edit for accuracy and tone
   - Check facts with sources

3. **Save important bulletins**
   ```bash
   python smart_bulletin_generator.py --topic "volitve" --save
   # Creates: bulletin_volitve_20241108_153045.json
   ```

---

## 🐛 Troubleshooting

### "Store not initialized"
```bash
# Run initialization first
python news_archive_rag.py --init
```

### "No articles found"
```bash
# Check Supabase connection
python -c "from supabase import create_client; client = create_client('$SUPABASE_URL', '$SUPABASE_KEY'); print(client.table('articles').select('id').limit(1).execute())"

# Index articles
python news_archive_rag.py --index-recent --days 30
```

### "GEMINI_API_KEY not found"
```bash
# Set in environment
export GEMINI_API_KEY='your-key-here'

# Or use .env file
echo "GEMINI_API_KEY=your-key-here" >> .env
```

### Poor search results
```bash
# Try more specific query
python news_archive_rag.py --search "Kakšne so bile zadnje politične spremembe?" --model gemini-2.5-pro

# Use category filter
python news_archive_rag.py --search "novice" --category politics

# Check what's indexed
python news_archive_rag.py --list-documents
```

---

## 💰 Cost Estimation

### Indexing Costs
- **1000 articles** × 1000 tokens = 1M tokens
- **Cost:** $0.15 (one-time)

### Search Costs
- **1000 queries/month** × 500 tokens = 0.5M tokens
- **Cost:** $0.001 (gemini-2.5-flash)

### Bulletin Generation
- **100 bulletins/month** × 2000 tokens = 0.2M tokens
- **Cost:** $0.002 (gemini-2.5-pro input) + $0.006 (output)

**Total Monthly: ~$0.01 - $0.20** (very affordable!)

---

## 📚 Learn More

- [TV3 Integration Plan](../../TV3_INTEGRATION_PLAN.md) - Complete integration guide
- [Gemini File Search Guide](../../GEMINI_FILE_SEARCH.md) - File Search documentation
- [MCP Setup Guide](../../MCP_SETUP.md) - MCP servers configuration
- [Official Gemini Docs](https://ai.google.dev/gemini-api/docs/file-search) - Google documentation

---

## 🤝 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [TV3_INTEGRATION_PLAN.md](../../TV3_INTEGRATION_PLAN.md)
3. Open issue at [SuperClaude GitHub](https://github.com/NomenAK/SuperClaude/issues)

---

**Last Updated:** November 2025
**Project:** TV3 AI NewsCaster
**Framework:** SuperClaude v2.0.1
