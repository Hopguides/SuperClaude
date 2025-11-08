# SuperClaude Demo Mode

Test SuperClaude functionality without requiring API keys!

## Quick Start

```bash
python3 examples/demo/demo_test.py
```

## What This Does

The demo test script verifies all SuperClaude components:

### ✅ Verification Tests

1. **SuperClaude Documentation RAG**
   - Module import verification
   - Class structure validation
   - CLI interface check
   - Demo query simulation

2. **Codebase Analysis RAG**
   - Module import verification
   - Language support check (29 languages)
   - Method structure validation
   - Demo code search simulation

3. **TV3 News Archive RAG**
   - Module import verification
   - Supabase integration check
   - Metadata filtering verification
   - Demo news search simulation

4. **Smart Bulletin Generator**
   - Module import verification
   - Bulletin type validation
   - Slovenian language demo
   - Professional TV format display

5. **Project File Structure**
   - Documentation files check
   - Python scripts validation
   - File size reporting

6. **MCP Server Configuration**
   - All 6 MCP servers listed
   - Configuration verification
   - Setup instructions

7. **Documentation Statistics**
   - Line count for all docs
   - Code metrics summary
   - Visual statistics display

## Features

### No API Keys Required

This demo runs completely offline and doesn't require:
- ❌ Gemini API key
- ❌ Supabase credentials
- ❌ Any MCP server keys

### What It Tests

✅ **Module Imports** - Verifies all Python modules can be imported
✅ **Class Structure** - Checks all required methods exist
✅ **File Structure** - Validates all documentation and code files
✅ **CLI Interfaces** - Tests command-line help systems
✅ **Configuration** - Verifies MCP and environment setup

### Simulated Demonstrations

The script includes realistic simulations of:

- 📖 Documentation search results
- 🔍 Code analysis queries
- 📰 News article searches
- 📺 TV bulletin generation (in Slovenian!)

## Example Output

```
============================================================
                SuperClaude Demo Test Suite
============================================================

1. SuperClaude Documentation RAG
--------------------------------
ℹ️  Testing module import...
✅ Module imported successfully
✅ Method '__init__' exists
✅ Method 'initialize_store' exists
✅ Method 'index_documentation' exists
✅ Method 'query' exists
✅ CLI help system available

Demo query simulation:
   Query: 'How do I use MCP servers?'
   Answer: MCP servers are configured in claude_mcp_config.json...
   Citations: MCP_SETUP.md, CLAUDE.md

...

============================================================
                        Test Summary
============================================================

✅ ALL TESTS PASSED: 7/7 (100%)

============================================================
                         Next Steps
============================================================

To use with real API keys:

1. Get Gemini API key:
   Visit: https://makersuite.google.com/app/apikey
   Add to .env: GEMINI_API_KEY=your_key_here

2. Test SuperClaude documentation search:
   python3 examples/gemini-file-search/superclaude_rag.py --index
   python3 examples/gemini-file-search/superclaude_rag.py --query "How do I use personas?"

...
```

## Perfect For

### Testing Installation
Verify your SuperClaude installation is complete and working correctly.

### Understanding Structure
See how all components fit together before diving into the code.

### Demo Presentations
Show SuperClaude capabilities without needing API keys or internet connection.

### Troubleshooting
Quickly identify if there are any missing dependencies or files.

### Learning
Understand what each component does through simulated examples.

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

Use in CI/CD:
```bash
if python3 examples/demo/demo_test.py; then
    echo "SuperClaude ready!"
else
    echo "SuperClaude has issues"
    exit 1
fi
```

## What's Next?

After running the demo:

1. **Get API keys** - See instructions in the demo output
2. **Read QUICK_START.md** - Complete setup guide
3. **Index documentation** - Try real queries
4. **Explore features** - Test with your own data

## Customization

You can modify `demo_test.py` to:
- Add more simulated examples
- Change output colors
- Add custom validation tests
- Create specific demo scenarios

## Files

- `demo_test.py` - Main demo test script (584 lines)
- `README.md` - This file

## Requirements

Only requires Python 3 standard library for basic tests. The actual imports test that dependencies are installed but doesn't require API keys.

## Support

See the main documentation:
- `QUICK_START.md` - Quick setup guide
- `GEMINI_FILE_SEARCH.md` - File Search documentation
- `TV3_INTEGRATION_PLAN.md` - TV3 integration guide
- `FUNCTIONAL_TEST_REPORT.md` - Test results

---

**Run the demo now:**
```bash
python3 examples/demo/demo_test.py
```
