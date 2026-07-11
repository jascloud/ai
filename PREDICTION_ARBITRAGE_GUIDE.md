# Prediction Market Arbitrage Agent - User Guide

## Overview

Automated scanner for yes/no prediction market arbitrage on **Polymarket** and **Kalshi**.

**What it does:**
- Fetches current prices from both platforms
- Detects cross-platform mispricings (arbitrage opportunities)
- Calculates optimal position sizing using Kelly Criterion
- Displays actionable recommendations with profit estimates

**Capital at risk:** $0 (analysis only, no execution)

---

## Quick Start

### 1. Run the Scanner

```bash
python3 prediction_arbitrage_agent.py
```

### 2. Review Output

The agent will display opportunities ranked by spread:

```
#1 Will Bitcoin reach $100k by EOY 2024?
├─ BUY:  NO  on Polymarket   @ $0.3000
├─ SELL: NO  on Kalshi       @ $0.5500
├─ SPREAD: +83.33% ($+0.2500)
├─ NET PROFIT: $+0.2330
├─ KELLY FRACTION: 12.5%
└─ RECOMMENDED SIZE: $125.00 (12.5% of bankroll)
```

**Translation:**
- Buy NO contracts on Polymarket at $0.30
- Sell those same NO contracts on Kalshi at $0.55
- Profit per contract: $0.23 (after fees)
- Risk position with $125 (12.5% of $1000 bankroll)

### 3. Save Results

Results automatically saved to:
```
prediction_arbitrage_results_YYYYMMDD_HHMMSS.json
```

---

## How It Works

### Arbitrage Detection

**Classic Arbitrage:** YES + NO should sum to $1.00

```
Market A: YES = $0.70, NO = $0.30  (sum = $1.00) ✓
Market B: YES = $0.75, NO = $0.25  (sum = $1.00) ✓

But if same market is priced differently on two platforms:
Platform A: YES = $0.70
Platform B: YES = $0.75

→ Buy on A @ $0.70, Sell on B @ $0.75
→ Profit: $0.05 per contract
```

### Spread Calculation

```
Spread % = (Sell Price - Buy Price) / Buy Price * 100

Example:
- Buy NO @ $0.30
- Sell NO @ $0.55
- Spread = ($0.55 - $0.30) / $0.30 * 100 = 83.33%
```

### Kelly Criterion Sizing

For arbitrage (near-certain win):

```
Kelly Fraction = (Win Amount / Bet Size) * 0.25

Example:
- Bet $0.30, Win $0.23 (after fees)
- Win Ratio = $0.23 / $0.30 = 76.7%
- Kelly = 76.7% * 0.25 = 19.2%

For $1000 bankroll:
- Recommended Size = $1000 * 0.192 = $192
```

**Why 25% of full Kelly?**
- Arbitrage is high-confidence, but market execution risk exists
- Conservative sizing prevents overexposure
- Typical arb positions: 5-20% of bankroll

---

## Configuration

Edit `prediction_arbitrage_agent.py` to adjust:

```python
# Bankroll (starting capital)
agent = PredictionArbitrageAgent(bankroll=1000.0)

# Minimum spread threshold (default 1%)
agent.min_spread_threshold = 1.0

# Number of markets to monitor
.fetch_polymarket_markets(limit=10)  # Default: top 10 by volume
.fetch_kalshi_markets(limit=10)
```

---

## Understanding the Output

### Spread Analysis

```
SPREAD: +83.33% (highest profit margin)
├─ Higher = Better opportunity
├─ Typically 2-10% on liquid markets
└─ >20% = rare, check for execution risks
```

### Fee Impact

```
NET PROFIT = (Sell Price - Buy Price) - Fees

Typical prediction market fees:
├─ Taker fee: 2%
├─ Maker fee: 0-1%
└─ Total per trade: 2-3%
```

### Kelly Fraction

```
KELLY FRACTION: 12.5%
├─ 0-5%: Small position, marginal opportunity
├─ 5-15%: Good position, solid arb
├─ 15-25%: Strong opportunity, high confidence
└─ >25%: Exceptional, but rare
```

---

## Output Example

### Good Opportunity

```
SPREAD: +83.33% ($+0.2500)
NET PROFIT: $+0.2330
KELLY FRACTION: 12.5%
RECOMMENDED SIZE: $125.00
```

**Interpretation:** Buy small ($125), high confidence profit.

### Marginal Opportunity

```
SPREAD: +5.00% ($+0.0200)
NET PROFIT: $+0.0036
KELLY FRACTION: 0.0%
RECOMMENDED SIZE: $0.00
```

