# MCP Servers Setup Guide

**SuperClaude MCP Integration**
**Version:** 2.0.1
**Last Updated:** November 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [MCP Servers List](#mcp-servers-list)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [API Keys Management](#api-keys-management)

---

## Overview

SuperClaude supports 10 MCP (Model Context Protocol) servers for enhanced capabilities:

**Core Servers (Included in v1.x):**
- **Context7** - Library documentation and code examples
- **Sequential** - Multi-step problem solving and analysis
- **Magic** - UI component generation
- **Puppeteer** - Browser automation and E2E testing

**Extended Servers (New in v2.0.1):**
- **Ref** - API documentation assistant
- **Supabase** - Database management
- **ShadCN UI** - React component library
- **Firecrawl** - Web scraping and content extraction
- **OpenRouter** - Access to 100+ AI models
- **Browserbase** - AI-powered browser automation

---

## Prerequisites

### System Requirements

```bash
# Node.js v18 or higher
node --version

# npm or pnpm
npm --version
# or
pnpm --version

# Claude Code CLI
claude --version
```

### Install pnpm (Recommended)

```bash
npm install -g pnpm@latest
```

---

## MCP Servers List

### 1. Ref - API Documentation Assistant

**Purpose:** Access documentation for APIs, libraries, and frameworks
**Package:** `ref-tools-mcp@latest`
**Type:** HTTP-based MCP server
**API Key Required:** Yes
**Get API Key:** https://ref.tools

**Capabilities:**
- Search documentation for programming languages
- Get API reference for libraries
- Find code examples and best practices
- Version-specific documentation

**Use Cases:**
- API integration
- Framework patterns
- Library adoption
- Best practices research

### 2. Supabase - Database Management

**Purpose:** Direct interaction with Supabase projects
**Package:** `@supabase/mcp-server-supabase@latest`
**Type:** NPM package MCP server
**API Key Required:** Yes (Access Token)
**Get API Key:** https://supabase.com/dashboard/account/tokens

**Capabilities:**
- Execute SQL queries
- List tables and schemas
- Check Edge Functions status
- Manage Supabase projects

**Use Cases:**
- Database queries
- Schema management
- Edge Functions monitoring
- Real-time development

### 3. ShadCN UI - Component Generator

**Purpose:** Generate and search ShadCN UI components
**Package:** `@jpisnice/shadcn-ui-mcp-server@latest`
**Type:** NPM package MCP server
**API Key Required:** No
**Dependencies:** Tailwind CSS, React

**Capabilities:**
- List available ShadCN components
- Generate component code
- Get component documentation
- Find component examples

**Use Cases:**
- React UI development
- Design systems
- Rapid prototyping
- Accessible components

### 4. Firecrawl - Web Scraping

**Purpose:** Scrape and extract content from websites
**Package:** `firecrawl-mcp@latest`
**Type:** NPM package MCP server
**API Key Required:** Yes
**Get API Key:** https://firecrawl.dev

**Capabilities:**
- Scrape web pages
- Extract structured data
- Convert HTML to Markdown
- Handle JavaScript-rendered pages

**Use Cases:**
- Content extraction
- Web scraping
- Data aggregation
- Article parsing

### 5. OpenRouter - AI Models Access

**Purpose:** Access 100+ AI models through unified API
**Package:** `@mcpservers/openrouterai@latest`
**Type:** NPM package MCP server
**API Key Required:** Yes
**Get API Key:** https://openrouter.ai/keys

**Available Models:**
- OpenAI: GPT-4, GPT-3.5
- Anthropic: Claude (all versions)
- Google: Gemini
- Meta: Llama
- Mistral AI
- 100+ more models

**Capabilities:**
- Send prompts to multiple AI models
- Compare model responses
- Get model pricing info
- Stream responses

**Use Cases:**
- AI-powered features
- Content generation
- Model experimentation
- Multi-model comparison

### 6. Browserbase - Browser Automation

**Purpose:** Automated browser sessions with AI assistance
**Package:** `@browserbasehq/mcp@latest`
**Type:** NPM package MCP server
**API Key Required:** Yes (+ Gemini API)
**Get API Keys:**
- Browserbase: https://browserbase.com
- Gemini: https://makersuite.google.com/app/apikey

**Capabilities:**
- Launch headless browsers
- Navigate web pages
- Extract JavaScript-rendered content
- Take screenshots
- Execute browser actions

**Use Cases:**
- Dynamic content extraction
- Browser automation
- Visual testing
- JavaScript-heavy sites

---

## Installation

### 1. Install MCP Server Packages

```bash
# Install all MCP servers globally
npm install -g @supabase/mcp-server-supabase@latest
npm install -g @jpisnice/shadcn-ui-mcp-server@latest
npm install -g @browserbasehq/mcp@latest
npm install -g firecrawl-mcp@latest
npm install -g ref-tools-mcp@latest
npm install -g @mcpservers/openrouterai@latest
```

### 2. Verify Installation

```bash
# Check if packages are installed
npm list -g --depth=0 | grep -E "mcp|supabase|shadcn|browserbase|firecrawl|ref-tools|openrouter"
```

---

## Configuration

### 1. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or your preferred editor
```

### 2. Create MCP Configuration File

```bash
# Copy the example configuration
cp claude_mcp_config.example.json claude_mcp_config.json

# Edit and add your API keys
nano claude_mcp_config.json
```

**Important:** The `claude_mcp_config.json` file should be in your Claude Code configuration directory, typically:
- Linux/macOS: `~/.config/claude/`
- Windows: `%APPDATA%\claude\`

### 3. Configuration File Structure

```json
{
  "mcpServers": {
    "ref": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=YOUR_API_KEY"
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "YOUR_TOKEN"]
    },
    "shadcn-ui": {
      "command": "npx",
      "args": ["@jpisnice/shadcn-ui-mcp-server"]
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR_API_KEY"
      }
    },
    "openrouter": {
      "command": "npx",
      "args": ["@mcpservers/openrouterai"],
      "env": {
        "OPENROUTER_API_KEY": "YOUR_API_KEY"
      }
    },
    "browserbase": {
      "command": "npx",
      "args": ["@browserbasehq/mcp"],
      "env": {
        "BROWSERBASE_API_KEY": "YOUR_BROWSERBASE_KEY",
        "GEMINI_API_KEY": "YOUR_GEMINI_KEY"
      }
    }
  }
}
```

---

## Testing

### Start Claude Code with MCP Support

```bash
# Start Claude Code
claude

