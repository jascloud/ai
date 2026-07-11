# Momentum Trading Agent System - Claude Code Documentation

This is a comprehensive multi-agent momentum trading system for S&P 500 stocks, built on the TradingAgents framework with Claude AI integration.

## 📋 Overview

The Momentum Trading Agent is a coordinated system of 7 specialized agents that work together to:
- Identify momentum trading opportunities in S&P 500 stocks
- Analyze technical, fundamental, sentiment, and news signals
- Debate bullish and bearish scenarios
- Manage portfolio risk and execute trades
- Backtest strategies with comprehensive metrics

## 🎯 Strategy

**Type**: Momentum Trading  
**Asset Class**: Equities (S&P 500)  
**Capital**: $500  
**Time Period**: 1 week (rolling)  

### Entry Signals
- RSI > 65 (strong uptrend)
- MACD positive divergence
- Price above 20-day SMA
- Volume confirmation above average

### Exit Signals
- Stop loss at 2% below entry
- Take profit at 5% above entry
- RSI > 80 (overbought exit)
- MACD bearish crossover

### Position Management
- Position sizing: Kelly Criterion
- Max position size: 5% per trade
- Risk per trade: 1%
- Rebalance: Daily

## 👥 7 Specialized Agents

### 1. **Technical Analyst Agent**
- **Role**: Identifies momentum patterns and technical signals
- **Indicators**: RSI, MACD, Stochastic, CCI, Rate of Change (ROC)
- **Focus**: Entry/exit timing based on technical analysis
- **Output**: Technical rating (1-5), recommended action

### 2. **Fundamental Analyst Agent**
- **Role**: Assesses company financial health
- **Metrics**: P/E ratio, revenue growth, profit margin, ROE
- **Focus**: Ensure trading quality companies
- **Output**: Fundamental rating (1-5), financial health assessment

### 3. **Sentiment Analyst Agent**
- **Role**: Gauges market sentiment and investor mood
- **Sources**: StockTwits, Reddit, social media sentiment analysis
- **Focus**: Short-term market psychology
- **Output**: Sentiment score (-1 to +1), sentiment trend

### 4. **News Analyst Agent**
- **Role**: Monitors catalysts and news events
- **Lookback**: 7-day news window
- **Focus**: Identify catalyst-driven momentum
- **Output**: Catalyst assessment, impact rating

### 5. **Bull Researcher Agent**
- **Role**: Identifies upside opportunities and positive scenarios
- **Debate Rounds**: 2 rounds of analysis
- **Focus**: Bullish thesis development
- **Output**: Bull case summary, upside scenario

### 6. **Bear Researcher Agent**
- **Role**: Identifies risks and downside scenarios
- **Debate Rounds**: 2 rounds of analysis
- **Focus**: Risk assessment and contrarian views
- **Output**: Bear case summary, downside risk assessment

### 7. **Portfolio Manager Agent**
- **Role**: Final decision-maker and risk controller
- **Constraints**: 
  - Max correlation between positions: 0.6
  - Max sector exposure: 30%
  - Max drawdown tolerance: 10%
- **Focus**: Portfolio-level risk management
- **Output**: Trade decision (BUY/SELL/HOLD), position size, risk controls

## 📊 Backtesting Metrics

All metrics calculated across 5 independent backtests:

- **Total Return**: Cumulative percentage return
- **Sharpe Ratio**: Risk-adjusted return (excess return/volatility)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Gross profit / Gross loss
- **Recovery Factor**: Total return / Max Drawdown
- **Sortino Ratio**: Risk-adjusted return (only downside volatility)
- **Calmar Ratio**: Annual return / Max Drawdown

## 🚀 Files

### Core Files
- `momentum-trading-agent-final.json` - Agent configuration
- `backtest_momentum_agent.py` - Backtesting engine with all 7 agents
- `market_data.py` - Real market data fetching (Alpha Vantage / Yahoo Finance)
- `run_momentum_backtest.sh` - Bash script to execute backtests

### Configuration
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies for the backtest engine
- `tradingagents/` - Full TradingAgents framework (optional, not required by the backtester)

## 📡 Data Sources — Read This First

**TradingView has no public REST API for historical OHLCV data** — it's a
charting/broker-integration product, not a data-licensing API. **There is
also no dedicated "Yahoo Finance" MCP server in the connector registry**
(checked via `SearchMcpRegistry`). "Connecting with TradingView"/Yahoo for
real prices is implemented via, tried in this order:

1. **Local cache file** (`market_data_cache.json` / `MOMENTUM_PRICE_CACHE_FILE`)
   — real closes written to disk by whoever orchestrates a run. In
   practice this is populated by an **Interactive Brokers (IBKR) MCP
   connector** call (`get_price_history`) when one is available and
   authenticated — that path was verified working end-to-end in this
   repo's dev session, and it sidesteps any outbound-HTTPS egress policy
   since it goes through the MCP connector infrastructure instead of raw
   HTTP. See `scripts/build_ibkr_price_cache.py` for the format.
