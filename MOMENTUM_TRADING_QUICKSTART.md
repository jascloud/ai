# 🚀 Momentum Trading Agent - Quick Start Guide

Complete setup and execution guide for the 7-agent momentum trading system.

## 📦 What You Get

- **7 Specialized Trading Agents**
  - Technical Analyst (momentum indicators)
  - Fundamental Analyst (company financials)
  - Sentiment Analyst (market psychology)
  - News Analyst (catalyst detection)
  - Bull Researcher (upside analysis)
  - Bear Researcher (downside analysis)
  - Portfolio Manager (risk control)

- **Backtesting Engine** with comprehensive metrics
- **Configuration System** (JSON + environment variables)
- **Automated Reporting** and analysis

## 🎯 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd trading-agents
pip install -r requirements.txt
# or for development
pip install -e .
cd ..
```

### Step 2: Configure Environment (Optional)

```bash
cp trading-agents/.env.example trading-agents/.env
```

Edit `.env` with your API keys:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
ALPHA_VANTAGE_API_KEY=...
TRADINGAGENTS_LLM_PROVIDER=anthropic
TRADINGAGENTS_DEEP_THINK_LLM=claude-opus-4-8
```

### Step 3: Run Backtests

**Simple (uses defaults: $100k capital, 1 week, 5 backtests)**:
```bash
bash run_momentum_backtest.sh
```

**Custom configuration**:
```bash
bash run_momentum_backtest.sh 50000 1_week 10
```

**Via Python directly**:
```bash
python3 backtest_momentum_agent.py \
  --capital 100000 \
  --period 1_week \
  --num-backtests 5 \
  --output results.json
```

### Step 4: Review Results

```bash
# View JSON results
cat momentum_backtest_results.json | python3 -m json.tool

# View markdown report
cat momentum_backtest_report_*.md

# Quick summary
python3 << 'EOF'
import json
with open('momentum_backtest_results.json') as f:
    data = json.load(f)
    agg = data['aggregate_metrics']
    print(f"Avg Return: {agg['avg_total_return']*100:.2f}%")
    print(f"Sharpe Ratio: {agg['avg_sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {agg['avg_max_drawdown']*100:.2f}%")
EOF
```

## 📊 Output Example

### Results JSON Structure

```json
{
  "backtest_summary": {
    "num_backtests": 5,
    "initial_capital": 100000,
    "time_period": "1_week",
    "agents": [
      "Technical Analyst",
      "Fundamental Analyst",
      "Sentiment Analyst",
      "News Analyst",
      "Bull Researcher",
      "Bear Researcher",
      "Portfolio Manager"
    ]
  },
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
        "calmar_ratio": 1.67,
        "final_capital": 114500.00,
        "total_trades": 13,
        "winning_trades": 8
      },
      "trades": [
        {
          "symbol": "AAPL",
          "action": "BUY",
          "price": 145.32,
          "quantity": 34.5,
          "cost": 5011.52
        },
        {
          "symbol": "AAPL",
          "action": "SELL",
          "price": 148.75,
          "quantity": 34.5,
          "proceeds": 5131.88,
          "profit": 120.36
        }
      ],
      "daily_returns": [0.0045, 0.0032, -0.0018, 0.0078, 0.0089],
      "daily_portfolio_values": [100000, 100450, 100882, 100750, 100828, 101719]
    }
  ],
  "aggregate_metrics": {
    "avg_total_return": 0.151,
    "std_total_return": 0.035,
    "avg_sharpe_ratio": 1.76,
    "std_sharpe_ratio": 0.28,
    "avg_max_drawdown": -0.092,
    "std_max_drawdown": 0.018,
    "avg_win_rate": 0.58,
    "std_win_rate": 0.08,
    "avg_profit_factor": 2.31,
    "std_profit_factor": 0.42,
    "avg_recovery_factor": 1.64,
    "avg_sortino_ratio": 2.08,
    "avg_calmar_ratio": 1.65,
    "total_trades_across_backtests": 65,
    "avg_trades_per_backtest": 13
  }
}
```

## 🔧 Configuration Files

### Agent Configuration: `momentum-trading-agent.json`

```json
{
  "name": "Momentum Trading Agent",
  "strategy": {
    "type": "momentum_trading",
    "entry_conditions": [
      "RSI > 65",
      "MACD positive",
      "Price > 20-day SMA",
      "Volume confirmation"
    ],
    "exit_conditions": [
      "Stop loss 2%",
      "Take profit 5%",
      "RSI > 80",
      "MACD bearish"
    ]
  },
  "agents": {
    "technical_analyst": {
      "indicators": ["RSI", "MACD", "Stochastic", "CCI", "ROC"]
    },
    "portfolio_manager": {
      "max_correlation": 0.6,
      "max_sector_exposure": 0.3
    }
  }
}
```

