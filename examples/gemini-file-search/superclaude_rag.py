#!/usr/bin/env python3
"""
SuperClaude Documentation RAG System
Index and search SuperClaude documentation using Gemini File Search

Usage:
    python superclaude_rag.py --index     # Index all documentation
    python superclaude_rag.py --query "How do I use personas?"
"""

import os
import sys
import time
import argparse
from pathlib import Path
from google import genai
from google.genai import types


class SuperClaudeRAG:
    """RAG system for SuperClaude documentation"""

    def __init__(self, api_key=None, store_name='superclaude-docs'):
        """
        Initialize RAG system

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            store_name: Name for the file search store
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        self.client = genai.Client(api_key=self.api_key)
        self.store_name = store_name
        self.store = None

    def initialize_store(self):
        """Create or get existing file search store"""
        print(f"Initializing file search store: {self.store_name}")

        try:
            # Check if store already exists
            stores = list(self.client.file_search_stores.list())
            for store in stores:
                if store.display_name == self.store_name:
                    self.store = store
                    print(f"✅ Using existing store: {store.name}")
                    return

            # Create new store
            self.store = self.client.file_search_stores.create(
                config={'display_name': self.store_name}
            )
            print(f"✅ Created new store: {self.store.name}")

        except Exception as e:
            print(f"❌ Error initializing store: {e}")
            sys.exit(1)

    def index_documentation(self, docs_path='.', extensions=None):
        """
        Index all documentation files

        Args:
            docs_path: Path to documentation directory
            extensions: List of file extensions to index (default: md, txt, rst, yml)
        """
        if extensions is None:
            extensions = ['*.md', '*.txt', '*.rst', '*.yml', '*.yaml']

        docs_dir = Path(docs_path)
        indexed_count = 0
        failed_count = 0

        print(f"\nIndexing documentation from: {docs_dir.absolute()}")
        print(f"Extensions: {', '.join(extensions)}\n")

        for ext in extensions:
            for file_path in docs_dir.glob(f"**/{ext}"):
                # Skip hidden directories and build artifacts
                skip_dirs = {'.git', '.github', 'node_modules', 'venv', '__pycache__', 'dist', 'build'}
                if any(part in skip_dirs or part.startswith('.') for part in file_path.parts):
                    continue

                # Skip very large files (>10MB)
                file_size = file_path.stat().st_size
                if file_size > 10 * 1024 * 1024:
                    print(f"⏭️  Skipping large file: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
                    continue

                try:
                    print(f"📄 Indexing: {file_path.name} ({file_size / 1024:.1f}KB)")

                    # Upload and import
                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=str(file_path),
                        file_search_store_name=self.store.name,
                        config={
                            'display_name': str(file_path.relative_to(docs_dir)),
                            'chunking_config': {
                                'white_space_config': {
                                    'max_tokens_per_chunk': 400,
                                    'max_overlap_tokens': 40
                                }
                            }
                        },
                        custom_metadata=[
                            {"key": "file_type", "string_value": file_path.suffix},
                            {"key": "file_name", "string_value": file_path.name},
                            {"key": "file_path", "string_value": str(file_path.relative_to(docs_dir))}
                        ]
                    )

                    # Wait for completion with timeout
                    timeout = 120  # 2 minutes
                    elapsed = 0
                    while not operation.done and elapsed < timeout:
                        time.sleep(2)
                        elapsed += 2
                        operation = self.client.operations.get(operation)

                    if operation.done:
                        indexed_count += 1
                        print(f"   ✅ Indexed successfully\n")
                    else:
                        failed_count += 1
                        print(f"   ⏱️  Timeout - file may be too complex\n")

                except Exception as e:
                    failed_count += 1
                    print(f"   ❌ Error: {e}\n")

                # Rate limiting - wait between uploads
                time.sleep(1)

        print("\n" + "="*60)
        print(f"✅ Indexing complete!")
        print(f"   Indexed: {indexed_count} files")
        print(f"   Failed: {failed_count} files")
        print("="*60 + "\n")

    def query(self, question, model="gemini-2.5-flash", verbose=False):
        """
        Query the documentation

        Args:
            question: Question to ask
            model: Gemini model to use
            verbose: Show detailed output including citations

        Returns:
            dict with 'answer', 'citations', and optional 'error'
        """
        if not self.store:
            return {
                'answer': None,
                'error': 'File search store not initialized. Run --index first.'
            }

        try:
            print(f"🔍 Querying: {question}\n")

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

            answer = response.text
            citations = self._extract_citations(response)

            if verbose:
                print("="*60)
                print("ANSWER:")
                print("="*60)
                print(answer)

                if citations:
                    print("\n" + "="*60)
                    print("SOURCES:")
                    print("="*60)
                    for i, citation in enumerate(citations, 1):
                        print(f"\n[{i}] {citation['document']}")
                        print(f"    {citation['content'][:150]}...")

                print("\n" + "="*60)

            return {
                'answer': answer,
                'citations': citations
            }

        except Exception as e:
            return {
                'answer': None,
                'error': str(e)
            }

    def _extract_citations(self, response):
        """Extract citations from response"""
        citations = []

        try:
            if response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata

                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        citations.append({
                            'document': chunk.source.document_name,
                            'content': chunk.content
                        })
        except Exception as e:
            print(f"Warning: Could not extract citations: {e}")

        return citations

    def list_documents(self):
        """List all documents in the store"""
        if not self.store:
            print("❌ Store not initialized")
            return

        try:
            print(f"\n📚 Documents in {self.store.display_name}:\n")

            documents = self.client.file_search_stores.list_documents(
                file_search_store_name=self.store.name
            )

            count = 0
            for doc in documents:
                count += 1
                size_kb = doc.size_bytes / 1024 if hasattr(doc, 'size_bytes') else 0
                print(f"{count}. {doc.display_name} ({size_kb:.1f}KB)")

            print(f"\nTotal: {count} documents\n")

        except Exception as e:
            print(f"❌ Error listing documents: {e}")

    def delete_store(self):
        """Delete the file search store"""
        if not self.store:
            print("❌ Store not initialized")
            return

        try:
            confirm = input(f"⚠️  Delete store '{self.store.display_name}'? (yes/no): ")
            if confirm.lower() == 'yes':
                self.client.file_search_stores.delete(
                    name=self.store.name,
                    config={'force': True}
                )
                print(f"✅ Store deleted: {self.store.name}")
            else:
                print("❌ Deletion cancelled")

        except Exception as e:
            print(f"❌ Error deleting store: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='SuperClaude Documentation RAG System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index all documentation
  python superclaude_rag.py --index

  # Query the documentation
  python superclaude_rag.py --query "How do I use personas?"

  # Query with verbose output (shows citations)
  python superclaude_rag.py --query "What are MCP servers?" --verbose

  # List indexed documents
  python superclaude_rag.py --list

  # Delete the store
  python superclaude_rag.py --delete
        """
    )

    parser.add_argument('--index', action='store_true',
                        help='Index all documentation files')
    parser.add_argument('--query', type=str,
                        help='Query the documentation')
    parser.add_argument('--list', action='store_true',
                        help='List all indexed documents')
    parser.add_argument('--delete', action='store_true',
                        help='Delete the file search store')
    parser.add_argument('--store-name', type=str, default='superclaude-docs',
                        help='File search store name (default: superclaude-docs)')
    parser.add_argument('--docs-path', type=str, default='.',
                        help='Path to documentation directory (default: .)')
    parser.add_argument('--model', type=str, default='gemini-2.5-flash',
                        help='Gemini model to use (default: gemini-2.5-flash)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output including citations')

    args = parser.parse_args()

    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Initialize RAG system
    rag = SuperClaudeRAG(store_name=args.store_name)
    rag.initialize_store()

    # Execute commands
    if args.index:
        rag.index_documentation(docs_path=args.docs_path)

    elif args.query:
        result = rag.query(args.query, model=args.model, verbose=args.verbose)

        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        elif not args.verbose:
            # If not verbose, just print the answer
            print(result['answer'])

    elif args.list:
        rag.list_documents()

    elif args.delete:
        rag.delete_store()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
