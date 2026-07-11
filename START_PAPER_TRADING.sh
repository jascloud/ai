#!/bin/bash
#
# Paper Trading Engine Startup Script
# Runs the optimized mean reversion strategy on live market data
# with simulated execution (no real money at risk)
#
# Usage: bash START_PAPER_TRADING.sh [duration_days]
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PAPER TRADING ENGINE - STARTUP${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi

# Verify required files exist
echo "Checking dependencies..."

if [ ! -f "paper_trading_engine.py" ]; then
    echo -e "${RED}ERROR: paper_trading_engine.py not found${NC}"
    exit 1
fi

if [ ! -f "paper_trading_config.json" ]; then
    echo -e "${RED}ERROR: paper_trading_config.json not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies verified${NC}"
echo ""

# Check price data
echo "Checking price data..."
if [ ! -f "intraday_bar_cache.json" ]; then
    echo -e "${YELLOW}⚠️  IMPORTANT: intraday_bar_cache.json not found${NC}"
    echo "   This file should contain real IBKR price data"
    echo "   Without it, paper trading will fail"
    echo ""
    echo -e "${YELLOW}OPTIONS:${NC}"
    echo "   1. Fetch from IBKR: Use /scripts/build_ibkr_price_cache.py"
    echo "   2. Use cached backup: Check ~/.tradingagents/cache/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create log directory
mkdir -p .paper_trading_logs
echo -e "${GREEN}✓ Created .paper_trading_logs directory${NC}"
echo ""

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo "  Symbol:            XAUUSD (Gold)"
echo "  Initial Capital:   \$10,000 (SIMULATED)"
echo "  Daily Loss Limit:  \$200 (-2%)"
echo "  Max Position:      \$500 (5%)"
echo "  Duration:          30 days (or 20+ trades)"
echo "  Strategy:          Optimized Mean Reversion (RSI 30/70)"
echo "  Timeframe:         Daily (NYSE close)"
echo ""

# Display risk warnings
echo -e "${YELLOW}RISK WARNINGS:${NC}"
echo "  ⚠️  This is PAPER TRADING (simulated, no real money)"
echo "  ⚠️  Backtest ≠ Live Performance (slippage, spreads, gaps)"
echo "  ⚠️  Strategy may underperform in trending markets"
echo "  ⚠️  Monitor daily for anomalies"
echo ""

# Ask for confirmation
echo -e "${YELLOW}Ready to start?${NC}"
read -p "Confirm (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo -e "${GREEN}Starting paper trading engine...${NC}"
echo "Logs will be saved to: .paper_trading_logs/"
echo ""
echo "To monitor progress:"
echo "  tail -f .paper_trading_logs/paper_trading_*.log"
echo ""
echo "Press Ctrl+C to stop trading"
echo ""

# Start the engine
python3 paper_trading_engine.py

echo ""
echo -e "${GREEN}Paper trading session complete!${NC}"
echo "Results saved to: .paper_trading_logs/"
echo ""
echo "Next steps:"
echo "  1. Review results: cat .paper_trading_logs/paper_trading_results_*.json"
echo "  2. Compare vs backtest: diff optimization results vs paper trading"
echo "  3. If validated, consider small live trading with limits"
echo ""
