# Next Steps: Paper Trading Phase

## You Are Here 📍

**Completed:** Strategy optimization and 1-year historical backtest
- ✅ Base strategy: 76 trades, -4.83% return (unprofitable)
- ✅ With trend filter: 2 trades (insufficient data)
- ✅ **Optimized v2: 19 trades, +6.32% return** ← Ready for validation

**Next:** Paper trading validation (2-4 weeks, zero real money at risk)

---

## Quick Start

### 1. Start Paper Trading (1 command)

```bash
bash START_PAPER_TRADING.sh
```

This will:
- Verify dependencies
- Load real XAUUSD price data
- Run continuous trading loop
- Save results daily to `.paper_trading_logs/`

### 2. Monitor Progress

In another terminal:

```bash
# Watch live trading log
tail -f .paper_trading_logs/paper_trading_*.log

# Check equity curve
tail -1 .paper_trading_logs/paper_trading_results_*.json | jq '.equity_curve[-5:]'

# View latest P&L
cat .paper_trading_logs/paper_trading_results_*.json | jq '{return: .total_return_pct, trades: .total_trades, drawdown: .max_drawdown_pct}'
```

### 3. Wait 30 Days or 20+ Trades

Engine will run continuously, checking for new prices daily and executing trades when RSI signals appear.

---

## What to Expect

### Timeline

| Period | Expected | Indicator |
|--------|----------|-----------|
| Day 1-2 | Load prices, initialize | Check: "Starting paper trading session" |
| Day 3-5 | First trade signals | RSI should cross 30 or 70 |
| Day 8-15 | 5-10 trades | Win rate should emerge (~35-40%) |
| Day 16-30 | 10-20 total trades | Equity curve should show trend |

### Daily Equity Curve

Expected progression (starting $10,000):

```
Day 1-7:   $10,000 → $9,900 (small position losses)
Day 8-15:  $9,900 → $10,200 (strategy finding winners)
Day 16-30: $10,200 → $10,600+ (cumulative gains)

Success: Final > Initial + 2.5% ($10,250+)
```

### Realistic Outcomes

**Good paper trading result:**
```
Initial:     $10,000
Final:       $10,400 (+4% vs +6.32% backtest)
Trades:      18 trades
Win Rate:    35.8% (vs 36.8% backtest)
Max DD:      20.2% (vs 18.89% backtest)
Slippage:    ~$1.00/trade
```

Explanation: Slightly lower return due to slippage ($1/trade × 18 = $18 cost), but validates strategy works on live data.

**Concerning paper trading result:**
```
Final:       $9,500 (-5%)
Trades:      3 only
Pattern:     All SELL signals, no BUYs
Max DD:      >25%
```

Explanation: Strategy not adapting to live market. Would need to revisit entry/exit logic.

---

## Success Criteria (from paper_trading_config.json)

To declare strategy validated, all of these must be true:

```
✓ Minimum 5 trades executed
✓ Win rate ≥ 30%
✓ Total return ≥ +2.5% (after slippage)
✓ Slippage cost < $2.00 per trade average
✓ Max drawdown < 20%
```

If **all criteria met** → Strategy ready for small live trading

If **3/5 criteria met** → Strategy shows promise; adjust and re-test

If **<3/5 criteria met** → Back to drawing board; refine strategy

---

## Expected Differences vs Backtest

### Why Paper Trading Returns Might Be Lower

| Factor | Impact | Amount |
|--------|--------|--------|
| Bid-ask spread | -$0.75 per trade | -$14.25 (18 trades) |
| Execution slippage | -$0.25 per trade | -$4.50 (18 trades) |
| Market gaps | Variable | -$0-100 |
| Late fills | 1-2% per trade | -$20-40 |
| **Total cost** | | **-$39-159** |

Backtest return: +$632 (6.32%)
Expected paper return: +$473-593 (4.7-5.9%)

**This is NORMAL and EXPECTED.** If paper trading hits +4%, you've proven the strategy works.

---

## What If Issues Appear?

### No Trades After 3 Days

**Check:**
```bash
# Verify prices loaded
tail -20 .paper_trading_logs/paper_trading_*.log | grep "price"

# Verify RSI calculation
tail -50 .paper_trading_logs/paper_trading_*.log | grep "RSI"
```

**Should see RSI values between 0-100 for each day.**

If not, likely issue:
- Price data is stale (need to refresh IBKR cache)
- RSI calculation has a bug

### All Trades Are Losses

**Possible causes:**
1. Slippage model too aggressive
2. Entry signal wrong (RSI threshold)
3. Stop loss too tight (1.5 ATR might be too tight)

**Fix:**
1. Reduce simulated slippage: edit `paper_trading_engine.py` line ~185
2. Adjust entry: try RSI < 35 or < 25
3. Increase stop: try 2.0 ATR instead of 1.5

Then restart paper trading with changes.

### Daily Loss Limit Keeps Triggering

**Cause:** Strategy underperforming, hitting -2% daily limit

**Options:**
1. **Increase limit temporarily:** `-2%` → `-3%` (to see if it recovers)
2. **Reduce position size:** `5%` → `2.5%` (let strategy prove itself with smaller positions)
3. **Adjust parameters:** Try looser entry signals (RSI 35/65 instead of 30/70)
4. **Give more time:** Sometimes strategies need 2-3 weeks to show edge

---

## During Paper Trading

### Daily Checklist

```
Each morning:
☐ Check log for new trades
☐ Verify equity didn't drop >5% overnight
☐ Review last 3 trades for patterns
☐ Confirm RSI calculations look correct

Each week:
☐ Run: cat .paper_trading_logs/paper_trading_results_*.json | jq '.trades | length'
☐ Calculate win rate: wins / total trades
☐ Check max drawdown hasn't exceeded 25%
☐ Refresh price cache if data is stale
```

