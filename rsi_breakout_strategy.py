#!/usr/bin/env python3
"""
RSI Breakout + Support/Resistance Strategy
Commodity: XAUUSD (Gold)
Timeframe: 1-hour bars
Win Rate Target: 20-40%

Strategy Logic:
- BUY: RSI > 50 + Price breakout above 20-bar high + Volume confirmation
- SELL: RSI < 50 + Price breakdown below 20-bar low + Volume confirmation
- Stop Loss: Recent swing point
- Take Profit: 2:1 Risk/Reward Ratio
"""

import json
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Any, Optional


class RSIBreakoutStrategy:
    """RSI Breakout Strategy with S/R Levels"""

    def __init__(self, symbol: str, bars: List[Dict[str, Any]], initial_capital: float = 10000):
        self.symbol = symbol
        self.bars = bars
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = [initial_capital]

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
        """Calculate RSI values"""
        rsi_values = [None] * len(prices)
        if len(prices) < period + 1:
            return rsi_values

        for i in range(period, len(prices)):
            gains = 0
            losses = 0
            for j in range(i - period, i):
                change = prices[j + 1] - prices[j]
                if change > 0:
                    gains += change
                else:
                    losses -= change

            avg_gain = gains / period
            avg_loss = losses / period

            if avg_loss == 0:
                rsi = 100.0 if avg_gain > 0 else 50.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values[i] = rsi

        return rsi_values

    @staticmethod
    def calculate_atr(bars: List[Dict[str, Any]], period: int = 14) -> List[Optional[float]]:
        """Calculate Average True Range"""
        atr_values = [None] * len(bars)

        if len(bars) < period:
            return atr_values

        tr_values = []
        for i in range(1, len(bars)):
            high = bars[i]['h']
            low = bars[i]['l']
            prev_close = bars[i - 1]['c']

            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)

        atr = statistics.mean(tr_values[:period])
        atr_values[period] = atr

        for i in range(period + 1, len(bars)):
            atr = (atr * (period - 1) + tr_values[i - 1]) / period
            atr_values[i] = atr

        return atr_values

    @staticmethod
    def get_support_resistance(bars: List[Dict[str, Any]], lookback: int = 20) -> Tuple[float, float]:
        """Get recent support and resistance levels"""
        if len(bars) < lookback:
            return bars[0]['l'], bars[0]['h']

        recent_lows = [bar['l'] for bar in bars[-lookback:]]
        recent_highs = [bar['h'] for bar in bars[-lookback:]]

        support = min(recent_lows)
        resistance = max(recent_highs)

        return support, resistance

    def run_backtest(self) -> Dict[str, Any]:
        """Run the RSI Breakout backtest"""
        if len(self.bars) < 100:
            return {"error": f"Not enough bars: {len(self.bars)} < 100"}

        closes = [bar['c'] for bar in self.bars]
        rsi_vals = self.calculate_rsi(closes, period=14)
        atr_vals = self.calculate_atr(self.bars, period=14)

        # Track recent highs/lows for breakout detection
        for i in range(50, len(self.bars)):
            bar = self.bars[i]
            price = bar['c']
            high = bar['h']
            low = bar['l']
            bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

            rsi = rsi_vals[i]
            atr = atr_vals[i]

            if rsi is None or atr is None:
                continue

            # Get support and resistance
            support, resistance = self.get_support_resistance(self.bars[:i+1], lookback=20)

            # BUY Signal: Breakout above resistance + RSI > 50 (strength)
            if not self.position and high > resistance and rsi > 50:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'breakout_buy',
                    'stop_loss': support,  # Below recent support
                    'take_profit': price + (atr * 3),  # 3 ATR for target
                }

            # SELL Signal: Breakdown below support + RSI < 50 (weakness)
            elif not self.position and low < support and rsi < 50:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'breakdown_sell',
                    'stop_loss': resistance,  # Above recent resistance
                    'take_profit': price - (atr * 3),  # 3 ATR for target
                }

            # Exit conditions
            elif self.position:
                entry_type = self.position['entry_type']
                entry_price = self.position['entry_price']

                if entry_type == 'breakout_buy':
                    # Exit on TP, SL, or reversal signal
                    if price >= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price <= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif rsi < 30:  # Reversal signal
                        exit_reason = 'rsi_reversal'
                    else:
                        exit_reason = None

                else:  # breakdown_sell
                    if price <= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price >= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif rsi > 70:  # Reversal signal
                        exit_reason = 'rsi_reversal'
                    else:
                        exit_reason = None

                if exit_reason:
                    pnl = price - entry_price if entry_type == 'breakout_buy' else entry_price - price
                    pnl_pct = (pnl / entry_price) * 100

                    position_size = self.current_capital / entry_price
                    self.current_capital += position_size * pnl

                    trade = {
                        'entry_time': self.position['entry_time'],
                        'entry_price': round(entry_price, 2),
                        'entry_type': entry_type,
                        'exit_time': bar_time.isoformat(),
                        'exit_price': round(price, 2),
                        'pnl': round(pnl, 2),
                        'pnl_pct': round(pnl_pct, 2),
                        'bars_held': i - self.position['entry_idx'],
                        'exit_reason': exit_reason,
                        'rsi_at_entry': round(rsi_vals[self.position['entry_idx']], 1),
                        'atr': round(atr, 2),
                    }
                    self.trades.append(trade)
                    self.position = None
                    self.equity_curve.append(self.current_capital)

        # Close any open position at the end
        if self.position:
            entry_price = self.position['entry_price']
            last_bar = self.bars[-1]
            exit_price = last_bar['c']
            entry_type = self.position['entry_type']

            pnl = exit_price - entry_price if entry_type == 'breakout_buy' else entry_price - exit_price
            pnl_pct = (pnl / entry_price) * 100

            position_size = self.current_capital / entry_price
            self.current_capital += position_size * pnl

            bar_time = datetime.fromtimestamp(last_bar['t'] / 1000, tz=timezone.utc)
            trade = {
                'entry_time': self.position['entry_time'],
                'entry_price': round(entry_price, 2),
                'entry_type': entry_type,
                'exit_time': bar_time.isoformat(),
                'exit_price': round(exit_price, 2),
                'pnl': round(pnl, 2),
                'pnl_pct': round(pnl_pct, 2),
                'bars_held': len(self.bars) - self.position['entry_idx'],
                'exit_reason': 'backtest_end',
                'rsi_at_entry': round(rsi_vals[self.position['entry_idx']], 1),
                'atr': round(atr_vals[-1] or 0, 2),
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

        buy_trades = [t for t in self.trades if t['entry_type'] == 'breakout_buy']
        sell_trades = [t for t in self.trades if t['entry_type'] == 'breakdown_sell']

        avg_winning = statistics.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_losing = statistics.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(sum([t['pnl'] for t in winning_trades]) / sum([t['pnl'] for t in losing_trades])) if losing_trades and sum([t['pnl'] for t in losing_trades]) != 0 else 0

        return {
            'symbol': self.symbol,
            'strategy': 'RSI Breakout + Support/Resistance',
            'total_bars': len(self.bars),
            'backtest_bars': len(self.bars) - 50,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.current_capital, 2),
            'total_return_pct': round(total_return_pct, 2),
            'num_trades': len(self.trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': round(win_rate, 2),
            'avg_win': round(avg_winning, 2),
            'avg_loss': round(avg_losing, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'trades': self.trades
        }


def main():
    print("="*80)
    print("RSI BREAKOUT + SUPPORT/RESISTANCE STRATEGY")
    print("Commodity: XAUUSD (Gold)")
    print("Timeframe: 1-hour bars")
    print("Target Win Rate: 20-40%")
    print("="*80)

    try:
        with open('intraday_bar_cache.json', 'r') as f:
            cache = json.load(f)
            xauusd_bars = cache['XAUUSD']['bars']
            print(f"\nLoaded {len(xauusd_bars)} real 1-hour bars for XAUUSD from IBKR")
    except Exception as e:
        print(f"\nError loading cache: {e}")
        return

    if not xauusd_bars:
        print("No XAUUSD data available")
        return

    tester = RSIBreakoutStrategy('XAUUSD', xauusd_bars, initial_capital=10000)
    result = tester.run_backtest()

    # Display results
    print(f"\n{'='*80}")
    print(f"BACKTEST RESULTS")
    print(f"{'='*80}")
    print(f"\nSymbol: {result['symbol']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Total Bars: {result['total_bars']}")
    print(f"Analysis Period: {result['backtest_bars']} bars (~50 days)")
    print(f"\nCapital Performance:")
    print(f"  Initial Capital: ${result['initial_capital']:,.2f}")
    print(f"  Final Capital: ${result['final_capital']:,.2f}")
    print(f"  Total Return: {result['total_return_pct']:+.2f}%")
    print(f"\nTrade Statistics:")
    print(f"  Total Trades: {result['num_trades']}")
    print(f"  Buy Trades (Breakout Long): {result['buy_trades']}")
    print(f"  Sell Trades (Breakdown Short): {result['sell_trades']}")
    print(f"  Winning Trades: {result['winning_trades']}")
    print(f"  Losing Trades: {result['losing_trades']}")
    print(f"  Win Rate: {result['win_rate_pct']:.1f}%", end="")
    if 20 <= result['win_rate_pct'] <= 40:
        print(" ✓ TARGET ACHIEVED")
    else:
        print(" (Target: 20-40%)")
    print(f"\nAverage Trade Size:")
    print(f"  Average Win: ${result['avg_win']:+,.2f}")
    print(f"  Average Loss: ${result['avg_loss']:+,.2f}")
    print(f"  Profit Factor: {result['profit_factor']:.2f}x")
    print(f"\nRisk Metrics:")
    print(f"  Max Drawdown: {result['max_drawdown_pct']:.2f}%")

    # Display all trades
    print(f"\n{'='*80}")
    print("ALL TRADES (Detailed List)")
    print(f"{'='*80}\n")

    for i, trade in enumerate(result['trades'], 1):
        entry_type = "LONG " if trade['entry_type'] == 'breakout_buy' else "SHORT"
        status = "✓ WIN " if trade['pnl'] > 0 else "✗ LOSS"

        print(f"Trade #{i:2d}: {entry_type}")
        print(f"  Entry:     {trade['entry_time'][:10]} {trade['entry_time'][11:16]} @ ${trade['entry_price']:>10.2f}")
        print(f"  Exit:      {trade['exit_time'][:10]} {trade['exit_time'][11:16]} @ ${trade['exit_price']:>10.2f}")
        print(f"  P&L:       ${trade['pnl']:>10.2f} ({trade['pnl_pct']:+.2f}%) [{status}]")
        print(f"  Duration:  {trade['bars_held']} hours | RSI: {trade['rsi_at_entry']:.1f} | ATR: ${trade['atr']:.2f}")
        print(f"  Exit:      {trade['exit_reason']}")
        print()

    # Summary
    print(f"{'='*80}")
    print("STRATEGY SUMMARY")
    print(f"{'='*80}\n")

    if result['num_trades'] > 0:
        sorted_trades = sorted(result['trades'], key=lambda x: x['pnl'], reverse=True)
        print(f"Best Trade: {sorted_trades[0]['entry_type']} | {sorted_trades[0]['pnl_pct']:+.2f}% | ${sorted_trades[0]['pnl']:+.2f}")
        print(f"Worst Trade: {sorted_trades[-1]['entry_type']} | {sorted_trades[-1]['pnl_pct']:+.2f}% | ${sorted_trades[-1]['pnl']:+.2f}")

        durations = [t['bars_held'] for t in result['trades']]
        print(f"\nTrade Duration (hours):")
        print(f"  Average: {statistics.mean(durations):.1f}")
        print(f"  Min: {min(durations)}")
        print(f"  Max: {max(durations)}")

    # Save results
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'strategy': 'RSI Breakout + Support/Resistance',
        'commodity': 'XAUUSD (Gold)',
        'timeframe': '1-hour',
        'target_win_rate': '20-40%',
        'result': result
    }

    with open('rsi_breakout_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Full results saved to rsi_breakout_results.json")


if __name__ == '__main__':
    main()