# Or with specific model
claude --model claude-sonnet-4-5-20250929
```

### Test Each Server

#### Test Ref
```
Prompt: "Use Ref to get documentation for React useState hook"
```

#### Test Supabase
```
Prompt: "Use Supabase MCP to list all tables in my project"
```

#### Test ShadCN UI
```
Prompt: "Use ShadCN to show available button components"
```

#### Test Firecrawl
```
Prompt: "Use Firecrawl to scrape https://example.com and extract the title"
```

#### Test OpenRouter
```
Prompt: "Use OpenRouter to list available AI models"
```

#### Test Browserbase
```
Prompt: "Use Browserbase to open https://example.com and take a screenshot"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: MCP Server Not Found

**Symptom:** Claude Code says MCP server is not available

**Solution:**
```bash
# Reinstall the specific package
npm install -g [package-name]@latest

# Example
npm install -g @supabase/mcp-server-supabase@latest
```

#### Issue 2: API Key Invalid

**Symptom:** MCP server returns 401 or authentication error

**Solution:**
1. Verify API key in `claude_mcp_config.json`
2. Check key validity at provider's dashboard
3. Regenerate key if expired
4. Ensure no extra spaces or quotes in API key

#### Issue 3: npx Command Failed

**Symptom:** MCP server fails to start

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall all packages
npm install -g pnpm@latest
npm install -g @supabase/mcp-server-supabase@latest
# ... (repeat for other packages)
```

#### Issue 4: Rate Limit Exceeded

**Symptom:** API calls fail due to too many requests

**Solution:**
- **OpenRouter:** Check credits at https://openrouter.ai/credits
- **Firecrawl:** Check usage at https://firecrawl.dev/dashboard
- **Browserbase:** Check usage at https://browserbase.com/dashboard
- **Gemini:** Check quota at https://makersuite.google.com

#### Issue 5: Environment Variable Not Found

**Symptom:** MCP server can't find API key

**Solution:**
1. Check `.env` file exists
2. Verify key names match configuration
3. Restart Claude Code session
4. Check file permissions

### Checking MCP Server Status

```bash
# List running MCP processes
ps aux | grep -E "mcp|npx"

