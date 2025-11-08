#!/bin/bash
# SuperClaude Deployment Script
# Quick setup and testing deployment

set -e

echo "🚀 SuperClaude Deployment Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}📋 Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r examples/gemini-file-search/requirements.txt
pip install --quiet -r examples/tv3-integration/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}🔧 Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file and add your API keys!${NC}"
    echo -e "${YELLOW}   Required keys:${NC}"
    echo -e "${YELLOW}   - GEMINI_API_KEY (get from: https://makersuite.google.com/app/apikey)${NC}"
    echo -e "${YELLOW}   - SUPABASE_URL and SUPABASE_KEY (optional, for TV3 features)${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi
echo ""

# Check if MCP config exists
if [ ! -f "claude_mcp_config.json" ]; then
    echo -e "${BLUE}🔧 Creating MCP config from template...${NC}"
    cp claude_mcp_config.example.json claude_mcp_config.json
    echo -e "${YELLOW}⚠️  Update claude_mcp_config.json with your API keys if needed${NC}"
else
    echo -e "${GREEN}✅ MCP config already exists${NC}"
fi
echo ""

# Run quick validation
echo -e "${BLUE}🧪 Running validation tests...${NC}"
echo ""

echo -e "${BLUE}Testing SuperClaude RAG...${NC}"
if python3 examples/gemini-file-search/superclaude_rag.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SuperClaude RAG working${NC}"
else
    echo -e "${RED}❌ SuperClaude RAG failed${NC}"
fi

echo -e "${BLUE}Testing Codebase RAG...${NC}"
if python3 examples/gemini-file-search/codebase_rag.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Codebase RAG working${NC}"
else
    echo -e "${RED}❌ Codebase RAG failed${NC}"
fi

echo -e "${BLUE}Testing News Archive RAG...${NC}"
if python3 examples/tv3-integration/news_archive_rag.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ News Archive RAG working${NC}"
else
    echo -e "${RED}❌ News Archive RAG failed${NC}"
fi

echo -e "${BLUE}Testing Bulletin Generator...${NC}"
if python3 examples/tv3-integration/smart_bulletin_generator.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bulletin Generator working${NC}"
else
    echo -e "${RED}❌ Bulletin Generator failed${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📖 Quick Start Guide:${NC}"
echo ""
echo -e "${YELLOW}1. Configure your API keys:${NC}"
echo "   nano .env"
echo ""
echo -e "${YELLOW}2. Test SuperClaude documentation search:${NC}"
echo "   python3 examples/gemini-file-search/superclaude_rag.py --index"
echo "   python3 examples/gemini-file-search/superclaude_rag.py --query \"How do I use MCP servers?\""
echo ""
echo -e "${YELLOW}3. Test codebase analysis:${NC}"
echo "   python3 examples/gemini-file-search/codebase_rag.py --index"
echo "   python3 examples/gemini-file-search/codebase_rag.py --overview"
echo ""
echo -e "${YELLOW}4. Demo mode (no API keys needed):${NC}"
echo "   python3 examples/demo/demo_test.py"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - GEMINI_FILE_SEARCH.md - Complete File Search guide"
echo "   - TV3_INTEGRATION_PLAN.md - TV3 implementation plan"
echo "   - FUNCTIONAL_TEST_REPORT.md - Test results"
echo "   - MCP_SETUP.md - MCP server setup"
echo ""
echo -e "${BLUE}🔗 Get API Keys:${NC}"
echo "   Gemini API: https://makersuite.google.com/app/apikey"
echo "   Supabase: https://supabase.com/dashboard/project/_/settings/api"
echo ""
