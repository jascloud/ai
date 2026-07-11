#!/usr/bin/env python3
"""
200-day EMA 20/50/100 backtest for XAUUSD, BTC, SPX500
Strategy: Buy when price > 200-EMA, Sell when price < 200-EMA
Timeframe: 1-hour bars
"""

import json
import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Any


class EMABacktester:
    """EMA 20/50/100 strategy backtester for 1-hour timeframes"""

    def __init__(self, symbol: str, bars: List[Dict[str, Any]], initial_capital: float = 10000):
        self.symbol = symbol
        self.bars = bars
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = None  # (entry_price, entry_idx, entry_time)
        self.trades = []
        self.equity_curve = [initial_capital]

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate EMA for a series of prices"""
        if not prices or len(prices) < period:
            return [None] * len(prices)

        ema_values = [None] * len(prices)

        # Start SMA for the first EMA value
        sma = sum(prices[:period]) / period
        ema_values[period - 1] = sma

        # Calculate EMA for subsequent values
        multiplier = 2 / (period + 1)
        for i in range(period, len(prices)):
            ema_values[i] = prices[i] * multiplier + ema_values[i - 1] * (1 - multiplier)

        return ema_values

    def run_backtest(self) -> Dict[str, Any]:
        """Run the EMA backtest"""
        if len(self.bars) < 200:
            return {"error": f"Not enough bars: {len(self.bars)} < 200"}

        # Extract close prices
        closes = [bar['c'] for bar in self.bars]

        # Calculate EMAs
        ema_20 = self.calculate_ema(closes, 20)
        ema_50 = self.calculate_ema(closes, 50)
        ema_100 = self.calculate_ema(closes, 100)
        ema_200 = self.calculate_ema(closes, 200)

        # Trading loop - start from bar 200 (need 200 bars for 200-EMA)
        for i in range(200, len(self.bars)):
            bar = self.bars[i]
            price = bar['c']
            bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

            ema_200_val = ema_200[i]
            if ema_200_val is None:
                continue

            # BUY signal: price crosses above 200-EMA
            if not self.position and price > ema_200_val:
                # Entry signal
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_ema200': ema_200_val,
                }

            # SELL signal: price crosses below 200-EMA
            elif self.position and price < ema_200_val:
                # Exit signal
                entry_price = self.position['entry_price']
                pnl = price - entry_price
                pnl_pct = (pnl / entry_price) * 100

                # Update capital
                position_size = self.current_capital / entry_price
                self.current_capital += position_size * pnl

                trade = {
                    'entry_time': self.position['entry_time'],
                    'entry_price': round(entry_price, 2),
                    'exit_time': bar_time.isoformat(),
                    'exit_price': round(price, 2),
                    'pnl': round(pnl, 2),
                    'pnl_pct': round(pnl_pct, 2),
                    'bars_held': i - self.position['entry_idx'],
                    'exit_reason': 'ema_200_crossbelow'
                }
                self.trades.append(trade)
                self.position = None
                self.equity_curve.append(self.current_capital)

        # Close any open position at the end
        if self.position:
            entry_price = self.position['entry_price']
            last_bar = self.bars[-1]
            exit_price = last_bar['c']
            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100

            position_size = self.current_capital / entry_price
            self.current_capital += position_size * pnl

            bar_time = datetime.fromtimestamp(last_bar['t'] / 1000, tz=timezone.utc)
            trade = {
                'entry_time': self.position['entry_time'],
                'entry_price': round(entry_price, 2),
                'exit_time': bar_time.isoformat(),
                'exit_price': round(exit_price, 2),
                'pnl': round(pnl, 2),
                'pnl_pct': round(pnl_pct, 2),
                'bars_held': len(self.bars) - self.position['entry_idx'],
                'exit_reason': 'backtest_end'
            }
            self.trades.append(trade)
            self.equity_curve.append(self.current_capital)

        # Calculate metrics
        total_return_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        win_rate = (len(winning_trades) / len(self.trades) * 100) if self.trades else 0

        max_drawdown = 0
        peak_capital = self.initial_capital
        for equity in self.equity_curve:
            if equity > peak_capital:
                peak_capital = equity
            drawdown = (peak_capital - equity) / peak_capital * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        avg_trade_return = sum([t['pnl_pct'] for t in self.trades]) / len(self.trades) if self.trades else 0

        return {
            'symbol': self.symbol,
            'total_bars': len(self.bars),
            'backtest_bars': len(self.bars) - 200,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.current_capital, 2),
            'total_return_pct': round(total_return_pct, 2),
            'num_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': round(win_rate, 2),
            'avg_trade_return_pct': round(avg_trade_return, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'trades': self.trades
        }


def generate_synthetic_ohlcv(symbol: str, num_bars: int, start_price: float,
                             start_date: str = "2026-02-01") -> List[Dict[str, Any]]:
    """Generate realistic synthetic OHLCV data"""
    bars = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    price = start_price
    trend = 0.0  # Trend component for more realistic movement

    for i in range(num_bars):
        dt = start_dt + timedelta(hours=i)

        # Skip non-market hours for SPX500
        if symbol == 'SPX500':
            et_hour = (dt.hour - 4) % 24
            if et_hour < 9 or (et_hour == 9 and dt.minute < 30) or et_hour >= 16:
                continue

        # Random walk with trend
        trend = trend * 0.9 + (random.random() - 0.5) * 0.01
        volatility = 0.015 if symbol == 'BTC' else 0.008
        change = trend + (random.random() - 0.5) * volatility * price

        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) * (1 + abs(volatility * 0.5))
        low_p = min(open_p, close_p) * (1 - abs(volatility * 0.5))
        volume = int(1000000 * (0.5 + random.random()))

        bars.append({
            "t": int(dt.timestamp() * 1000),
            "o": round(open_p, 2),
            "h": round(high_p, 2),
            "l": round(low_p, 2),
            "c": round(close_p, 2),
            "v": volume
        })

        price = close_p

    return bars


def main():
    print("="*70)
    print("EMA 20/50/100 200-Day Backtest")
    print("Strategy: Buy > 200-EMA, Sell < 200-EMA")
    print("Timeframe: 1-hour bars")
    print("="*70)

    # Load XAUUSD real data
    try:
        with open('intraday_bar_cache.json', 'r') as f:
            cache = json.load(f)
            xauusd_bars = cache['XAUUSD']['bars']
            print(f"\nXAUUSD: Loaded {len(xauusd_bars)} real 1-hour bars from cache")
    except Exception as e:
        print(f"\nXAUUSD: Error loading cache - {e}")
        xauusd_bars = []

    # Generate synthetic BTC and SPX500 data (realistic starting prices)
    # ~50 days at 24h = 1200 bars, ~35 trading days at 6.5h = 227 bars
    btc_bars = generate_synthetic_ohlcv('BTC', 1200, start_price=45000, start_date="2026-02-01")
    spx_bars = generate_synthetic_ohlcv('SPX500', 1200, start_price=5500, start_date="2026-02-01")

    print(f"BTC: Generated {len(btc_bars)} synthetic 1-hour bars")
    print(f"SPX500: Generated {len(spx_bars)} synthetic 1-hour bars")

    results = {}
    all_trades = {}

    # Run backtests
    for symbol, bars in [('XAUUSD', xauusd_bars), ('BTC', btc_bars), ('SPX500', spx_bars)]:
        if not bars:
            print(f"\n{symbol}: Skipping (no data)")
            continue

        tester = EMABacktester(symbol, bars, initial_capital=10000)
        result = tester.run_backtest()
        results[symbol] = result
        all_trades[symbol] = result.get('trades', [])

        print(f"\n{symbol} Results:")
        print(f"  Total bars: {result['total_bars']}")
        print(f"  Backtest period: {result['backtest_bars']} bars (starting from 200-EMA warmup)")
        print(f"  Initial capital: ${result['initial_capital']:,.2f}")
        print(f"  Final capital: ${result['final_capital']:,.2f}")
        print(f"  Total return: {result['total_return_pct']:+.2f}%")
        print(f"  Trades: {result['num_trades']} (W:{result['winning_trades']} L:{result['losing_trades']})")
        print(f"  Win rate: {result['win_rate_pct']:.1f}%")
        print(f"  Max drawdown: {result['max_drawdown_pct']:.2f}%")

    # Print all trades
    print("\n" + "="*70)
    print("ALL TRADES (Listed by Entry Time)")
    print("="*70)

    all_trade_list = []
    for symbol in ['XAUUSD', 'BTC', 'SPX500']:
        for trade in all_trades.get(symbol, []):
            trade['symbol'] = symbol
            all_trade_list.append(trade)

    # Sort by entry time
    all_trade_list.sort(key=lambda x: x['entry_time'])

    for i, trade in enumerate(all_trade_list, 1):
        symbol = trade['symbol']
        entry_time = trade['entry_time']
        entry_price = trade['entry_price']
        exit_time = trade['exit_time']
        exit_price = trade['exit_price']
        pnl = trade['pnl']
        pnl_pct = trade['pnl_pct']
        exit_reason = trade['exit_reason']
        bars_held = trade['bars_held']

        status = "✓ WIN" if pnl > 0 else "✗ LOSS" if pnl < 0 else "BREAK"

        print(f"\nTrade #{i:3d}: {symbol}")
        print(f"  Entry:     {entry_time[:10]} {entry_time[11:16]} @ ${entry_price:>10.2f}")
        print(f"  Exit:      {exit_time[:10]} {exit_time[11:16]} @ ${exit_price:>10.2f}")
        print(f"  P&L:       ${pnl:>10.2f} ({pnl_pct:+.2f}%) [{status}]")
        print(f"  Duration:  {bars_held} bars")
        print(f"  Reason:    {exit_reason}")

    # Summary statistics across all symbols
    print("\n" + "="*70)
    print("CROSS-SYMBOL SUMMARY")
    print("="*70)

    total_trades = sum(r['num_trades'] for r in results.values())
    total_wins = sum(r['winning_trades'] for r in results.values())
    total_losses = sum(r['losing_trades'] for r in results.values())
    overall_return_pct = sum(t['pnl_pct'] for t in all_trade_list) / len(all_trade_list) if all_trade_list else 0

    print(f"\nTotal trades across all symbols: {total_trades}")
    print(f"  Winning trades: {total_wins}")
    print(f"  Losing trades: {total_losses}")
    print(f"  Win rate: {(total_wins/total_trades*100) if total_trades > 0 else 0:.1f}%")
    print(f"  Average trade return: {overall_return_pct:.2f}%")

    # Save results to JSON
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'strategy': 'EMA 20/50/100',
        'entry_rule': 'Price > 200-EMA',
        'exit_rule': 'Price < 200-EMA',
        'timeframe': '1-hour',
        'results': results,
        'all_trades': all_trade_list
    }

    with open('ema_backtest_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Full results saved to ema_backtest_results.json")


if __name__ == '__main__':
    main()
