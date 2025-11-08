# TV3 AI NewsCaster - MCP & Gemini File Search Integration Plan

**Comprehensive Integration Strategy**
**Project:** TV3 AI NewsCaster Admin Panel
**Date:** November 2025
**SuperClaude Version:** 2.0.1

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Current Architecture](#current-architecture)
3. [MCP Servers Integration](#mcp-servers-integration)
4. [Gemini File Search Implementation](#gemini-file-search-implementation)
5. [Complete Implementation Guide](#complete-implementation-guide)
6. [Code Examples](#code-examples)
7. [Deployment Strategy](#deployment-strategy)

---

## Project Overview

### TV3 AI NewsCaster
**Purpose:** AI-powered news aggregation and bulletin generation system

**Key Components:**
- RSS feed aggregation
- Article extraction and processing
- AI-powered content generation
- News bulletin creation
- React admin panel

**Tech Stack:**
- Frontend: React, TypeScript
- Backend: Supabase (PostgreSQL + Edge Functions)
- AI Processing: OpenRouter (multiple models)
- Web Scraping: Firecrawl, Browserbase
- API: REST + Supabase Realtime

---

## Current Architecture

### Database Schema (Supabase)

```sql
-- RSS Sources
CREATE TABLE rss_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  category TEXT,
  language TEXT DEFAULT 'sl',
  active BOOLEAN DEFAULT true,
  last_fetched TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Articles
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES rss_sources(id),
  title TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  content TEXT,
  summary TEXT,
  published_at TIMESTAMP,
  scraped_at TIMESTAMP,
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Bulletins
CREATE TABLE bulletins (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT,
  articles JSONB, -- Array of article IDs
  generated_at TIMESTAMP DEFAULT NOW(),
  published BOOLEAN DEFAULT false
);
```

### Current Workflow

```
1. RSS Feed Fetch (Scheduled)
   ↓
2. Extract Article URLs
   ↓
3. Firecrawl Scraping → Article Content
   ↓
4. OpenRouter AI → Summarization
   ↓
5. Store in Supabase
   ↓
6. Generate Bulletin (AI aggregation)
   ↓
7. Admin Panel Display
```

---

## MCP Servers Integration

### 1. **Supabase MCP** - Database Management

**Use Cases:**
- Direct database queries from admin panel
- Real-time schema inspection
- Edge Functions monitoring
- Data validation

**Integration Points:**

```typescript
// 1. Query articles directly
const articles = await supabaseMCP.query(`
  SELECT a.*, s.name as source_name
  FROM articles a
  JOIN rss_sources s ON a.source_id = s.id
  WHERE a.processed = false
  ORDER BY published_at DESC
  LIMIT 50
`);

// 2. Monitor Edge Functions
const functions = await supabaseMCP.listEdgeFunctions();

// 3. Schema inspection
const schema = await supabaseMCP.describeTable('articles');
```

**Benefits:**
- ✅ Quick database debugging
- ✅ Schema validation
- ✅ Real-time monitoring
- ✅ No need for external DB clients

---

### 2. **Firecrawl MCP** - Article Content Extraction

**Use Cases:**
- Extract full article content from URLs
- Convert HTML to clean Markdown
- Handle JavaScript-rendered pages
- Batch scraping optimization

**Integration:**

```typescript
// Article scraping workflow
async function scrapeArticle(url: string) {
  // Use Firecrawl for static content
  const result = await firecrawlMCP.scrape({
    url: url,
    formats: ['markdown', 'html'],
    onlyMainContent: true
  });

  return {
    title: result.metadata.title,
    content: result.markdown,
    author: result.metadata.author,
    publishedAt: result.metadata.publishDate
  };
}

// Batch scraping from RSS feed
async function processFeed(feedUrl: string) {
  const articles = await parseFeed(feedUrl);

  for (const article of articles) {
    const content = await scrapeArticle(article.url);
    await saveToSupabase(content);
  }
}
```

**Benefits:**
- ✅ Clean content extraction
- ✅ Markdown format ready for AI
- ✅ Handles paywalls (some cases)
- ✅ Rate limiting built-in

---

### 3. **Browserbase MCP** - Dynamic Content Scraping

**Use Cases:**
- JavaScript-heavy news sites
- Pages requiring interaction
- Screenshot capture for archives
- Anti-scraping bypass

**Integration:**

```typescript
// For JS-heavy sites that Firecrawl can't handle
async function scrapeWithBrowserbase(url: string) {
  const session = await browserbaseMCP.createSession();

  try {
    await browserbaseMCP.navigate(session, url);

    // Wait for content to load
    await browserbaseMCP.waitForSelector(session, 'article');

    // Extract content
    const content = await browserbaseMCP.evaluate(session, `
      document.querySelector('article').innerText
    `);

    // Optional: Take screenshot for archive
    const screenshot = await browserbaseMCP.screenshot(session);

    return { content, screenshot };

  } finally {
    await browserbaseMCP.closeSession(session);
  }
}
```

**Benefits:**
- ✅ Handles complex JS sites
- ✅ AI-powered navigation (Gemini)
- ✅ Screenshot archives
- ✅ Bypasses some anti-scraping

---

### 4. **OpenRouter MCP** - Multi-Model AI Processing

**Use Cases:**
- Article summarization
- Sentiment analysis
- Category classification
- Bulletin generation
- Model comparison

**Integration:**

```typescript
// Summarize article with multiple models
async function summarizeArticle(content: string) {
  // Try GPT-4 first (high quality)
  try {
    const summary = await openRouterMCP.generate({
      model: 'openai/gpt-4-turbo',
      prompt: `Summarize this article in 2-3 sentences:\n\n${content}`,
      maxTokens: 150
    });
    return summary;
  } catch (error) {
    // Fallback to Claude (cheaper)
    return await openRouterMCP.generate({
      model: 'anthropic/claude-3-haiku',
      prompt: `Summarize this article in 2-3 sentences:\n\n${content}`,
      maxTokens: 150
    });
  }
}

// Generate news bulletin from multiple articles
async function generateBulletin(articles: Article[]) {
  const prompt = `
Generate a news bulletin from these articles:

${articles.map((a, i) => `${i + 1}. ${a.title}\n${a.summary}`).join('\n\n')}

Create a coherent 2-3 minute news bulletin script in Slovenian.
`;

  // Use GPT-4 for best quality
  const bulletin = await openRouterMCP.generate({
    model: 'openai/gpt-4-turbo',
    prompt: prompt,
    maxTokens: 1000,
    temperature: 0.7
  });

  return bulletin;
}

// Compare model outputs
async function compareSummaries(content: string) {
  const models = [
    'openai/gpt-4-turbo',
    'anthropic/claude-3-sonnet',
    'google/gemini-pro'
  ];

  const summaries = await Promise.all(
    models.map(model =>
      openRouterMCP.generate({
        model,
        prompt: `Summarize: ${content}`,
        maxTokens: 150
      })
    )
  );

  return summaries;
}
```

**Benefits:**
- ✅ Access to 100+ models
- ✅ Cost optimization (fallback models)
- ✅ Quality comparison
- ✅ Unified API

---

### 5. **ShadCN UI MCP** - Admin Panel Components

**Use Cases:**
- Generate dashboard components
- Create data tables
- Build forms
- UI consistency

**Integration:**

```typescript
// Generate article table component
const articleTable = await shadcnMCP.generate({
  component: 'data-table',
  props: {
    columns: ['title', 'source', 'publishedAt', 'processed'],
    sortable: true,
    filterable: true,
    pagination: true
  }
});

// Generate RSS source form
const rssForm = await shadcnMCP.generate({
  component: 'form',
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'url', type: 'url', required: true },
    { name: 'category', type: 'select', options: ['politics', 'sports', 'tech'] },
    { name: 'active', type: 'checkbox', default: true }
  ]
});

// Generate bulletin editor
const bulletinEditor = await shadcnMCP.generate({
  component: 'rich-text-editor',
  props: {
    placeholder: 'Enter bulletin content...',
    toolbar: ['bold', 'italic', 'list', 'link']
  }
});
```

**Benefits:**
- ✅ Rapid UI development
- ✅ Accessible components
- ✅ Tailwind CSS integration
- ✅ Consistent design system

---

### 6. **Ref MCP** - Documentation Assistant

**Use Cases:**
- API documentation lookup
- Framework best practices
- Code examples
- Troubleshooting

**Integration:**

```typescript
// Look up Supabase Edge Functions docs
const edgeFunctionDocs = await refMCP.search({
  query: 'supabase edge functions deployment',
  library: 'supabase'
});

// Get React hooks documentation
const reactDocs = await refMCP.search({
  query: 'useEffect cleanup',
  library: 'react'
});

// Find OpenRouter API examples
const openRouterDocs = await refMCP.search({
  query: 'openrouter api streaming',
  library: 'openrouter'
});
```

**Benefits:**
- ✅ Quick documentation access
- ✅ Code examples
- ✅ Version-specific docs
- ✅ Official sources only

---

## Gemini File Search Implementation

### Strategy Overview

Create **multiple file search stores** for different purposes:

1. **News Archive Store** - Indexed articles for semantic search
2. **Documentation Store** - Project docs, API references
3. **Source Analysis Store** - RSS feed patterns and trends

---

### 1. News Archive RAG System

**Purpose:** Semantic search across all scraped news articles

**Implementation:**

```python
#!/usr/bin/env python3
"""
TV3 News Archive RAG System
Index and search news articles using Gemini File Search
"""

from google import genai
from google.genai import types
import time
from datetime import datetime


class NewsArchiveRAG:
    def __init__(self, api_key, supabase_client):
        self.client = genai.Client(api_key=api_key)
        self.supabase = supabase_client
        self.store = None

    def initialize_store(self):
        """Create or get news archive store"""
        stores = list(self.client.file_search_stores.list())
        for store in stores:
            if store.display_name == 'tv3-news-archive':
                self.store = store
                print(f"✅ Using existing store: {store.name}")
                return

        self.store = self.client.file_search_stores.create(
            config={'display_name': 'tv3-news-archive'}
        )
        print(f"✅ Created new store: {self.store.name}")

    def index_article(self, article):
        """
        Index a single article

        Args:
            article: Dict with title, content, url, published_at, category
        """
        # Create temporary text file with article content
        content = f"""
Title: {article['title']}
Published: {article['published_at']}
Source: {article['source_name']}
Category: {article['category']}
URL: {article['url']}

{article['content']}
"""

        # Write to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Upload to file search store
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file=temp_path,
                file_search_store_name=self.store.name,
                config={
                    'display_name': f"{article['published_at'][:10]} - {article['title'][:50]}",
                    'chunking_config': {
                        'white_space_config': {
                            'max_tokens_per_chunk': 400,
                            'max_overlap_tokens': 40
                        }
                    }
                },
                custom_metadata=[
                    {"key": "article_id", "string_value": str(article['id'])},
                    {"key": "source", "string_value": article['source_name']},
                    {"key": "category", "string_value": article['category']},
                    {"key": "published_date", "string_value": article['published_at'][:10]},
                    {"key": "url", "string_value": article['url']}
                ]
            )

            # Wait for completion
            while not operation.done:
                time.sleep(2)
                operation = self.client.operations.get(operation)

            print(f"✅ Indexed: {article['title'][:60]}...")
            return True

        finally:
            import os
            os.unlink(temp_path)

    def index_recent_articles(self, days=7):
        """Index recent articles from Supabase"""
        # Fetch recent articles
        result = self.supabase.table('articles').select(
            'id, title, content, url, published_at, category, rss_sources(name)'
        ).gte(
            'published_at',
            f'now() - interval \'{days} days\''
        ).eq(
            'processed', True
        ).execute()

        articles = result.data
        print(f"Found {len(articles)} articles to index")

        indexed = 0
        for article in articles:
            article['source_name'] = article['rss_sources']['name']
            if self.index_article(article):
                indexed += 1
            time.sleep(1)  # Rate limiting

        print(f"\n✅ Indexed {indexed}/{len(articles)} articles")

    def search_articles(self, query, category=None, date_from=None):
        """
        Search articles semantically

        Args:
            query: Search query
            category: Filter by category (optional)
            date_from: Filter by date (optional)
        """
        # Build metadata filter
        filters = []
        if category:
            filters.append(f'category="{category}"')
        if date_from:
            filters.append(f'published_date>="{date_from}"')

        metadata_filter = ' AND '.join(filters) if filters else None

        # Search
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.store.name],
                            metadata_filter=metadata_filter
                        )
                    )
                ]
            )
        )

        return {
            'answer': response.text,
            'citations': self._extract_citations(response)
        }

    def _extract_citations(self, response):
        """Extract article citations"""
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


# Usage example
if __name__ == "__main__":
    from supabase import create_client
    import os

    # Initialize
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    rag = NewsArchiveRAG(
        api_key=os.getenv('GEMINI_API_KEY'),
        supabase_client=supabase
    )

    rag.initialize_store()

    # Index recent articles
    rag.index_recent_articles(days=7)

    # Search examples
    result = rag.search_articles("Kaj se je zgodilo v politiki?", category="politics")
    print(result['answer'])

    result = rag.search_articles("Športne novice o nogometu")
    print(result['answer'])
```

---

### 2. Smart Bulletin Generator with RAG

**Purpose:** Use RAG to find related articles and generate coherent bulletins

```python
#!/usr/bin/env python3
"""
TV3 Smart Bulletin Generator
Uses Gemini File Search to find related articles and generate bulletins
"""

from news_archive_rag import NewsArchiveRAG
from google import genai
from google.genai import types


class SmartBulletinGenerator:
    def __init__(self, api_key, supabase_client):
        self.client = genai.Client(api_key=api_key)
        self.rag = NewsArchiveRAG(api_key, supabase_client)
        self.rag.initialize_store()

    def generate_bulletin(self, topic, duration_minutes=2):
        """
        Generate news bulletin on a specific topic

        Args:
            topic: Topic or theme for the bulletin
            duration_minutes: Target duration in minutes
        """
        # 1. Find relevant articles using RAG
        print(f"🔍 Finding articles about: {topic}")

        search_result = self.rag.search_articles(
            f"Find all news articles about {topic}. Focus on the most important and recent developments."
        )

        # 2. Generate bulletin script
        print("📝 Generating bulletin script...")

        prompt = f"""
Based on the following news information about {topic}:

{search_result['answer']}

Generate a {duration_minutes}-minute news bulletin script in Slovenian that:
1. Has a strong opening
2. Covers the main points logically
3. Includes transitions between topics
4. Has a closing statement
5. Is suitable for TV broadcast

Format the script with clear sections and speaking cues.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",  # Use Pro for better quality
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2000
            )
        )

        bulletin = {
            'topic': topic,
            'script': response.text,
            'sources': search_result['citations'],
            'generated_at': datetime.now().isoformat()
        }

        return bulletin

    def generate_daily_bulletin(self):
        """Generate comprehensive daily bulletin"""
        categories = ['politics', 'economy', 'sports', 'culture']
        bulletin_parts = []

        for category in categories:
            print(f"\n📰 Processing {category}...")

            result = self.rag.search_articles(
                f"What are the most important {category} news today?",
                category=category,
                date_from=datetime.now().strftime('%Y-%m-%d')
            )

            bulletin_parts.append({
                'category': category,
                'content': result['answer'],
                'sources': result['citations']
            })

        # Combine into full bulletin
        combined_content = '\n\n'.join([
            f"## {part['category'].upper()}\n{part['content']}"
            for part in bulletin_parts
        ])

        prompt = f"""
Create a comprehensive 5-minute daily news bulletin in Slovenian from these category summaries:

{combined_content}

The bulletin should:
1. Start with the most important news
2. Flow naturally between categories
3. Be engaging and professional
4. Be exactly 5 minutes when read at normal speed
5. Include opening and closing
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )

        return {
            'type': 'daily_bulletin',
            'script': response.text,
            'categories': categories,
            'parts': bulletin_parts,
            'generated_at': datetime.now().isoformat()
        }


# Usage
if __name__ == "__main__":
    from supabase import create_client
    import os

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    generator = SmartBulletinGenerator(
        api_key=os.getenv('GEMINI_API_KEY'),
        supabase_client=supabase
    )

    # Generate topic-specific bulletin
    bulletin = generator.generate_bulletin("volitve in politika", duration_minutes=3)
    print("\n" + "="*60)
    print("BULLETIN SCRIPT:")
    print("="*60)
    print(bulletin['script'])

    # Generate daily bulletin
    daily = generator.generate_daily_bulletin()
    print("\n" + "="*60)
    print("DAILY BULLETIN:")
    print("="*60)
    print(daily['script'])
```

---

### 3. Article Recommendation Engine

**Purpose:** Suggest related articles for bulletin creation

```python
class ArticleRecommendationEngine:
    def __init__(self, api_key, supabase_client):
        self.rag = NewsArchiveRAG(api_key, supabase_client)
        self.rag.initialize_store()

    def find_related_articles(self, article_id):
        """Find articles related to a given article"""
        # Get original article
        article = self.supabase.table('articles').select('*').eq('id', article_id).single().execute()

        # Use RAG to find similar
        result = self.rag.search_articles(
            f"Find articles similar to this: {article.data['title']}. {article.data['summary']}"
        )

        return result

    def suggest_bulletin_articles(self, theme, count=5):
        """Suggest best articles for a bulletin theme"""
        result = self.rag.search_articles(
            f"Find the {count} most important articles about {theme} that would work well together in a news bulletin"
        )

        return result

    def find_trending_topics(self, days=7):
        """Identify trending topics from recent articles"""
        result = self.rag.search_articles(
            f"What are the main topics and trends in the news from the last {days} days? List the top 5 topics with brief explanations.",
            date_from=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        )

        return result
```

---

## Complete Implementation Guide

### Phase 1: MCP Servers Setup (Week 1)

**1.1 Install all MCP packages**
```bash
# Install globally
npm install -g @supabase/mcp-server-supabase@latest
npm install -g @jpisnice/shadcn-ui-mcp-server@latest
npm install -g @browserbasehq/mcp@latest
npm install -g firecrawl-mcp@latest
npm install -g ref-tools-mcp@latest
npm install -g @mcpservers/openrouterai@latest
```

**1.2 Configure Claude Code MCP**
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "YOUR_TOKEN"]
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {"FIRECRAWL_API_KEY": "YOUR_KEY"}
    },
    "openrouter": {
      "command": "npx",
      "args": ["@mcpservers/openrouterai"],
      "env": {"OPENROUTER_API_KEY": "YOUR_KEY"}
    },
    "browserbase": {
      "command": "npx",
      "args": ["@browserbasehq/mcp"],
      "env": {
        "BROWSERBASE_API_KEY": "YOUR_KEY",
        "GEMINI_API_KEY": "YOUR_KEY"
      }
    },
    "shadcn-ui": {
      "command": "npx",
      "args": ["@jpisnice/shadcn-ui-mcp-server"]
    },
    "ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_KEY"
    }
  }
}
```

**1.3 Test each MCP server**
```bash
# In Claude Code session
claude

# Test Supabase
> Use Supabase MCP to list all tables in TV3 project

# Test Firecrawl
> Use Firecrawl to scrape https://www.24ur.com

# Test OpenRouter
> Use OpenRouter to summarize this text with GPT-4

# Test ShadCN
> Use ShadCN to generate a data table component
```

---

### Phase 2: Gemini File Search Setup (Week 1-2)

**2.1 Install Python dependencies**
```bash
pip install google-genai supabase python-dotenv
```

**2.2 Set up environment variables**
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

**2.3 Create RAG system**
- Copy `news_archive_rag.py` to `tv3-backend/scripts/`
- Copy `smart_bulletin_generator.py` to `tv3-backend/scripts/`
- Test with sample articles

**2.4 Index existing articles**
```bash
python scripts/news_archive_rag.py --index-all
```

---

### Phase 3: Backend Integration (Week 2-3)

**3.1 Article Processing Pipeline**
```typescript
// tv3-backend/functions/process-article/index.ts

import { createClient } from '@supabase/supabase-js';

export async function processArticle(articleId: string) {
  const supabase = createClient(/* ... */);

  // 1. Fetch article
  const { data: article } = await supabase
    .from('articles')
    .select('*')
    .eq('id', articleId)
    .single();

  // 2. Scrape content (Firecrawl or Browserbase)
  let content;
  try {
    content = await scrapeWithFirecrawl(article.url);
  } catch (error) {
    // Fallback to Browserbase for JS-heavy sites
    content = await scrapeWithBrowserbase(article.url);
  }

  // 3. Summarize with OpenRouter
  const summary = await summarizeWithOpenRouter(content);

  // 4. Update in Supabase
  await supabase
    .from('articles')
    .update({
      content: content,
      summary: summary,
      processed: true
    })
    .eq('id', articleId);

  // 5. Index in Gemini File Search (async)
  await indexInGemini(article);

  return { success: true, articleId };
}
```

**3.2 Scheduled Jobs**
```typescript
// Cron job to process RSS feeds every hour
// tv3-backend/functions/cron-fetch-feeds/index.ts

export async function cronFetchFeeds() {
  const supabase = createClient(/* ... */);

  // 1. Get active RSS sources
  const { data: sources } = await supabase
    .from('rss_sources')
    .select('*')
    .eq('active', true);

  for (const source of sources) {
    // 2. Parse RSS feed
    const articles = await parseRSSFeed(source.url);

    for (const article of articles) {
      // 3. Check if already exists
      const existing = await supabase
        .from('articles')
        .select('id')
        .eq('url', article.url)
        .single();

      if (!existing.data) {
        // 4. Insert new article
        const { data: newArticle } = await supabase
          .from('articles')
          .insert({
            source_id: source.id,
            title: article.title,
            url: article.url,
            published_at: article.publishedAt
          })
          .select()
          .single();

        // 5. Trigger processing
        await processArticle(newArticle.id);
      }
    }

    // Update last fetched
    await supabase
      .from('rss_sources')
      .update({ last_fetched: new Date().toISOString() })
      .eq('id', source.id);
  }
}
```

---

### Phase 4: Frontend Integration (Week 3-4)

**4.1 Article Search Component**
```tsx
// tv3-admin/src/components/ArticleSearch.tsx

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export function ArticleSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  async function searchArticles() {
    setLoading(true);

    try {
      const response = await fetch('/api/search-articles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await response.json();
      setResults(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search articles..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button onClick={searchArticles} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </div>

      {results && (
        <div className="space-y-4">
          <h3 className="font-bold">Answer:</h3>
          <p>{results.answer}</p>

          <h3 className="font-bold">Sources:</h3>
          <ul className="space-y-2">
            {results.citations.map((citation, i) => (
              <li key={i} className="border p-2 rounded">
                <strong>{citation.document}</strong>
                <p className="text-sm text-gray-600">{citation.content}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

**4.2 Bulletin Generator UI**
```tsx
// tv3-admin/src/components/BulletinGenerator.tsx

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';

export function BulletinGenerator() {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(2);
  const [bulletin, setBulletin] = useState(null);
  const [generating, setGenerating] = useState(false);

  async function generateBulletin() {
    setGenerating(true);

    try {
      const response = await fetch('/api/generate-bulletin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, duration })
      });

      const data = await response.json();
      setBulletin(data);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Input
          placeholder="Bulletin topic (e.g., 'politics', 'sports')"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />

        <Select
          value={duration}
          onValueChange={setDuration}
        >
          <option value={1}>1 minute</option>
          <option value={2}>2 minutes</option>
          <option value={3}>3 minutes</option>
          <option value={5}>5 minutes</option>
        </Select>

        <Button onClick={generateBulletin} disabled={generating}>
          {generating ? 'Generating...' : 'Generate Bulletin'}
        </Button>
      </div>

      {bulletin && (
        <div className="border p-4 rounded space-y-4">
          <h3 className="font-bold text-xl">Generated Bulletin</h3>

          <Textarea
            value={bulletin.script}
            rows={15}
            className="font-mono"
          />

          <div>
            <h4 className="font-bold">Sources:</h4>
            <ul className="text-sm space-y-1">
              {bulletin.sources.map((source, i) => (
                <li key={i}>• {source.document}</li>
              ))}
            </ul>
          </div>

          <div className="flex gap-2">
            <Button>Save to Database</Button>
            <Button variant="outline">Export</Button>
            <Button variant="outline">Copy to Clipboard</Button>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

### Phase 5: API Endpoints (Week 4)

**5.1 Search Articles Endpoint**
```typescript
// tv3-backend/functions/search-articles/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  const { query, category, dateFrom } = await req.json();

  // Call Python RAG script
  const cmd = `python3 scripts/news_archive_rag.py search "${query}" --category "${category || ''}" --date-from "${dateFrom || ''}"`;

  try {
    const { stdout } = await execAsync(cmd);
    const result = JSON.parse(stdout);

    return new Response(JSON.stringify(result), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});
```

**5.2 Generate Bulletin Endpoint**
```typescript
// tv3-backend/functions/generate-bulletin/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { exec } from 'child_process';
import { promisify } from 'util';
import { createClient } from '@supabase/supabase-js';

const execAsync = promisify(exec);

serve(async (req) => {
  const { topic, duration } = await req.json();

  // Call Python bulletin generator
  const cmd = `python3 scripts/smart_bulletin_generator.py generate "${topic}" --duration ${duration}`;

  try {
    const { stdout } = await execAsync(cmd);
    const bulletin = JSON.parse(stdout);

    // Save to database
    const supabase = createClient(/* ... */);
    const { data } = await supabase
      .from('bulletins')
      .insert({
        title: `${topic} - ${duration}min`,
        content: bulletin.script,
        articles: bulletin.sources.map(s => s.article_id)
      })
      .select()
      .single();

    return new Response(JSON.stringify({ ...bulletin, id: data.id }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500
    });
  }
});
```

---

## Deployment Strategy

### Development Environment
```bash
# Local development
cp .env.example .env
# Fill in API keys

# Start Supabase locally
supabase start

# Start frontend
cd tv3-admin
npm run dev

# Test MCP servers
claude
```

### Staging Environment
```bash
# Deploy Edge Functions
supabase functions deploy process-article
supabase functions deploy search-articles
supabase functions deploy generate-bulletin
supabase functions deploy cron-fetch-feeds

# Set secrets
supabase secrets set GEMINI_API_KEY=...
supabase secrets set OPENROUTER_API_KEY=...
supabase secrets set FIRECRAWL_API_KEY=...
supabase secrets set BROWSERBASE_API_KEY=...

# Deploy frontend
vercel deploy --env staging
```

### Production Environment
```bash
# Database migrations
supabase db push

# Deploy functions
supabase functions deploy --project-ref YOUR_REF

# Deploy frontend
vercel deploy --prod

# Set up cron jobs
supabase functions schedule cron-fetch-feeds --cron "0 * * * *"  # Every hour
```

---

## Cost Estimation

### Monthly Costs (Estimated)

**MCP Services:**
- Supabase: $25/month (Pro plan)
- Firecrawl: $49/month (500 pages → ~1000 articles)
- OpenRouter: ~$20/month (assuming 1000 articles × $0.02 avg)
- Browserbase: $50/month (10 hours → fallback only)
- Ref: Free
- ShadCN: Free

**Gemini File Search:**
- Indexing: ~$2/month (1000 articles × 1000 tokens × $0.15/1M)
- Storage: Free
- Queries: ~$1/month (1000 queries × 500 tokens × $0.000002)

**Total: ~$147/month**

---

## Success Metrics

### Performance
- Article processing time: <30s per article
- Search latency: <2s
- Bulletin generation: <10s

### Quality
- Article extraction accuracy: >95%
- Summary quality: Manual review score >4/5
- Bulletin coherence: Manual review score >4/5

### Cost
- Cost per article processed: <$0.05
- Cost per bulletin generated: <$0.10
- Total monthly cost: <$200

---

## Next Steps

1. **Week 1:** Set up MCP servers and test each one
2. **Week 2:** Implement Gemini File Search RAG system
3. **Week 3:** Integrate backend processing pipeline
4. **Week 4:** Build frontend components
5. **Week 5:** Deploy to staging and test
6. **Week 6:** Deploy to production

---

**Created:** November 2025
**Project:** TV3 AI NewsCaster
**Framework:** SuperClaude v2.0.1

*This integration plan maximizes the use of all 10 MCP servers and Gemini File Search to create a powerful, AI-driven news processing system.*
