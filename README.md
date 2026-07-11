# AI Repository - Trading System Integration

This repository contains integration and setup for advanced trading systems and libraries.

## Structure

- **ccxt/** - Full CCXT repository (https://github.com/ccxt/ccxt)
  - TypeScript source of truth in `ts/src/`
  - Transpiled to JavaScript, Python, PHP, C#, and Go
  - Comprehensive documentation in `CLAUDE.md`

- **trading-agents/** - TradingAgents Framework (https://github.com/TauricResearch/TradingAgents)
  - Multi-agent LLM financial trading framework
  - Specialized agents: Fundamental, Sentiment, News, Technical Analysts
  - Researcher, Trader, Risk Management, and Portfolio Manager agents
  - Python-based implementation with CLI support

## TradingAgents Quick Start

1. **Install dependencies**:
   ```bash
   cd trading-agents
   pip install -r requirements.txt
   # or
   pip install -e .
   ```

2. **Configure API keys**: Copy `.env.example` to `.env` and add your:
   - LLM provider keys (OpenAI, Anthropic, Gemini, etc.)
   - Data provider credentials (Alpha Vantage, Financial APIs, etc.)

3. **Run the framework**:
   ```bash
   python main.py
   # or use CLI
   python cli/main.py
   ```

4. **Read the docs**: See `trading-agents/README.md` for detailed documentation

## CCXT Skills

The following skills are available when working with CCXT code:

- `ccxt-typescript` - TypeScript/JavaScript (Node.js and browser)
- `ccxt-python` - Python (sync and async support)
- `ccxt-php` - PHP (sync and ReactPHP async)
- `ccxt-csharp` - C# and .NET
- `ccxt-go` - Go
- `ccxt-java` - Java (Java 21+)
- `new-exchange` - Scaffold new exchange integration

## Quick Start

1. **Read CCXT documentation**: `ccxt/CLAUDE.md` contains the authoritative architecture guide
2. **Edit TypeScript source**: All changes start in `ccxt/ts/src/`
3. **Build for all languages**: Run `npm run build` in `ccxt/`
4. **Test**: Use language-specific test runners in each language directory

## Key Rules

⚠️ **CRITICAL**: CCXT is a transpiled library. The single source of truth is TypeScript (`ts/src/`).

- ✅ DO edit: `ts/src/` (all `.ts` files)
- ❌ NEVER edit: Generated files (`js/`, `python/ccxt/`, `php/`, `cs/ccxt/`, `go/v4/`)
- ⚠️ MOSTLY DON'T: Base files with partly-transpiled code (see `CLAUDE.md` §4)

Always run the full test suite after changes:
```bash
cd ccxt
npm run build
npm run test  # TypeScript
npm run test-python  # Python
# etc.
```

## Documentation

- `ccxt/CLAUDE.md` - Architecture, transpiler conventions, source of truth
- `ccxt/CONTRIBUTING.md` - Detailed contribution guidelines
- `ccxt/wiki/Manual.md` - Unified API specification
- `ccxt/wiki/Requirements.md` - New exchange checklist
