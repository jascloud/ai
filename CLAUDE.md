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

## 👥 9 Specialized Agents

Real-data status per agent, and which `data_clients/` module backs each
one, per the phased real-data rollout (see
`agent_rating_diagnostics_summary.json` for the clearance-rate
diagnostics run after every phase):

### 1. **Technical Analyst Agent** — real data
- **Role**: Identifies momentum patterns and technical signals
- **Indicators**: RSI, MACD, SMA, Momentum, plus optional live
  enrichment (overnight gap, 5min RSI confirmation) via
  `data_clients/equity_quotes.py`, `ohlcv_multi_timeframe.py`,
  `extended_hours.py` — never used during the historical backtest loop
  (would be lookahead bias)
- **Output**: Technical rating (1-5), recommended action, confidence

### 2. **Fundamental Analyst Agent** — real data
- **Role**: Assesses company financial health from earnings surprise
  history, estimate revisions, analyst consensus/price targets, and SEC
  filing trends/guidance language
- **Sources**: `earnings_calendar.py`, `estimate_revisions.py`,
  `analyst_ratings.py`, `sec_filings.py`
- **Output**: Fundamental rating (1-5), sources used, degraded reasons

### 3. **Sentiment Analyst Agent** — real data
- **Role**: One combined social-sentiment score from Twitter/X + Reddit
  + StockTwits (deliberately not three separate averaged agents)
- **Source**: `social_sentiment.py`
- **Output**: Sentiment score (-1 to +1), social volume, sources used

### 4. **News Analyst Agent** — real data
- **Role**: Real-time headline feed scored by a finance-tuned lexicon
  sentiment classifier
- **Sources**: `news_wire.py`, `news_sentiment.py`
- **Output**: Rating (1-5), headline count, sentiment score

### 5. **Bull Researcher Agent** — real data
- **Role**: Unusual call-side options volume/open-interest skew (a
  bullish-flow proxy) — no longer random confidence
- **Source**: `options_chain.py` (per-symbol)
- **Output**: Rating (1-5), scenario, confidence

### 6. **Bear Researcher Agent** — real data
- **Role**: Put/call volume ratio + put-side skew (a hedging-demand /
  bearish-flow proxy) — no longer random confidence
- **Source**: `options_chain.py` (per-symbol)
- **Output**: Rating (1-5), scenario, confidence

### 7. **Macro Agent** — real data (new, dampener)
- **Role**: FOMC-meeting proximity (local calendar, no key needed),
  2s10s yield curve, fed funds rate trend, CPI/PCE/jobs releases.
  Excluded from the weighted average entirely — applied afterward as a
  multiplicative `dampen_factor` and/or hard `suppress_buy` override
  (e.g. the day before an FOMC decision), so it can't be diluted away
  like an ordinary averaged vote
- **Source**: `macro_calendar.py`
- **Output**: dampen_factor, suppress_buy, note

### 8. **Geopolitical Agent** — real data (new)
- **Role**: Caldara-Iacoviello Geopolitical Risk (GPR) Index + EIA WTI
  oil-price-based supply-disruption proxy. Neutral (3) by default;
  PortfolioManager applies a crisis override (rating <= 1.5 caps the
  decision at HOLD) so an active crisis pulls the aggregate down
  materially instead of being one vote among several
- **Source**: `geopolitical_risk.py`
- **Output**: Rating (1-5), risk level, note

### 9. **Portfolio Manager Agent**
- **Role**: Final decision-maker and risk controller. Weighted mean
  (Technical Analyst = 50% of the decision, every other averaged agent
  shares the remaining 50%), thresholds BUY >= 3.5 / SELL <= 2.5,
  dampener/crisis-override application, full `agent_ratings_log` for
  auditability
- **Constraints**:
  - Max correlation between positions: 0.6
  - Max sector exposure: 30%
  - Max position size / total exposure / open positions: enforced by
    `data_clients/risk_monitor.py` as a hard-stop gate before every BUY
- **Output**: Trade decision (BUY/SELL/HOLD), position size, `avg_rating`
  (the weighted+dampened value that drove the decision), `flat_avg_rating`
  (old-style mean, audit-only), `agent_ratings_log`

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
