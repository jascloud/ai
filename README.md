# AI Repository - CCXT Integration

This repository contains integration and setup for the CCXT cryptocurrency trading library.

## Structure

- **ccxt/** - Full CCXT repository (https://github.com/ccxt/ccxt)
  - TypeScript source of truth in `ts/src/`
  - Transpiled to JavaScript, Python, PHP, C#, and Go
  - Comprehensive documentation in `CLAUDE.md`

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
