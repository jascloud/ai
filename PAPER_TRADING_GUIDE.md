# Paper Trading Guide - Optimized Mean Reversion Strategy

## Overview

This guide covers running the **optimized mean reversion strategy** in paper trading mode (simulated execution with real market data) for 2-4 weeks to validate the backtest results.

**Key Point:** Paper trading is ZERO real money at risk—all execution is simulated with realistic slippage/spreads.

---

## Why Paper Trading?

### Gaps Between Backtest and Live Trading

| Aspect | Backtest | Live/Paper Trading |
|--------|----------|-------------------|
| Fill Price | Close price only | Bid-ask spread (±0.75) |
| Slippage | 0 | ~0.25 per order |
| Gaps | None (daily data) | Can be significant |
| Order Execution | Instant | May take minutes |
| Market Hours | 24/5 (gold) | Real market hours only |
| Commission | 0 | Included in spread model |

Paper trading **bridges this gap** by:
- Using real market prices (live IBKR data)
- Simulating realistic execution costs
- Running continuously over 2-4 weeks
- Monitoring equity curve and drawdown
- Detecting any edge cases or bugs

---

## Quick Start

### 1. Verify Prerequisites

```bash
# Check Python version
python3 --version  # Need 3.8+

# Check required files exist
ls -la paper_trading_engine.py
ls -la paper_trading_config.json
ls -la START_PAPER_TRADING.sh

# Check price data (most recent IBKR cache)
ls -la intraday_bar_cache.json
# If missing, fetch from IBKR first
```

### 2. Start Paper Trading

```bash
bash START_PAPER_TRADING.sh
```

The script will:
- Verify dependencies
- Create log directory (`.paper_trading_logs/`)
- Display configuration
- Ask for confirmation
- Run the trading engine
- Save results when complete

### 3. Monitor Progress

While trading runs, in another terminal:

```bash
# Watch live log output
tail -f .paper_trading_logs/paper_trading_*.log

# Check latest results
cat .paper_trading_logs/paper_trading_results_*.json | jq .

# Check if any trades executed
cat .paper_trading_logs/paper_trading_results_*.json | jq '.trades | length'
```

---

## Configuration

### Risk Controls (in `paper_trading_config.json`)

```json
{
  "daily_loss_limit_pct": 2,      // Stop trading after -$200 loss
  "max_position_size_pct": 5,     // Max $500 per trade
  "max_concurrent_positions": 3,  // Never more than 3 open trades
  "max_position_hold_days": 14    // Close positions after 14 days
}
```

**Can adjust these before starting, but NOT recommended** while trading.

### Execution Model

```json
{
  "bid_ask_spread_usd": 0.75,     // Gold typical spread
  "execution_slippage_usd": 0.25  // Realistic slippage
}
```

Gold (XAUUSD) typical spreads:
- Liquid hours (9:30-16:00 EDT): $0.50-0.75
- After hours: $1.00-2.00
- Our model uses $1.00 total cost ($0.75 spread + $0.25 slippage)

### Strategy Parameters

```json
{
  "rsi_period": 14,
  "rsi_buy_threshold": 30,        // Buy when RSI < 30
  "rsi_sell_threshold": 70,       // Sell when RSI > 70
  "stop_loss_atr_multiple": 1.5,  // Tight stops
  "take_profit_atr_multiple": 2.5
}
```

These match the optimized backtest (DO NOT CHANGE).

---

## Expected Behavior

### First 24-48 Hours

- Engine loads price history
- Calculates RSI/ATR for each daily bar
- Looks for entry signals (RSI < 30 or > 70)
- May take time to generate first trade
- Check logs: `tail -f .paper_trading_logs/paper_trading_*.log`

### During Trading

**Good signs:**
- ✓ Trades every 3-7 days
- ✓ Mix of BUY and SELL signals
- ✓ Win rate around 35-40%
- ✓ P&L varies but stays positive overall
- ✓ Max drawdown < 20%

**Red flags:**
- ✗ No trades after 5+ days (check RSI calculations)
- ✗ Only SELL signals (check entry logic)
- ✗ Every trade is a loss (check stop loss/take profit)
- ✗ Equity dropping faster than -2% per day (check slippage)

### Completion (After 30 Days or 20+ Trades)

Engine will:
- Print final summary to console
- Save results to JSON
- Exit cleanly

---

## Monitoring the Equity Curve

### Manual Check

```bash
python3 -c "
import json
import sys
from pathlib import Path

log_dir = Path('.paper_trading_logs')
result_files = sorted(log_dir.glob('paper_trading_results_*.json'))

if result_files:
    with open(result_files[-1]) as f:
        data = json.load(f)
        
    print(f\"Initial Capital: \${data['initial_capital']:,.2f}\")
    print(f\"Final Capital:   \${data['final_capital']:,.2f}\")
    print(f\"Return:          {data['total_return_pct']:+.2f}%\")
    print(f\"Max Drawdown:    {data['max_drawdown_pct']:.2f}%\")
    print(f\"Trades:          {data['total_trades']}\")
    print()
    print(f\"Equity Curve (last 10): {[round(e, 0) for e in data['equity_curve'][-10:]]}\")
"
```

### Visual Check (if gnuplot available)

```bash
# Extract equity curve
python3 -c "
import json
result_files = sorted(Path('.paper_trading_logs').glob('paper_trading_results_*.json'))
with open(result_files[-1]) as f:
    eq = json.load(f)['equity_curve']
for i, e in enumerate(eq):
    print(f'{i} {e:.2f}')
" | gnuplot -e "set title 'Paper Trading Equity'; plot '-' with lines"
```

---

## Troubleshooting

### "No price data available"

**Cause:** `intraday_bar_cache.json` missing or empty

