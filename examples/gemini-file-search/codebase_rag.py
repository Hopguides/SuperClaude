#!/usr/bin/env python3
"""
SuperClaude Codebase RAG System
Index and search codebase using Gemini File Search

Usage:
    python codebase_rag.py --index              # Index entire codebase
    python codebase_rag.py --query "How does authentication work?"
    python codebase_rag.py --find-function "handles user login"
"""

import os
import sys
import time
import argparse
from pathlib import Path
from google import genai
from google.genai import types


class CodebaseRAG:
    """RAG system for codebase analysis"""

    # Language detection mapping
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react-typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c-header',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.sh': 'shell',
        '.bash': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.vue': 'vue',
    }

    def __init__(self, api_key=None, store_name='superclaude-codebase'):
        """
        Initialize codebase RAG system

        Args:
            api_key: Gemini API key
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
        print(f"Initializing codebase store: {self.store_name}")

        try:
            stores = list(self.client.file_search_stores.list())
            for store in stores:
                if store.display_name == self.store_name:
                    self.store = store
                    print(f"✅ Using existing store: {store.name}")
                    return

            self.store = self.client.file_search_stores.create(
                config={'display_name': self.store_name}
            )
            print(f"✅ Created new store: {self.store.name}")

        except Exception as e:
            print(f"❌ Error initializing store: {e}")
            sys.exit(1)

    def index_codebase(self, code_path='.', languages=None):
        """
        Index code files

        Args:
            code_path: Path to codebase directory
            languages: List of languages to index (default: all supported)
        """
        code_dir = Path(code_path)

        # Get extensions based on languages
        if languages:
            extensions = [f"*{ext}" for ext, lang in self.LANGUAGE_MAP.items() if lang in languages]
        else:
            extensions = [f"*{ext}" for ext in self.LANGUAGE_MAP.keys()]

        # Directories to skip
        skip_dirs = {
            '.git', '.github', '.vscode', '.idea',
            'node_modules', 'venv', 'env', '__pycache__',
            'dist', 'build', 'target', 'bin', 'obj',
            '.cache', '.pytest_cache', '.mypy_cache'
        }

        indexed_count = 0
        failed_count = 0
        total_size = 0

        print(f"\n🔍 Indexing codebase from: {code_dir.absolute()}")
        print(f"Languages: {', '.join(set(self.LANGUAGE_MAP.values()))}\n")

        for ext in extensions:
            for file_path in code_dir.glob(f"**/{ext}"):
                # Skip excluded directories
                if any(part in skip_dirs or part.startswith('.') for part in file_path.parts):
                    continue

                # Skip very large files (>5MB)
                file_size = file_path.stat().st_size
                if file_size > 5 * 1024 * 1024:
                    print(f"⏭️  Skipping large file: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
                    continue

                # Skip empty files
                if file_size == 0:
                    continue

                try:
                    language = self._detect_language(file_path.suffix)
                    relative_path = file_path.relative_to(code_dir)

                    print(f"📝 {language:15s} | {relative_path} ({file_size / 1024:.1f}KB)")

                    # Upload and import
                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=str(file_path),
                        file_search_store_name=self.store.name,
                        config={
                            'display_name': str(relative_path),
                            'chunking_config': {
                                'white_space_config': {
                                    'max_tokens_per_chunk': 500,  # Larger chunks for code
                                    'max_overlap_tokens': 50
                                }
                            }
                        },
                        custom_metadata=[
                            {"key": "language", "string_value": language},
                            {"key": "file_type", "string_value": file_path.suffix},
                            {"key": "file_name", "string_value": file_path.name},
                            {"key": "file_path", "string_value": str(relative_path)},
                            {"key": "size_bytes", "numeric_value": file_size}
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
                        indexed_count += 1
                        total_size += file_size
                        print(f"   ✅ Indexed\n")
                    else:
                        failed_count += 1
                        print(f"   ⏱️  Timeout\n")

                except Exception as e:
                    failed_count += 1
                    print(f"   ❌ Error: {e}\n")

                # Rate limiting
                time.sleep(1)

        print("\n" + "="*60)
        print(f"✅ Indexing complete!")
        print(f"   Indexed: {indexed_count} files ({total_size / 1024 / 1024:.2f}MB)")
        print(f"   Failed: {failed_count} files")
        print("="*60 + "\n")

    def _detect_language(self, extension):
        """Detect programming language from file extension"""
        return self.LANGUAGE_MAP.get(extension.lower(), 'unknown')

    def query(self, question, model="gemini-2.5-flash", language=None):
        """
        Query the codebase

        Args:
            question: Question about the code
            model: Gemini model to use
            language: Filter by programming language

        Returns:
            dict with 'answer' and 'citations'
        """
        if not self.store:
            return {
                'answer': None,
                'error': 'Store not initialized. Run --index first.'
            }

        try:
            print(f"🔍 Querying: {question}\n")

            # Build tool config
            tool_config = types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[self.store.name]
                )
            )

            # Add language filter if specified
            if language:
                tool_config.file_search.metadata_filter = f'language="{language}"'

            response = self.client.models.generate_content(
                model=model,
                contents=question,
                config=types.GenerateContentConfig(tools=[tool_config])
            )

            answer = response.text
            citations = self._extract_citations(response)

            # Print answer with citations
            print("="*60)
            print("ANSWER:")
            print("="*60)
            print(answer)

            if citations:
                print("\n" + "="*60)
                print("SOURCE FILES:")
                print("="*60)
                for i, citation in enumerate(citations, 1):
                    print(f"\n[{i}] {citation['document']}")
                    if len(citation['content']) > 300:
                        print(f"    {citation['content'][:300]}...")
                    else:
                        print(f"    {citation['content']}")

            print("\n" + "="*60)

            return {'answer': answer, 'citations': citations}

        except Exception as e:
            return {'answer': None, 'error': str(e)}

    def find_function(self, description, language=None):
        """
        Find functions based on description

        Args:
            description: What the function should do
            language: Optional language filter

        Returns:
            dict with answer and citations
        """
        query = f"""