### Environment: `trading-agents/.env`

```bash
# LLM Provider
TRADINGAGENTS_LLM_PROVIDER=anthropic
TRADINGAGENTS_DEEP_THINK_LLM=claude-opus-4-8
TRADINGAGENTS_QUICK_THINK_LLM=claude-opus-4-8

# API Keys
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Optional
TRADINGAGENTS_TEMPERATURE=0.7
TRADINGAGENTS_MAX_DEBATE_ROUNDS=2
TRADINGAGENTS_CHECKPOINT_ENABLED=true
```

## 📈 Understanding Metrics

| Metric | Interpretation | Target |
|--------|-----------------|--------|
| **Total Return** | Overall profit percentage | +10% to +50% |
| **Sharpe Ratio** | Risk-adjusted returns | > 1.0 is good, > 2.0 excellent |
| **Max Drawdown** | Largest peak-to-trough loss | < 10% for conservative |
| **Win Rate** | % of profitable trades | > 50% indicates strategy edge |
| **Profit Factor** | Gross profit / Gross loss | > 1.5 is acceptable, > 2.0 strong |
| **Recovery Factor** | Total return / Max drawdown | > 2.0 is good |
| **Sortino Ratio** | Return / downside volatility | > 1.0 is good |
| **Calmar Ratio** | Annual return / Max drawdown | > 1.0 is good |

## 🛠 CLI Usage

### With Claude Code

```bash
# Run with config
claude code --config momentum-trading-agent.json

# Interactive mode
claude code console --config momentum-trading-agent.json

# Execute backtests
claude code run backtest_momentum_agent.py --capital 100000
```

### With Python

```bash
# Validate strategy
python3 backtest_momentum_agent.py --validate

# Run single backtest
python3 backtest_momentum_agent.py --num-backtests 1

# Custom output
python3 backtest_momentum_agent.py --output custom_results.json
```

### With Bash

```bash
# Standard run
bash run_momentum_backtest.sh

# Custom capital and period
bash run_momentum_backtest.sh 250000 1_month 10

# Check requirements only
python3 -c "import numpy, pandas, scipy; print('✓ All requirements met')"
```

## 🎓 How It Works

### Agent Workflow

```
1. Market Data Selection
         ↓
2. Technical Analyst → Technical signals (RSI, MACD, etc.)
         ↓
3. Fundamental Analyst → Financial ratings
         ↓
4. Sentiment Analyst → Market sentiment scores
         ↓
5. News Analyst → Catalyst impact
         ↓
6. Bull Researcher ←→ Bear Researcher (Debate)
         ↓
7. Portfolio Manager (Final Decision)
         ↓
8. Execute: BUY / SELL / HOLD
         ↓
9. Risk Management & Position Sizing
         ↓
10. Log Results & Metrics
```

### Decision Logic

**BUY** when:
- Avg agent rating ≥ 4.0
- Technical signals positive
- Risk/reward favorable

**SELL** when:
- Avg agent rating ≤ 2.0
- Risk management trigger
- Stop loss hit

**HOLD** when:
- Mixed signals
- Low confidence
- Position already open

## 🔐 Security Considerations

- API keys stored in `.env` (add to `.gitignore`)
- No sensitive data in logs
- Rate limiting for API calls
- Local backtesting (no cloud dependency)

## 📞 Troubleshooting

### ModuleNotFoundError: No module named 'tradingagents'

```bash
cd trading-agents
pip install -e .
cd ..
```

### No API keys configured

```bash
# Works with simulated data for backtesting
python3 backtest_momentum_agent.py --validate
```

### Permission denied on bash script

```bash
chmod +x run_momentum_backtest.sh
bash run_momentum_backtest.sh
```

### Out of memory

```bash
# Reduce number of backtests
bash run_momentum_backtest.sh 100000 1_week 2
```

## 📚 Next Steps

1. **Extend Testing**: Run on longer time periods (1-3 months)
2. **Optimize Parameters**: Fine-tune momentum thresholds
3. **Add Real Data**: Integrate with Alpha Vantage or Yahoo Finance
4. **Live Trading**: Connect to CCXT for actual trading
5. **Machine Learning**: Add ML-based signal prediction

## 📖 Documentation

- `CLAUDE.md` - Full agent documentation
- `momentum-trading-agent.json` - Configuration schema
- `trading-agents/README.md` - TradingAgents framework docs

## 🤝 Support

- Issues: See `trading-agents/README.md`
- GitHub: https://github.com/TauricResearch/TradingAgents
- Paper: https://arxiv.org/abs/2412.20138

---

**Ready to trade? Run**: `bash run_momentum_backtest.sh`

**Questions?** Check the full documentation in `CLAUDE.md`