**Solution:**
```bash
# Option 1: Fetch from IBKR
python3 scripts/build_ibkr_price_cache.py

# Option 2: Check backup location
ls -la ~/.tradingagents/cache/

# Option 3: Use historical data file
# (Engine falls back to embedded historical data)
```

### "No trades executed after 5 days"

**Possible causes:**
1. RSI calculation error (check logs)
2. Price data is stale (check dates in log)
3. Strategy conditions too strict (RSI < 30 is rare)

**Debug:**
```bash
# Check recent log entries for RSI values
tail -100 .paper_trading_logs/paper_trading_*.log | grep RSI

# Should see values between 0-100
# If all near 50, RSI calculation may be wrong
```

### "Trades look unrealistic (too large wins/losses)"

**Cause:** Slippage model too aggressive

**Fix:** Edit `paper_trading_engine.py`, line ~185:
```python
spread = 0.75  # Reduce to 0.50 for liquid hours
slippage = 0.25  # Reduce to 0.10 if seeing too much cost
```

### "Daily loss limit keeps triggering"

**Cause:** Strategy underperforming live vs backtest

**Options:**
1. Increase daily limit temporarily: `-2%` → `-3%`
2. Reduce position size: `5%` → `2.5%`
3. Review losing trades for issues (slippage, entry timing)

---

## Interpreting Results

### Success Criteria (from `paper_trading_config.json`)

```
✓ Minimum 5 trades executed
✓ Win rate ≥ 30%
✓ Return ≥ +2.5%
✓ Slippage cost < 2% per trade
✓ Max drawdown < 20%
```

### Comparison to Backtest

Expected differences:

| Metric | Backtest | Paper Trading |
|--------|----------|---------------|
| Return | +6.32% | +2-4% (slippage cost) |
| Trades | 19 | 10-20 (depends on data period) |
| Win Rate | 36.8% | 30-40% (should be similar) |
| Drawdown | 18.89% | 15-25% (slippage increases slightly) |

**If paper trading returns are 80%+ of backtest**, strategy is validated.

---

## Next Steps After Paper Trading

### If Results Are Good (✓ All criteria met)

1. **Small Live Trading** (optional):
   - Start with $500-1000 real capital
   - Trade only 1-2 positions at a time
   - Use same risk limits as paper trading
   - Monitor for 2-4 weeks

2. **Scale Up**:
   - Increase position size gradually
   - Extend to other commodities (Silver, Oil)
   - Consider different timeframes (4-hour, weekly)

### If Results Are Concerning (✗ Multiple failures)

1. **Debug Strategy**:
   - Review losing trades in detail
   - Check if RSI thresholds are too loose
   - Verify entry/exit logic is correct

2. **Adjust Parameters**:
   - Try RSI 25/75 (more extreme)
   - Try RSI 35/65 (less extreme)
   - Adjust ATR multiples for stops/targets

3. **Re-backtest** with new parameters

---

## Important Notes

### Capital Management

- Paper trading uses **simulated $10,000**
- No real money is at risk
- Daily loss limit: **-2%** ($200)
- Position size limit: **5%** ($500 max)

### Continuous Execution

The trading engine is designed to run **continuously**, checking for new prices daily. To keep it running:

1. **Local machine:**
   - Run in `screen` or `tmux` session
   - Don't close terminal window

2. **Cloud/VPS (recommended):**
   - SSH into server
   - Use `nohup` or `screen`
   - Leave it running 24/7

   ```bash
   nohup bash START_PAPER_TRADING.sh > paper_trading.out 2>&1 &
   ```

3. **Monitor remotely:**
   ```bash
   tail -f paper_trading.out
   ```

### Data Freshness

- Engine loads historical data once at startup
- Then checks for new prices daily
- If prices don't update (no new IBKR data), trading slows down
- Plan to refresh `intraday_bar_cache.json` weekly

---

## File Locations

### During Paper Trading

```
.paper_trading_logs/
├── paper_trading_20260711_205900.log          # Main log
├── paper_trading_prices_20260711_205900.json  # Cached prices
└── paper_trading_results_20260711_205900.json # Final results
```

### Results File Format

```json
{
  "session_id": "20260711_205900",
  "symbol": "XAUUSD",
  "initial_capital": 10000,
  "final_capital": 10631.68,
  "total_return_pct": 6.32,
  "total_trades": 19,
  "max_drawdown_pct": 18.89,
  "trades": [
    {
      "entry_time": "2025-09-18T...",
      "entry_price": 3684.75,
      "exit_time": "2025-09-22T...",
      "exit_price": 3764.18,
      "exit_fill_price": 3764.18,
      "pnl": -79.43,
      "pnl_pct": -2.16,
      "exit_reason": "stop_loss",
      "slippage": 1.00
    },
    ...
  ],
  "equity_curve": [10000, 9920.57, ...]
}
```

---

## Questions?

If you encounter issues:

1. Check logs: `tail -f .paper_trading_logs/paper_trading_*.log`
2. Review configuration: `cat paper_trading_config.json | jq .risk_controls`
3. Inspect latest results: `cat .paper_trading_logs/paper_trading_results_*.json | jq`
4. Compare to backtest: Check `optimized_backtest_v2_results.json`

---

## Timeline

- **Day 1-7:** Initial price loading, first trades should appear
- **Day 8-14:** Accumulate 5-10 trades, assess win rate
- **Day 15-21:** 10-15 trades, validate consistency
- **Day 22-30:** Final trades, complete analysis, make go/no-go decision

**Total duration:** 30 days (or sooner if 20+ trades completed)

---

**Status:** Ready to validate. Paper trading starts with ZERO real capital at risk. Good luck! 🎯
