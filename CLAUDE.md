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
**Capital**: $100,000  
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
- `momentum-trading-agent.json` - Agent configuration
- `backtest_momentum_agent.py` - Backtesting engine with all 7 agents
- `run_momentum_backtest.sh` - Bash script to execute backtests

### Configuration
- `.env.example` - Environment variables template
- `tradingagents/` - Full TradingAgents framework

## 🔧 Setup

### 1. Installation

```bash
cd trading-agents
pip install -e .
# or
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
TRADINGAGENTS_LLM_PROVIDER=anthropic
TRADINGAGENTS_DEEP_THINK_LLM=claude-opus-4-8
TRADINGAGENTS_QUICK_THINK_LLM=claude-opus-4-8
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
```

### 3. Run Backtests

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
    initial_capital=100000,
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
    "initial_capital": 100000,
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