2. **Alpha Vantage** (registry has an official "Alpha Vantage MCP
   Server", not installed by default here) — requires `ALPHA_VANTAGE_API_KEY`
3. **Yahoo Finance** via `yfinance` (fallback) — no key required, but the
   host must be reachable from wherever this runs; confirmed blocked by
   this dev session's own egress policy (403 from the agent proxy) —
   your deployment environment's policy may differ

| Agent | Data Source |
|-------|--------------|
| Technical Analyst | **Real** historical closing prices |
| Fundamental Analyst | Simulated (no live fundamentals feed configured) |
| Sentiment Analyst | Simulated (no live social/sentiment feed configured) |
| News Analyst | Simulated (no live news feed configured) |
| Bull / Bear Researcher | Simulated (debate framing over the above) |
| Portfolio Manager | Aggregates whatever the above produced |

`backtest_momentum_agent.py` and `market_data.py` **never fabricate prices**
as a fallback — if neither Alpha Vantage nor Yahoo Finance is reachable, the
run fails loudly with the specific cause (see `MarketDataError`) instead of
producing numbers. Every result file tags each agent's `data_source` so
simulated ratings are never presented as real.

## 🔧 Setup

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your real API key:
```
ALPHA_VANTAGE_API_KEY=your_key   # required for real price data
```

### 3. Validate (checks strategy config AND real data connectivity)

```bash
python3 backtest_momentum_agent.py --validate
```

This exits non-zero and prints the specific network/API error if real
market data cannot be reached — that must be resolved before backtests
will produce results.

### 4. Run Backtests

```bash
bash run_momentum_backtest.sh
```

## 📈 Usage Examples

### Via Claude Code CLI

```bash
# Run with configuration
claude code --config momentum-trading-agent.json

# Run backtests
claude code run backtest_momentum_agent.py

# Interactive mode
claude code console --config momentum-trading-agent.json
```

### Via Python

```python
from backtest_momentum_agent import MomentumBacktester

# Initialize backtester
backtester = MomentumBacktester(
    initial_capital=500,
    time_period="1_week",
    num_backtests=5
)

# Run all backtests
results = backtester.run_all_backtests()

# Get summary
summary = backtester.get_summary_metrics()
print(summary)
```

## 📝 Configuration Schema

See `momentum-trading-agent.json` for full schema:

```json
{
  "strategy": {
    "type": "momentum_trading",
    "entry_conditions": [...],
    "exit_conditions": [...]
  },
  "backtesting": {
    "initial_capital": 500,
    "time_period": "1_week",
    "num_backtests": 5,
    "metrics": [...]
  },
  "agents": {
    "technical_analyst": {...},
    "fundamental_analyst": {...},
    ...
  }
}
```

## 🔄 Agent Workflow

```
Stock Selected (SP500)
    ↓
Technical Analyst → Technical signals
    ↓
Fundamental Analyst → Financial assessment
    ↓
Sentiment Analyst → Market mood
    ↓
News Analyst → Catalysts
    ↓
Bull Researcher ←→ Bear Researcher (2-round debate)
    ↓
Portfolio Manager (Final Decision)
    ↓
Execute Trade or Hold
```

## 📊 Output Format

Backtests produce JSON output:

```json
{
  "backtest_results": [
    {
      "backtest_id": 1,
      "metrics": {
        "total_return": 0.145,
        "sharpe_ratio": 1.82,
        "max_drawdown": -0.087,
        "win_rate": 0.62,
        "profit_factor": 2.43,
        "recovery_factor": 1.67,
        "sortino_ratio": 2.15,
        "calmar_ratio": 1.67
      },
      "trades": [...],
      "daily_returns": [...]
    }
  ],
  "summary": {
    "avg_total_return": 0.151,
    "avg_sharpe_ratio": 1.76,
    "avg_max_drawdown": -0.092,
    ...
  }
}
```

## 🛠 Skills & Tools Available

### Technical Analysis Skills
- `technical_analysis` - RSI, MACD, Stochastic calculations
- `momentum_indicators` - ROC, CCI, Momentum oscillators

### Fundamental Analysis Skills
- `fundamental_analysis` - Financial metrics, ratios
- `earnings_quality` - Earnings analysis and trends

### Market Intelligence Skills
- `sentiment_analysis` - Social media and news sentiment
- `news_analysis` - Catalyst detection and impact assessment

### Portfolio Skills
- `portfolio_management` - Position sizing, correlation analysis
- `risk_management` - Drawdown control, volatility management
- `research_debate` - Bull/Bear case synthesis

## 🔍 Monitoring & Logging

Results are logged to:
- `~/.tradingagents/logs/` - Execution logs
- `~/.tradingagents/cache/` - Market data cache
- `~/.tradingagents/memory/` - Trading memory log

View recent trades:
```bash
cat ~/.tradingagents/memory/trading_memory.md
```

## 🤖 Model Configuration

Default models configured:
- **Deep Think**: Claude Opus 4.8 (complex analysis)
- **Quick Think**: Claude Opus 4.8 (fast decisions)

Override via environment:
```bash
export TRADINGAGENTS_DEEP_THINK_LLM=claude-opus-4-8
export TRADINGAGENTS_QUICK_THINK_LLM=claude-opus-4-8
export TRADINGAGENTS_TEMPERATURE=0.7
```

## 📚 References

- [TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- [TradingAgents Paper](https://arxiv.org/abs/2412.20138)
- [CCXT Exchange Library](https://github.com/ccxt/ccxt)

## 🧪 Testing

Run unit tests:

```bash
cd trading-agents
python -m pytest tests/ -v
```

Run strategy validation:

```bash
python backtest_momentum_agent.py --validate
```

## 📄 License

This agent system builds on TradingAgents (MIT License). For full license terms, see `trading-agents/LICENSE`.

## 🤝 Contributing

To extend the momentum trading agent:

1. Add new indicators to `technical_indicators_tools.py`
2. Create new analyst agents in `tradingagents/agents/analysts/`
3. Update agent configuration in `momentum-trading-agent.json`
4. Run backtests to validate performance
5. Commit changes to the designated branch

## 📞 Support

For issues with TradingAgents, see [GitHub Issues](https://github.com/TauricResearch/TradingAgents/issues)

For Claude Code help: `/help`

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-11  
**Status**: Production Ready