**Interpretation:** Too small after fees, skip this one.

---

## Running Continuously

### Option 1: One-off scan

```bash
python3 prediction_arbitrage_agent.py
```

### Option 2: Monitor every hour

```bash
while true; do
    python3 prediction_arbitrage_agent.py
    sleep 3600  # Check every 60 minutes
done
```

### Option 3: Use cron for scheduled runs

```bash
# Add to crontab (every 4 hours)
0 */4 * * * cd /path/to/ai && python3 prediction_arbitrage_agent.py
```

---

## Next Steps: Manual Execution

Once you identify an opportunity:

### 1. Verify on Platforms

```
Go to Polymarket.com
  → Search market title
  → Confirm YES/NO prices match agent output

Go to Kalshi.com
  → Find same market
  → Check current bid/ask
```

### 2. Calculate Position Size

```
Agent recommends: $125 (12.5% of $1000)
Your position:
  - $125 on Polymarket (BUY side)
  - $125 on Kalshi (SELL side)
```

### 3. Execute

```
1. Place buy order on Polymarket (YES or NO as indicated)
2. Immediately place sell order on Kalshi (opposite side)
3. Monitor for fills
```

### 4. Monitor

```
✓ Both orders filled = Locked-in profit
✗ Partial fill = Unhedged exposure
✗ Price moved = Spread closed, cancel unfilled order
```

---

## Risk Management

### Slippage Risk
- Prices move while you're placing orders
- Use limit orders, not market orders
- Tighter spreads (<5%) are riskier

### Execution Risk
- What if one platform fills and other doesn't?
- Recommended: Place both orders within 10 seconds
- Use platforms' APIs if available for faster execution

### Fee Risk
- Agent estimates 2-3% total fees
- Verify actual fees on each platform
- Some platforms offer rebates for makers (0-1%)

### Liquidity Risk
- Large positions may cause slippage
- Keep positions small initially ($50-200)
- Check market depth before entering

---

## Troubleshooting

### No opportunities found

```
Cause: All spreads too small after fees
Solution:
  1. Lower min_spread_threshold (1% → 0.5%)
  2. Expand market coverage (limit=10 → limit=20)
  3. Check if markets are actually mispriced
```

### API connection errors

```
Error: "Tunnel connection failed: 403 Forbidden"
Cause: Outbound HTTPS blocked or API endpoints changed
Solution:
  1. Use demo data (agent falls back automatically)
  2. Check API endpoints (Polymarket/Kalshi may have updated)
  3. Run in environment with internet access
```

### Position too large

```
KELLY FRACTION: 25%+
RECOMMENDED SIZE: >$250
Problem: Over-leveraged for arb
Solution: Reduce position to 5-15% max
```

---

## Results File Format

```json
{
  "timestamp": "2026-07-11T21:18:14...",
  "bankroll": 1000.0,
  "opportunities_found": 3,
  "opportunities": [
    {
      "market": "Will Bitcoin reach $100k by EOY 2024?",
      "buy": "NO on Polymarket",
      "buy_price": 0.3,
      "sell": "NO on Kalshi",
      "sell_price": 0.55,
      "spread_pct": 83.33,
      "net_profit": 0.233,
      "recommended_size": 125.0,
      "kelly_fraction": 0.125
    }
  ]
}
```

---

## FAQ

**Q: Can the agent execute trades automatically?**
A: Not yet. This MVP is analysis-only. Execution requires API keys + authentication.

**Q: What if my actual fees are different?**
A: Edit the agent to adjust fee assumptions (currently 2% taker, 1% maker).

**Q: How often should I scan?**
A: Every 30-60 minutes. Spreads close quickly as algos detect arbs.

**Q: What's the typical win rate?**
A: ~95%+ if properly executed (arbs are near-certain if hedged).

**Q: How much can I make?**
A: Depends on spread size and capital. Example: 5% spread * $10k = $500 profit.

**Q: Is this legal?**
A: Yes. Arbitrage is legal and common on prediction markets.

---

## Next Features (Coming)

- [ ] Automated execution via Polymarket/Kalshi APIs
- [ ] Real-time price monitoring (update every 30s)
- [ ] Slippage simulation (more realistic fill prices)
- [ ] Portfolio balancing (manage multiple concurrent arbs)
- [ ] Performance tracking (realized vs expected profit)
- [ ] Sentiment analysis for market strength signals

---

**Ready to find arbitrage opportunities?**

```bash
python3 prediction_arbitrage_agent.py
```

Good luck! 🎯
