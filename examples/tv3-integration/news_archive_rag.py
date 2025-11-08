#!/usr/bin/env python3
"""
TV3 News Archive RAG System
Index and search news articles using Gemini File Search

Usage:
    python news_archive_rag.py --init                    # Initialize store
    python news_archive_rag.py --index-recent --days 7   # Index recent articles
    python news_archive_rag.py --search "politične novice"
    python news_archive_rag.py --search "šport" --category sports
"""

import os
import sys
import time
import argparse
import tempfile
from datetime import datetime, timedelta
from google import genai
from google.genai import types

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase-py not installed")
    print("Install with: pip install supabase")
    sys.exit(1)


class NewsArchiveRAG:
    """RAG system for TV3 news articles"""

    def __init__(self, gemini_api_key=None, supabase_url=None, supabase_key=None):
        """Initialize RAG system with API keys"""
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required")

        self.client = genai.Client(api_key=self.gemini_api_key)
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.store = None

    def initialize_store(self):
        """Create or get existing file search store"""
        print("🔍 Initializing TV3 news archive store...")

        try:
            # Check for existing store
            stores = list(self.client.file_search_stores.list())
            for store in stores:
                if store.display_name == 'tv3-news-archive':
                    self.store = store
                    print(f"✅ Using existing store: {store.name}")
                    return

            # Create new store
            self.store = self.client.file_search_stores.create(
                config={'display_name': 'tv3-news-archive'}
            )
            print(f"✅ Created new store: {self.store.name}")

        except Exception as e:
            print(f"❌ Error initializing store: {e}")
            sys.exit(1)

    def fetch_articles(self, days=7):
        """Fetch recent articles from Supabase"""
        try:
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()

            response = self.supabase.table('articles')\
                .select('id, title, content, url, published_at, category, rss_sources(name)')\
                .gte('published_at', date_threshold)\
                .eq('processed', True)\
                .execute()

            articles = response.data

            # Flatten source name
            for article in articles:
                if article.get('rss_sources'):
                    article['source_name'] = article['rss_sources']['name']
                else:
                    article['source_name'] = 'Unknown'

            print(f"✅ Fetched {len(articles)} articles from Supabase")
            return articles

        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return []

    def index_article(self, article):
        """
        Index a single article in Gemini File Search

        Args:
            article: Dict with id, title, content, url, published_at, category, source_name
        """
        # Prepare article content
        content = f"""Title: {article['title']}
Published: {article['published_at']}
Source: {article['source_name']}
Category: {article.get('category', 'general')}
URL: {article['url']}

{article.get('content', 'No content available')}
"""

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
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
                    {"key": "category", "string_value": article.get('category', 'general')},
                    {"key": "published_date", "string_value": article['published_at'][:10]},
                    {"key": "url", "string_value": article['url']}
                ]
            )

            # Wait for completion
            timeout = 120
            elapsed = 0
            while not operation.done and elapsed < timeout:
                time.sleep(2)
                elapsed += 2
                operation = self.client.operations.get(operation)

            if operation.done:
                return True
            else:
                print(f"  ⏱️  Timeout indexing article")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

        finally:
            os.unlink(temp_path)

    def index_recent_articles(self, days=7):
        """Index recent articles from Supabase"""
        if not self.store:
            print("❌ Store not initialized. Run --init first.")
            return

        articles = self.fetch_articles(days=days)

        if not articles:
            print("No articles to index")
            return

        print(f"\n📚 Indexing {len(articles)} articles...")
        indexed = 0
        failed = 0

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] {article['title'][:60]}...")

            if self.index_article(article):
                indexed += 1
                print(f"  ✅ Indexed")
            else:
                failed += 1

            # Rate limiting
            time.sleep(1)

        print("\n" + "="*60)
        print(f"✅ Indexing complete!")
        print(f"   Success: {indexed}")
        print(f"   Failed: {failed}")
        print("="*60)

    def search_articles(self, query, category=None, date_from=None, model="gemini-2.5-flash"):
        """
        Search articles semantically

        Args:
            query: Search query in natural language
            category: Filter by category (optional)
            date_from: Filter by date YYYY-MM-DD (optional)
            model: Gemini model to use
        """
        if not self.store:
            print("❌ Store not initialized. Run --init first.")
            return None

        # Build metadata filter
        filters = []
        if category:
            filters.append(f'category="{category}"')
        if date_from:
            filters.append(f'published_date>="{date_from}"')

        metadata_filter = ' AND '.join(filters) if filters else None

        print(f"🔍 Searching for: {query}")
        if metadata_filter:
            print(f"   Filters: {metadata_filter}")

        try:
            # Build tool config
            tool_config = types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[self.store.name],
                    metadata_filter=metadata_filter
                )
            )

            # Search
            response = self.client.models.generate_content(
                model=model,
                contents=query,
                config=types.GenerateContentConfig(tools=[tool_config])
            )

            result = {
                'query': query,
                'answer': response.text,
                'citations': self._extract_citations(response)
            }

            return result

        except Exception as e:
            print(f"❌ Search error: {e}")
            return None

    def _extract_citations(self, response):
        """Extract article citations from response"""
        citations = []

        try:
            if response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata

                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        citations.append({
                            'document': chunk.source.document_name,
                            'content': chunk.content[:200]
                        })
        except Exception as e:
            print(f"Warning: Could not extract citations: {e}")

        return citations

    def print_search_results(self, result):
        """Pretty print search results"""
        if not result:
            return

        print("\n" + "="*60)
        print("ODGOVOR:")
        print("="*60)
        print(result['answer'])

        if result['citations']:
            print("\n" + "="*60)
            print("VIRI:")
            print("="*60)
            for i, citation in enumerate(result['citations'], 1):
                print(f"\n[{i}] {citation['document']}")
                print(f"    {citation['content']}...")

        print("\n" + "="*60)


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description='TV3 News Archive RAG System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize the file search store
  python news_archive_rag.py --init

  # Index articles from the last 7 days
  python news_archive_rag.py --index-recent --days 7

  # Search all articles
  python news_archive_rag.py --search "Kaj se dogaja v politiki?"

  # Search with category filter
  python news_archive_rag.py --search "športne novice" --category sports

  # Search with date filter
  python news_archive_rag.py --search "novice" --date-from 2024-11-01
        """
    )

    parser.add_argument('--init', action='store_true',
                        help='Initialize file search store')
    parser.add_argument('--index-recent', action='store_true',
                        help='Index recent articles from Supabase')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to look back (default: 7)')
    parser.add_argument('--search', type=str,
                        help='Search query')
    parser.add_argument('--category', type=str,
                        help='Filter by category')
    parser.add_argument('--date-from', type=str,
                        help='Filter by date (YYYY-MM-DD)')
    parser.add_argument('--model', type=str, default='gemini-2.5-flash',
                        help='Gemini model (default: gemini-2.5-flash)')

    args = parser.parse_args()

    # Check environment
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your-key'")
        sys.exit(1)

    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY not set")
        sys.exit(1)

    # Initialize RAG
    rag = NewsArchiveRAG()

    if args.init or args.index_recent or args.search:
        rag.initialize_store()

    # Execute commands
    if args.index_recent:
        rag.index_recent_articles(days=args.days)

    elif args.search:
        result = rag.search_articles(
            query=args.search,
            category=args.category,
            date_from=args.date_from,
            model=args.model
        )

        if result:
            rag.print_search_results(result)

    elif args.init:
        print("✅ Store initialized successfully")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