Find code that implements: {description}

Please:
1. Show the function/method definition
2. Explain what it does
3. Show how it's used (if available)
4. Highlight any important details or edge cases
"""
        return self.query(query, language=language)

    def explain_pattern(self, pattern_description, language=None):
        """
        Explain how a design pattern is implemented

        Args:
            pattern_description: Pattern to find
            language: Optional language filter

        Returns:
            dict with answer and citations
        """
        query = f"""
Explain how this pattern/concept is implemented in the codebase: {pattern_description}

Please:
1. Show relevant code examples
2. Explain the implementation approach
3. Note any variations or special cases
4. Identify related code
"""
        return self.query(query, language=language)

    def analyze_dependencies(self, file_or_module):
        """Analyze dependencies for a file or module"""
        query = f"""
Analyze the dependencies for: {file_or_module}

Please:
1. List all imports and dependencies
2. Explain what each dependency is used for
3. Identify any circular dependencies
4. Show the dependency tree if possible
"""
        return self.query(query)

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

    def list_indexed_languages(self):
        """List all programming languages in the indexed codebase"""
        if not self.store:
            print("❌ Store not initialized")
            return

        try:
            print(f"\n💻 Languages in {self.store.display_name}:\n")

            documents = self.client.file_search_stores.list_documents(
                file_search_store_name=self.store.name
            )

            # Count by language
            language_counts = {}
            for doc in documents:
                # Try to extract language from metadata or file extension
                ext = Path(doc.display_name).suffix
                lang = self._detect_language(ext)
                language_counts[lang] = language_counts.get(lang, 0) + 1

            for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {lang:15s} : {count:4d} files")

            print(f"\nTotal: {sum(language_counts.values())} files\n")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='SuperClaude Codebase RAG System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index entire codebase
  python codebase_rag.py --index

  # Index only Python files
  python codebase_rag.py --index --language python

  # Query the codebase
  python codebase_rag.py --query "How does authentication work?"

  # Find a specific function
  python codebase_rag.py --find-function "handles user login"

  # Explain a pattern (in Python only)
  python codebase_rag.py --explain-pattern "dependency injection" --language python

  # Analyze dependencies
  python codebase_rag.py --analyze-deps "src/auth/login.py"

  # List indexed languages
  python codebase_rag.py --list-languages
        """
    )

    parser.add_argument('--index', action='store_true',
                        help='Index the codebase')
    parser.add_argument('--query', type=str,
                        help='Query the codebase')
    parser.add_argument('--find-function', type=str,
                        help='Find functions by description')
    parser.add_argument('--explain-pattern', type=str,
                        help='Explain how a pattern is implemented')
    parser.add_argument('--analyze-deps', type=str,
                        help='Analyze dependencies for a file/module')
    parser.add_argument('--list-languages', action='store_true',
                        help='List all indexed programming languages')
    parser.add_argument('--language', type=str,
                        help='Filter by programming language')
    parser.add_argument('--code-path', type=str, default='.',
                        help='Path to codebase directory (default: .)')
    parser.add_argument('--store-name', type=str, default='superclaude-codebase',
                        help='File search store name (default: superclaude-codebase)')
    parser.add_argument('--model', type=str, default='gemini-2.5-flash',
                        help='Gemini model to use (default: gemini-2.5-flash)')

    args = parser.parse_args()

    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize RAG system
    rag = CodebaseRAG(store_name=args.store_name)
    rag.initialize_store()

    # Execute commands
    if args.index:
        languages = [args.language] if args.language else None
        rag.index_codebase(code_path=args.code_path, languages=languages)

    elif args.query:
        result = rag.query(args.query, model=args.model, language=args.language)
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            sys.exit(1)

    elif args.find_function:
        result = rag.find_function(args.find_function, language=args.language)
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            sys.exit(1)

    elif args.explain_pattern:
        result = rag.explain_pattern(args.explain_pattern, language=args.language)
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            sys.exit(1)

    elif args.analyze_deps:
        result = rag.analyze_dependencies(args.analyze_deps)
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            sys.exit(1)

    elif args.list_languages:
        rag.list_indexed_languages()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