# Check Claude Code config
cat ~/.config/claude/claude_mcp_config.json

# Verify npm packages
npm list -g --depth=0
```

---

## API Keys Management

### Getting API Keys

| Service | Where to Get | Free Tier | Paid Plans |
|---------|-------------|-----------|------------|
| **Ref** | https://ref.tools | Unlimited | N/A |
| **Supabase** | https://supabase.com/dashboard/account/tokens | 500MB DB | From $25/mo |
| **ShadCN UI** | N/A (No key needed) | Unlimited | N/A |
| **Firecrawl** | https://firecrawl.dev | 500 pages/mo | From $49/mo |
| **OpenRouter** | https://openrouter.ai/keys | Pay-per-use | Variable pricing |
| **Browserbase** | https://browserbase.com | 10 hours/mo | From $50/mo |
| **Gemini** | https://makersuite.google.com/app/apikey | 60 req/min | Free tier |

### Security Best Practices

1. **Never commit API keys to Git**
   - `.env` is in `.gitignore`
   - `claude_mcp_config.json` is in `.gitignore`
   - Use `.example` files for templates

2. **Rotate keys regularly**
   - Regenerate keys every 3 months
   - Update both `.env` and `claude_mcp_config.json`

3. **Limit key permissions**
   - Use read-only keys when possible
   - Enable key expiration dates
   - Set up IP restrictions if available

4. **Monitor key usage**
   - Check dashboards weekly
   - Set up usage alerts
   - Review access logs

5. **Backup keys securely**
   - Use password manager
   - Encrypted storage only
   - Never share keys in chat/email

---

## Updating MCP Servers

### Update All Servers

```bash
# Update npm
npm install -g npm@latest

# Update individual packages
npm update -g @supabase/mcp-server-supabase
npm update -g @jpisnice/shadcn-ui-mcp-server
npm update -g @browserbasehq/mcp
npm update -g firecrawl-mcp
npm update -g ref-tools-mcp
npm update -g @mcpservers/openrouterai

# Verify versions
npm list -g --depth=0 | grep mcp
```

---

## Support

- **SuperClaude Issues:** https://github.com/NomenAK/SuperClaude/issues
- **MCP Protocol:** https://modelcontextprotocol.io
- **Claude Code Docs:** https://docs.anthropic.com/claude/docs/claude-code

---

## Additional Resources

### Official Documentation

- **MCP Protocol:** https://modelcontextprotocol.io
- **Supabase MCP:** https://github.com/supabase/mcp-server-supabase
- **OpenRouter:** https://openrouter.ai/docs
- **Firecrawl:** https://docs.firecrawl.dev
- **Browserbase:** https://docs.browserbase.com
- **Ref Tools:** https://ref.tools/docs
- **ShadCN UI:** https://ui.shadcn.com

### Service Dashboards

- **Supabase:** https://supabase.com/dashboard
- **OpenRouter:** https://openrouter.ai/dashboard
- **Firecrawl:** https://firecrawl.dev/dashboard
- **Browserbase:** https://browserbase.com/dashboard
- **Gemini API:** https://makersuite.google.com

---

**Last Updated:** November 2025
**SuperClaude Version:** 2.0.1
**Maintained By:** SuperClaude Community

⚠️ **SECURITY WARNING:** Never commit API keys to version control. Always use `.env` files and keep them in `.gitignore`.
