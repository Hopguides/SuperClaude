#!/usr/bin/env python3
"""
TV3 Smart Bulletin Generator
Generate AI-powered news bulletins using Gemini File Search RAG

Usage:
    python smart_bulletin_generator.py --topic "politika" --duration 2
    python smart_bulletin_generator.py --daily
    python smart_bulletin_generator.py --trending
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# Import our RAG system
from news_archive_rag import NewsArchiveRAG


class SmartBulletinGenerator:
    """Generate news bulletins using RAG and AI"""

    def __init__(self, gemini_api_key=None, supabase_url=None, supabase_key=None):
        """Initialize bulletin generator"""
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.gemini_api_key)

        # Initialize RAG system
        self.rag = NewsArchiveRAG(
            gemini_api_key=gemini_api_key,
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
        self.rag.initialize_store()

    def generate_topic_bulletin(self, topic, duration_minutes=2, language='slovenian'):
        """
        Generate bulletin on a specific topic

        Args:
            topic: Topic or theme for the bulletin
            duration_minutes: Target duration in minutes (1-10)
            language: Output language (default: slovenian)

        Returns:
            dict with script, sources, metadata
        """
        print(f"\n📰 Generating {duration_minutes}-minute bulletin on: {topic}")

        # 1. Find relevant articles using RAG
        print("🔍 Finding relevant articles...")

        search_query = f"""
Find all recent news articles about {topic}.
Focus on the most important and newsworthy developments.
Summarize the key points and main stories.
"""

        search_result = self.rag.search_articles(search_query)

        if not search_result:
            print("❌ No articles found")
            return None

        # 2. Generate bulletin script
        print("📝 Generating bulletin script...")

        # Calculate approximate word count (150 words per minute in Slovenian)
        target_words = duration_minutes * 150

        prompt = f"""
You are a professional TV news anchor for TV3 Slovenia.

Based on the following news information about {topic}:

{search_result['answer']}

Generate a {duration_minutes}-minute news bulletin script in {language} that:

1. **Opening** (10 seconds)
   - Strong, attention-grabbing opening
   - Brief overview of what's coming

2. **Main Content** ({duration_minutes - 0.5} minutes)
   - Cover the main points logically
   - Clear transitions between stories
   - Use journalistic, professional language
   - Include relevant facts and context
   - Maintain neutral, objective tone

3. **Closing** (10 seconds)
   - Brief summary
   - Professional sign-off

**Format Requirements:**
- Write in natural, spoken language
- Target approximately {target_words} words
- Use short, clear sentences
- Include speaker cues in [brackets] where helpful
- Structure with clear sections

**Language:** {language}
**Tone:** Professional, neutral, engaging
**Target Duration:** {duration_minutes} minutes when read at normal speaking pace

Generate the complete bulletin script now:
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",  # Use Pro for best quality
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2000
            )
        )

        bulletin = {
            'topic': topic,
            'duration_minutes': duration_minutes,
            'language': language,
            'script': response.text,
            'sources': search_result['citations'],
            'generated_at': datetime.now().isoformat(),
            'word_count': len(response.text.split())
        }

        print(f"✅ Generated bulletin ({bulletin['word_count']} words)")

        return bulletin

    def generate_daily_bulletin(self, duration_minutes=5):
        """
        Generate comprehensive daily news bulletin

        Args:
            duration_minutes: Target duration (default: 5 minutes)

        Returns:
            dict with complete daily bulletin
        """
        print(f"\n📺 Generating {duration_minutes}-minute daily bulletin...")

        categories = {
            'politics': 'politika',
            'economy': 'gospodarstvo',
            'sports': 'šport',
            'culture': 'kultura'
        }

        bulletin_parts = []

        # Search each category
        for cat_key, cat_name in categories.items():
            print(f"\n📂 Processing {cat_name}...")

            result = self.rag.search_articles(
                f"Kakšne so najpomembnejše {cat_name} novice danes? Povzemi glavne zgodbe.",
                category=cat_key,
                date_from=datetime.now().strftime('%Y-%m-%d')
            )

            if result:
                bulletin_parts.append({
                    'category': cat_name,
                    'content': result['answer'],
                    'sources': result['citations']
                })

        # Combine into full bulletin
        print("\n🎬 Creating complete bulletin...")

        combined_content = '\n\n'.join([
            f"## {part['category'].upper()}\n{part['content']}"
            for part in bulletin_parts
        ])

        target_words = duration_minutes * 150

        prompt = f"""
You are a professional TV news anchor for TV3 Slovenia.

Create a comprehensive {duration_minutes}-minute daily news bulletin in Slovenian from these category summaries:

{combined_content}

The bulletin should:

1. **Opening** (20 seconds)
   - "Dober večer, dobrodošli na TV3"
   - Brief overview of top stories across all categories

2. **Main Stories** ({duration_minutes - 1} minutes)
   - Start with the most important news (usually politics or breaking news)
   - Flow naturally between categories
   - Give appropriate weight to each category based on importance
   - Use smooth transitions
   - Maintain engaging pace

3. **Closing** (20 seconds)
   - Brief recap of key points
   - Professional sign-off
   - "Hvala za vašo pozornost. Lep večer!"

**Format:**
- Approximately {target_words} words total
- Natural, spoken Slovenian
- Professional news anchor style
- Clear section breaks
- [Speaker cues] where helpful

Generate the complete daily bulletin script:
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=3000
            )
        )

        daily_bulletin = {
            'type': 'daily_bulletin',
            'duration_minutes': duration_minutes,
            'categories': list(categories.values()),
            'script': response.text,
            'parts': bulletin_parts,
            'generated_at': datetime.now().isoformat(),
            'word_count': len(response.text.split())
        }

        print(f"✅ Generated daily bulletin ({daily_bulletin['word_count']} words)")

        return daily_bulletin

    def find_trending_topics(self, days=7, top_n=5):
        """
        Identify trending topics from recent news

        Args:
            days: Look back this many days
            top_n: Return top N topics

        Returns:
            dict with trending topics
        """
        print(f"\n📊 Finding trending topics from last {days} days...")

        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        result = self.rag.search_articles(
            f"""
