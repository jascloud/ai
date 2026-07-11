#!/usr/bin/env python3
"""
Simple Mean Reversion Strategy
Commodity: XAUUSD (Gold)
Timeframe: 1-hour bars
Win Rate Target: 20-40%

Strategy: Buy oversold (RSI < 30), Sell overbought (RSI > 70)
Exit: At moving average or opposite signal
"""

import json
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class MeanReversionStrategy:
    """Simple Mean Reversion using RSI"""

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
        """Calculate RSI"""
        rsi_values = [None] * len(prices)
        if len(prices) < period + 1:
            return rsi_values

        for i in range(period, len(prices)):
            gains = sum(max(0, prices[j+1] - prices[j]) for j in range(i - period, i))
            losses = sum(max(0, prices[j] - prices[j+1]) for j in range(i - period, i))

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
    def calculate_sma(prices: List[float], period: int = 20) -> List[Optional[float]]:
        """Calculate Simple Moving Average"""
        sma_values = [None] * len(prices)
        if len(prices) < period:
            return sma_values

        for i in range(period - 1, len(prices)):
            sma_values[i] = statistics.mean(prices[i - period + 1:i + 1])

        return sma_values

    @staticmethod
    def calculate_atr(bars: List[Dict[str, Any]], period: int = 14) -> List[Optional[float]]:
        """Calculate ATR"""
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

    def run_backtest(self) -> Dict[str, Any]:
        """Run the mean reversion backtest"""
        if len(self.bars) < 100:
            return {"error": f"Not enough bars: {len(self.bars)} < 100"}

        closes = [bar['c'] for bar in self.bars]
        rsi_vals = self.calculate_rsi(closes, period=14)
        sma_vals = self.calculate_sma(closes, period=20)
        atr_vals = self.calculate_atr(self.bars, period=14)

        # Trading loop
        for i in range(50, len(self.bars)):
            bar = self.bars[i]
            price = bar['c']
            bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

            rsi = rsi_vals[i]
            sma = sma_vals[i]
            atr = atr_vals[i]

            if rsi is None or sma is None or atr is None:
                continue

            # BUY Signal: RSI < 30 (oversold)
            if not self.position and rsi < 30:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'mean_reversion_buy',
                    'stop_loss': price - (atr * 2.5),
                    'take_profit': price + (atr * 2.5),
                }

            # SELL Signal: RSI > 70 (overbought)
            elif not self.position and rsi > 70:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'mean_reversion_sell',
                    'stop_loss': price + (atr * 2.5),
                    'take_profit': price - (atr * 2.5),
                }

            # Exit logic
            elif self.position:
                entry_type = self.position['entry_type']
                entry_price = self.position['entry_price']

                if entry_type == 'mean_reversion_buy':
                    # Exit on TP, SL, or RSI > 50 reversal
                    if price >= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price <= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif rsi > 50:  # Mean reversion complete
                        exit_reason = 'mean_reversion_complete'
                    else:
                        exit_reason = None

                else:  # mean_reversion_sell
                    if price <= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price >= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif rsi < 50:  # Mean reversion complete
                        exit_reason = 'mean_reversion_complete'
                    else:
                        exit_reason = None

                if exit_reason:
                    pnl = price - entry_price if entry_type == 'mean_reversion_buy' else entry_price - price
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
                        'rsi_entry': round(rsi_vals[self.position['entry_idx']], 1),
                        'rsi_exit': round(rsi, 1),
                    }
                    self.trades.append(trade)
                    self.position = None
                    self.equity_curve.append(self.current_capital)

        # Close any open position
        if self.position:
            entry_price = self.position['entry_price']
            last_bar = self.bars[-1]
            exit_price = last_bar['c']
            entry_type = self.position['entry_type']

            pnl = exit_price - entry_price if entry_type == 'mean_reversion_buy' else entry_price - exit_price
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
                'rsi_entry': round(rsi_vals[self.position['entry_idx']], 1),
                'rsi_exit': round(rsi_vals[-1], 1),
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

        buy_trades = [t for t in self.trades if t['entry_type'] == 'mean_reversion_buy']
        sell_trades = [t for t in self.trades if t['entry_type'] == 'mean_reversion_sell']

        avg_winning = statistics.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_losing = statistics.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        total_wins_pnl = sum([t['pnl'] for t in winning_trades])
        total_losses_pnl = sum([t['pnl'] for t in losing_trades])
        profit_factor = abs(total_wins_pnl / total_losses_pnl) if total_losses_pnl != 0 else 0

        return {
            'symbol': self.symbol,
            'strategy': 'Mean Reversion (RSI-based)',
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
    print("MEAN REVERSION STRATEGY (RSI-Based)")
    print("Commodity: XAUUSD (Gold)")
    print("Timeframe: 1-hour bars")
    print("Entry: RSI < 30 (BUY) or RSI > 70 (SELL)")
    print("Exit: Mean reversion, Take profit, or Stop loss")
    print("Target Win Rate: 20-40%")
    print("="*80)

    try:
        with open('intraday_bar_cache.json', 'r') as f:
            cache = json.load(f)
            xauusd_bars = cache['XAUUSD']['bars']
            print(f"\n✓ Loaded {len(xauusd_bars)} real 1-hour bars for XAUUSD")
    except Exception as e:
        print(f"\n✗ Error loading cache: {e}")
        return

    tester = MeanReversionStrategy('XAUUSD', xauusd_bars, initial_capital=10000)
    result = tester.run_backtest()

    # Results
    print(f"\n{'='*80}")
    print("BACKTEST RESULTS")
    print(f"{'='*80}")
    print(f"\nSymbol: {result['symbol']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Period: {result['backtest_bars']} 1-hour bars (~{result['backtest_bars']//24} days)")

    print(f"\n💰 CAPITAL PERFORMANCE:")
    print(f"  Initial: ${result['initial_capital']:,.2f}")
    print(f"  Final:   ${result['final_capital']:,.2f}")
    print(f"  Return:  {result['total_return_pct']:+.2f}%")

    print(f"\n📊 TRADE STATISTICS:")
    print(f"  Total Trades: {result['num_trades']}")
    print(f"  Buy (Oversold):  {result['buy_trades']}")
    print(f"  Sell (Overbought): {result['sell_trades']}")
    print(f"  Wins:   {result['winning_trades']}")
    print(f"  Losses: {result['losing_trades']}")

    win_status = "✓ TARGET HIT" if 20 <= result['win_rate_pct'] <= 40 else "⚠️  OUTSIDE TARGET"
    print(f"  Win Rate: {result['win_rate_pct']:.1f}% [{win_status}]")

    print(f"\n💵 TRADE SIZING:")
    print(f"  Avg Win:  ${result['avg_win']:+,.2f}")
    print(f"  Avg Loss: ${result['avg_loss']:+,.2f}")
    print(f"  P/F Ratio: {result['profit_factor']:.2f}x (target: > 1.5x)")

    print(f"\n📉 RISK:")
    print(f"  Max Drawdown: {result['max_drawdown_pct']:.2f}%")

    # All trades
    print(f"\n{'='*80}")
    print(f"ALL TRADES ({result['num_trades']} total)")
    print(f"{'='*80}\n")

    for idx, trade in enumerate(result['trades'], 1):
        signal = "BUY " if trade['entry_type'] == 'mean_reversion_buy' else "SELL"
        status = "✓" if trade['pnl'] > 0 else "✗"

        print(f"{idx:2d}. {signal} | Entry: {trade['entry_time'][:16]} @ ${trade['entry_price']:>8.2f} (RSI {trade['rsi_entry']:>5.1f})")
        print(f"    Exit: {trade['exit_time'][:16]} @ ${trade['exit_price']:>8.2f} (RSI {trade['rsi_exit']:>5.1f})")
        print(f"    P&L: ${trade['pnl']:>8.2f} ({trade['pnl_pct']:>+6.2f}%) [{status}] | Hold: {trade['bars_held']}h | {trade['exit_reason']}\n")

    # Summary metrics
    print(f"{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}\n")

    if result['num_trades'] > 0:
        sorted_trades = sorted(result['trades'], key=lambda x: x['pnl'], reverse=True)
        print(f"Best Trade:  {sorted_trades[0]['entry_type']:21s} | {sorted_trades[0]['pnl_pct']:>+6.2f}% | ${sorted_trades[0]['pnl']:>8.2f}")
        print(f"Worst Trade: {sorted_trades[-1]['entry_type']:21s} | {sorted_trades[-1]['pnl_pct']:>+6.2f}% | ${sorted_trades[-1]['pnl']:>8.2f}")

        durations = [t['bars_held'] for t in result['trades']]
        print(f"\nAvg Hold Time: {statistics.mean(durations):.1f} hours")
        print(f"Min Hold Time: {min(durations)} hours")
        print(f"Max Hold Time: {max(durations)} hours")

        # Win/Loss streak analysis
        consecutive_wins = 0
        max_consecutive = 0
        current_streak = 0
        for trade in result['trades']:
            if trade['pnl'] > 0:
                current_streak += 1
                max_consecutive = max(max_consecutive, current_streak)
            else:
                current_streak = 0

        print(f"\nLongest Win Streak: {max_consecutive} trades")

    # Save
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'strategy': 'Mean Reversion (RSI-Based)',
        'commodity': 'XAUUSD (Gold)',
        'timeframe': '1-hour',
        'target_win_rate': '20-40%',
        'result': result
    }

    with open('mean_reversion_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to mean_reversion_results.json")


if __name__ == '__main__':
    main()