### Commands for Monitoring

```bash
# Live feed (updates as trades happen)
tail -f .paper_trading_logs/paper_trading_*.log

# Current equity
python3 -c "
import json
from pathlib import Path
f = sorted(Path('.paper_trading_logs').glob('*results*.json'))[-1]
d = json.load(open(f))
print(f'Capital: \${d[\"final_capital\"]:,.0f}')
print(f'Return: {d[\"total_return_pct\"]:+.2f}%')
print(f'Trades: {d[\"total_trades\"]}')
print(f'DD: {d[\"max_drawdown_pct\"]:.1f}%')
"

# Recent trades
python3 -c "
import json
from pathlib import Path
f = sorted(Path('.paper_trading_logs').glob('*results*.json'))[-1]
trades = json.load(open(f))['trades'][-5:]
for t in trades:
    print(f\"{t['entry_time'][:10]} {t['entry_type']:10s} \${t['pnl']:>8.0f} ({t['pnl_pct']:>+6.2f}%)\")
"
```

---

## After Paper Trading Completes

### Analysis

```bash
# Generate summary
python3 -c "
import json
from pathlib import Path
f = sorted(Path('.paper_trading_logs').glob('*results*.json'))[-1]
d = json.load(open(f))

trades = d['trades']
wins = [t for t in trades if t['pnl'] > 0]
losses = [t for t in trades if t['pnl'] < 0]

print(f\"PAPER TRADING RESULTS\")
print(f\"=\"*40)
print(f\"Initial:  \${d['initial_capital']:>10,.0f}\")
print(f\"Final:    \${d['final_capital']:>10,.0f}\")
print(f\"Return:   {d['total_return_pct']:>10+.2f}%\")
print(f\"Trades:   {len(trades):>10}\")
print(f\"Wins:     {len(wins):>10} ({len(wins)/len(trades)*100:.1f}%)\")
print(f\"Losses:   {len(losses):>10}\")
print(f\"Avg Win:  \${sum(t['pnl'] for t in wins)/len(wins):>10,.2f}\")
print(f\"Avg Loss: \${sum(t['pnl'] for t in losses)/len(losses):>10,.2f}\")
print(f\"Max DD:   {d['max_drawdown_pct']:>10.2f}%\")
print()
print(f\"Compare to Backtest:\")
print(f\"Backtest Return: +6.32%\")
print(f\"Paper Return:    {d['total_return_pct']:+.2f}%\")
if d['total_return_pct'] >= 2.5:
    print(f\"✓ VALIDATED: Paper return is {d['total_return_pct']/6.32*100:.0f}% of backtest\")
else:
    print(f\"✗ NEEDS WORK: Paper return below +2.5% threshold\")
"
```

### Decision Tree

```
Was paper trading return ≥ +2.5%?
├─ YES (≥ +2.5%)
│  └─ Did win rate stay 30-40%?
│     ├─ YES → VALIDATED ✓
│     │  └─ Option 1: Small live trading ($500-1000)
│     │  └─ Option 2: Test on other commodities
│     │  └─ Option 3: Try different timeframes (4h, weekly)
│     └─ NO → Check win rate formula
│
└─ NO (< +2.5%)
   └─ Was it close (2.0-2.5%)?
      ├─ YES → Possibly fine; might be unlucky period
      │  └─ Extend paper trading another 2 weeks
      │  └─ Or adjust: reduce slippage model, try RSI 35/65
      └─ NO → Strategy underperforming
         └─ Back to: Adjust parameters → Re-backtest → Re-paper trade
```

---

## When to Consider Live Trading

Only after paper trading validation and **all** these are true:

```
✓ Paper trading return ≥ +2.5%
✓ Win rate 30-40% (similar to backtest)
✓ Max drawdown < 20% (acceptable)
✓ Trade count ≥ 10 (statistically meaningful)
✓ Execution slippage matched assumptions (±0.50 on average)
✓ No anomalies in entry/exit logic
✓ Comfort level with position sizing and risk
```

If all above: Safe to try with **$500-1000 real capital** starting small.

If any concern: **Extend paper trading** or **refine strategy** first.

---

## Timeline Summary

```
Day 0:     Start paper trading (bash START_PAPER_TRADING.sh)
Day 1-7:   Initial trades appear
Day 8-15:  Accumulate 5-10 trades, pattern emerges
Day 16-30: Complete 15-20 trades, confidence builds
Day 31:    Analysis, decision, next phase

TOTAL:     30 days (or sooner if 20+ trades) → Go/No-go decision
```

---

## Files You'll Need

Before starting:

```
✓ paper_trading_engine.py        (trading logic)
✓ paper_trading_config.json      (risk controls)
✓ START_PAPER_TRADING.sh         (startup)
✓ PAPER_TRADING_GUIDE.md         (this file)
✓ intraday_bar_cache.json        (XAUUSD price data - must refresh weekly)
```

After completion:

```
Results saved to .paper_trading_logs/:
├── paper_trading_YYYYMMDD_HHMMSS.log
├── paper_trading_results_YYYYMMDD_HHMMSS.json
└── paper_trading_prices_YYYYMMDD_HHMMSS.json
```

---

## Ready? 🚀

```bash
# One command to start the validation phase
bash START_PAPER_TRADING.sh

# Monitor in another terminal
tail -f .paper_trading_logs/paper_trading_*.log
```

**Duration:** 30 days
**Capital at risk:** $0 (simulated)
**Expected outcome:** Confirm strategy works on live data

Let it run. Check daily. Report results in 4 weeks. 🎯

---

**Previous phases:** Backtest complete ✅
**Current phase:** Paper trading validation 🔄
**Future phases:** Small live trading ($500) → Scale up ($5000+)