Analyze all news articles from the last {days} days.

Identify the top {top_n} trending topics or themes that appear most frequently.

For each topic:
1. Name of the topic/theme
2. Brief description (2-3 sentences)
3. Why it's trending
4. Key developments

Format as a numbered list in Slovenian.
""",
            date_from=date_from,
            model="gemini-2.5-pro"
        )

        if not result:
            print("❌ No trends found")
            return None

        trending = {
            'period_days': days,
            'top_n': top_n,
            'analysis': result['answer'],
            'sources': result['citations'],
            'analyzed_at': datetime.now().isoformat()
        }

        return trending

    def suggest_bulletin_topics(self, count=5):
        """
        Suggest bulletin topics based on recent news

        Args:
            count: Number of suggestions

        Returns:
            list of suggested topics
        """
        print(f"\n💡 Suggesting {count} bulletin topics...")

        result = self.rag.search_articles(
            f"""
Based on all recent news articles, suggest {count} compelling topics for news bulletins.

For each topic:
1. Topic title
2. Why it's newsworthy
3. Key angles to cover
4. Estimated importance (1-5 scale)

Choose topics that:
- Have enough recent coverage
- Are newsworthy and engaging
- Would work well as standalone bulletins
- Cover different areas (politics, economy, sports, etc.)

Format as a numbered list in Slovenian.
""",
            model="gemini-2.5-pro"
        )

        if not result:
            return None

        suggestions = {
            'count': count,
            'suggestions': result['answer'],
            'generated_at': datetime.now().isoformat()
        }

        return suggestions

    def save_bulletin(self, bulletin, filename=None):
        """Save bulletin to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            topic_slug = bulletin.get('topic', 'daily').replace(' ', '_')[:30]
            filename = f"bulletin_{topic_slug}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(bulletin, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved to: {filename}")

    def print_bulletin(self, bulletin):
        """Pretty print bulletin"""
        print("\n" + "="*80)
        print("TV3 NEWS BULLETIN")
        print("="*80)

        if bulletin.get('topic'):
            print(f"\nTopic: {bulletin['topic']}")
        if bulletin.get('type'):
            print(f"Type: {bulletin['type']}")

        print(f"Duration: {bulletin.get('duration_minutes', 'N/A')} minutes")
        print(f"Word Count: {bulletin.get('word_count', 'N/A')} words")
        print(f"Generated: {bulletin.get('generated_at', 'N/A')}")

        print("\n" + "-"*80)
        print("SCRIPT:")
        print("-"*80)
        print(bulletin['script'])

        if bulletin.get('sources'):
            print("\n" + "-"*80)
            print("SOURCES:")
            print("-"*80)
            for i, source in enumerate(bulletin['sources'], 1):
                print(f"\n[{i}] {source['document']}")

        print("\n" + "="*80)


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description='TV3 Smart Bulletin Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate bulletin on specific topic
  python smart_bulletin_generator.py --topic "politika" --duration 2

  # Generate daily bulletin
  python smart_bulletin_generator.py --daily --duration 5

  # Find trending topics
  python smart_bulletin_generator.py --trending --days 7

  # Get bulletin topic suggestions
  python smart_bulletin_generator.py --suggest-topics

  # Save bulletin to file
  python smart_bulletin_generator.py --topic "gospodarstvo" --save
        """
    )

    parser.add_argument('--topic', type=str,
                        help='Generate bulletin on specific topic')
    parser.add_argument('--duration', type=int, default=2,
                        help='Bulletin duration in minutes (default: 2)')
    parser.add_argument('--daily', action='store_true',
                        help='Generate comprehensive daily bulletin')
    parser.add_argument('--trending', action='store_true',
                        help='Find trending topics')
    parser.add_argument('--days', type=int, default=7,
                        help='Days to analyze for trending (default: 7)')
    parser.add_argument('--suggest-topics', action='store_true',
                        help='Suggest bulletin topics')
    parser.add_argument('--save', action='store_true',
                        help='Save bulletin to JSON file')
    parser.add_argument('--language', type=str, default='slovenian',
                        help='Output language (default: slovenian)')

    args = parser.parse_args()

    # Check environment
    required_vars = ['GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"❌ Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    # Initialize generator
    generator = SmartBulletinGenerator()

    # Execute commands
    bulletin = None

    if args.topic:
        bulletin = generator.generate_topic_bulletin(
            topic=args.topic,
            duration_minutes=args.duration,
            language=args.language
        )

    elif args.daily:
        bulletin = generator.generate_daily_bulletin(
            duration_minutes=args.duration
        )

    elif args.trending:
        trending = generator.find_trending_topics(days=args.days)
        if trending:
            print("\n" + "="*60)
            print("TRENDING TOPICS:")
            print("="*60)
            print(trending['analysis'])
            print("\n" + "="*60)

    elif args.suggest_topics:
        suggestions = generator.suggest_bulletin_topics()
        if suggestions:
            print("\n" + "="*60)
            print("BULLETIN TOPIC SUGGESTIONS:")
            print("="*60)
            print(suggestions['suggestions'])
            print("\n" + "="*60)

    else:
        parser.print_help()
        sys.exit(0)

    # Print and save bulletin
    if bulletin:
        generator.print_bulletin(bulletin)

        if args.save:
            generator.save_bulletin(bulletin)


if __name__ == "__main__":
    main()
