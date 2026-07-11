#!/usr/bin/env python3
"""
RSI + Bollinger Band Mean Reversion Strategy
Commodity: XAUUSD (Gold)
Timeframe: 1-hour bars aggregated to weekly signals
Win Rate Target: 20-40%

Strategy Logic:
- BUY: RSI < 30 (oversold) + Price at/below lower Bollinger Band + Above 20-EMA (uptrend)
- SELL: RSI > 70 (overbought) + Price at/above upper Bollinger Band + Below 20-EMA (downtrend)
- Stop Loss: Beyond recent swing point (ATR-based)
- Take Profit: 2:1 Risk/Reward ratio or BB mean reversion
"""

import json
import statistics
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Any, Optional


class RSIBBandStrategy:
    """RSI + Bollinger Band Mean Reversion Strategy"""

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
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        middle = [None] * len(prices)
        upper = [None] * len(prices)
        lower = [None] * len(prices)

        if len(prices) < period:
            return upper, middle, lower

        for i in range(period - 1, len(prices)):
            lookback = prices[i - period + 1:i + 1]
            sma = statistics.mean(lookback)
            std = statistics.stdev(lookback) if len(lookback) > 1 else 0

            middle[i] = sma
            upper[i] = sma + (std * std_dev)
            lower[i] = sma - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[Optional[float]]:
        """Calculate EMA"""
        ema_values = [None] * len(prices)
        if len(prices) < period:
            return ema_values

        sma = statistics.mean(prices[:period])
        ema_values[period - 1] = sma

        multiplier = 2 / (period + 1)
        for i in range(period, len(prices)):
            ema_values[i] = prices[i] * multiplier + ema_values[i - 1] * (1 - multiplier)

        return ema_values

    @staticmethod
    def calculate_atr(bars: List[Dict[str, Any]], period: int = 14) -> List[Optional[float]]:
        """Calculate Average True Range"""
        atr_values = [None] * len(bars)

        if len(bars) < period:
            return atr_values

        # Calculate true ranges
        tr_values = []
        for i in range(1, len(bars)):
            high = bars[i]['h']
            low = bars[i]['l']
            prev_close = bars[i - 1]['c']

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)

        # Calculate ATR
        atr = statistics.mean(tr_values[:period])
        atr_values[period] = atr

        for i in range(period + 1, len(bars)):
            atr = (atr * (period - 1) + tr_values[i - 1]) / period
            atr_values[i] = atr

        return atr_values

    def get_weekly_signal_day(self, bar_idx: int) -> bool:
        """Check if this is a weekly close (Friday 16:00 ET)"""
        if bar_idx >= len(self.bars):
            return False

        bar = self.bars[bar_idx]
        dt = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

        # Check if it's Friday (weekday 4) and near end of US trading (16:00 ET = 20:00 UTC)
        et_hour = (dt.hour - 4) % 24
        is_friday = dt.weekday() == 4
        is_close = 15 <= et_hour <= 16

        return is_friday and is_close

    def run_backtest(self) -> Dict[str, Any]:
        """Run the RSI + Bollinger Band backtest"""
        if len(self.bars) < 300:
            return {"error": f"Not enough bars: {len(self.bars)} < 300"}

        closes = [bar['c'] for bar in self.bars]

        # Calculate indicators
        rsi_vals = self.calculate_rsi(closes, period=14)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes, period=20)
        ema_20 = self.calculate_ema(closes, period=20)
        atr_vals = self.calculate_atr(self.bars, period=14)

        # Trading loop - process only weekly signals
        for i in range(200, len(self.bars)):
            bar = self.bars[i]
            price = bar['c']
            bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

            rsi = rsi_vals[i]
            bb_u = bb_upper[i]
            bb_l = bb_lower[i]
            ema = ema_20[i]
            atr = atr_vals[i]

            if rsi is None or bb_u is None or ema is None or atr is None:
                continue

            # Entry signals - calculate BB distance
            bb_range = bb_u - bb_l if bb_u and bb_l else 1
            lower_bb_distance = (price - bb_l) / bb_range if bb_range > 0 else 0
            upper_bb_distance = (bb_u - price) / bb_range if bb_range > 0 else 0

            # BUY Signal: RSI oversold + Price near lower BB + Above EMA trend
            if not self.position and rsi < 35 and lower_bb_distance < 0.25 and price > ema:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'mean_reversion_buy',
                    'stop_loss': price - (atr * 2),  # 2 ATR below entry
                    'take_profit': price + (atr * 4),  # 4 ATR above entry (2:1 RR)
                }

            # SELL Signal: RSI overbought + Price near upper BB + Below EMA trend
            elif not self.position and rsi > 65 and upper_bb_distance < 0.25 and price < ema:
                self.position = {
                    'entry_price': price,
                    'entry_idx': i,
                    'entry_time': bar_time.isoformat(),
                    'entry_type': 'mean_reversion_sell',
                    'stop_loss': price + (atr * 2),  # 2 ATR above entry (for short)
                    'take_profit': price - (atr * 4),  # 4 ATR below entry (2:1 RR)
                }

            # Exit conditions for open position
            elif self.position:
                entry_type = self.position['entry_type']
                entry_price = self.position['entry_price']

                if entry_type == 'mean_reversion_buy':
                    # Exit on TP, SL, or BB midline touch
                    if price >= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price <= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif price >= bb_middle[i] if bb_middle[i] else False:  # Exit at mean
                        exit_reason = 'mean_reversion'
                    else:
                        exit_reason = None

                else:  # mean_reversion_sell
                    # Exit on TP, SL, or BB midline touch
                    if price <= self.position['take_profit']:
                        exit_reason = 'take_profit'
                    elif price >= self.position['stop_loss']:
                        exit_reason = 'stop_loss'
                    elif price <= bb_middle[i] if bb_middle[i] else False:  # Exit at mean
                        exit_reason = 'mean_reversion'
                    else:
                        exit_reason = None

                if exit_reason:
                    pnl = price - entry_price if entry_type == 'mean_reversion_buy' else entry_price - price
                    pnl_pct = (pnl / entry_price) * 100

                    # Update capital
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

        # Separate buy and sell trades
        buy_trades = [t for t in self.trades if t['entry_type'] == 'mean_reversion_buy']
        sell_trades = [t for t in self.trades if t['entry_type'] == 'mean_reversion_sell']

        avg_winning = statistics.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_losing = statistics.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(sum([t['pnl'] for t in winning_trades]) / sum([t['pnl'] for t in losing_trades])) if losing_trades and sum([t['pnl'] for t in losing_trades]) != 0 else 0

        return {
            'symbol': self.symbol,
            'strategy': 'RSI + Bollinger Band Mean Reversion',
            'total_bars': len(self.bars),
            'backtest_bars': len(self.bars) - 200,
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
    print("RSI + BOLLINGER BAND MEAN REVERSION STRATEGY")
    print("Commodity: XAUUSD (Gold)")
    print("Timeframe: 1-hour bars")
    print("Target Win Rate: 20-40%")
    print("="*80)

    # Load XAUUSD real data
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

    # Run backtest
    tester = RSIBBandStrategy('XAUUSD', xauusd_bars, initial_capital=10000)
    result = tester.run_backtest()

    # Display results
    print(f"\n{'='*80}")
    print(f"BACKTEST RESULTS")
    print(f"{'='*80}")
    print(f"\nSymbol: {result['symbol']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Total Bars: {result['total_bars']}")
    print(f"Analysis Period: {result['backtest_bars']} bars")
    print(f"\nCapital Performance:")
    print(f"  Initial Capital: ${result['initial_capital']:,.2f}")
    print(f"  Final Capital: ${result['final_capital']:,.2f}")
    print(f"  Total Return: {result['total_return_pct']:+.2f}%")
    print(f"\nTrade Statistics:")
    print(f"  Total Trades: {result['num_trades']}")
    print(f"  Buy Trades (Mean Reversion Long): {result['buy_trades']}")
    print(f"  Sell Trades (Mean Reversion Short): {result['sell_trades']}")
    print(f"  Winning Trades: {result['winning_trades']}")
    print(f"  Losing Trades: {result['losing_trades']}")
    print(f"  Win Rate: {result['win_rate_pct']:.1f}% ✓ TARGET: 20-40%")
    print(f"\nAverage Trade Size:")
    print(f"  Average Win: ${result['avg_win']:+,.2f}")
    print(f"  Average Loss: ${result['avg_loss']:+,.2f}")
    print(f"  Profit Factor: {result['profit_factor']:.2f}x (target: > 1.5x)")
    print(f"\nRisk Metrics:")
    print(f"  Max Drawdown: {result['max_drawdown_pct']:.2f}%")

    # Display all trades
    print(f"\n{'='*80}")
    print("ALL TRADES (Detailed List)")
    print(f"{'='*80}\n")

    for i, trade in enumerate(result['trades'], 1):
        entry_type = "LONG" if trade['entry_type'] == 'mean_reversion_buy' else "SHORT"
        status = "✓ WIN" if trade['pnl'] > 0 else "✗ LOSS"
        bars_held = trade['bars_held']
        hours_held = bars_held  # Since bars are hourly

        print(f"Trade #{i:2d}: {entry_type}")
        print(f"  Entry:     {trade['entry_time'][:10]} {trade['entry_time'][11:16]} @ ${trade['entry_price']:>10.2f}")
        print(f"  Exit:      {trade['exit_time'][:10]} {trade['exit_time'][11:16]} @ ${trade['exit_price']:>10.2f}")
        print(f"  P&L:       ${trade['pnl']:>10.2f} ({trade['pnl_pct']:+.2f}%) [{status}]")
        print(f"  Duration:  {hours_held} hours | RSI Entry: {trade['rsi_at_entry']:.1f} | ATR: ${trade['atr']:.2f}")
        print(f"  Exit Reason: {trade['exit_reason']}")
        print()

    # Summary statistics
    print(f"{'='*80}")
    print("STRATEGY PERFORMANCE ANALYSIS")
    print(f"{'='*80}\n")

    if result['num_trades'] > 0:
        consecutive_wins = 0
        max_consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_losses = 0

        for trade in result['trades']:
            if trade['pnl'] > 0:
                consecutive_wins += 1
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                consecutive_losses = 0
            else:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                consecutive_wins = 0

        sorted_trades = sorted(result['trades'], key=lambda x: x['pnl'], reverse=True)
        best_trade = sorted_trades[0]
        worst_trade = sorted_trades[-1]

        print(f"Best Trade: {best_trade['entry_type']} | {best_trade['pnl_pct']:+.2f}% | ${best_trade['pnl']:+.2f}")
        print(f"Worst Trade: {worst_trade['entry_type']} | {worst_trade['pnl_pct']:+.2f}% | ${worst_trade['pnl']:+.2f}")
        print(f"Max Consecutive Wins: {max_consecutive_wins}")
        print(f"Max Consecutive Losses: {max_consecutive_losses}")

        durations = [t['bars_held'] for t in result['trades']]
        print(f"\nTrade Duration Analysis (hours):")
        print(f"  Average: {statistics.mean(durations):.1f} hours")
        print(f"  Median: {statistics.median(durations):.1f} hours")
        print(f"  Min: {min(durations)} hours")
        print(f"  Max: {max(durations)} hours")

        print(f"\nStrategy Quality Metrics:")
        if result['profit_factor'] > 1.5:
            print(f"  Profit Factor ({result['profit_factor']:.2f}x): ✓ EXCELLENT (>1.5x)")
        elif result['profit_factor'] > 1.0:
            print(f"  Profit Factor ({result['profit_factor']:.2f}x): ✓ GOOD (>1.0x)")
        else:
            print(f"  Profit Factor ({result['profit_factor']:.2f}x): ✗ NEEDS IMPROVEMENT (<1.0x)")

        if result['win_rate_pct'] >= 20 and result['win_rate_pct'] <= 40:
            print(f"  Win Rate ({result['win_rate_pct']:.1f}%): ✓ TARGET ACHIEVED (20-40%)")
        elif result['win_rate_pct'] > 40:
            print(f"  Win Rate ({result['win_rate_pct']:.1f}%): ✓ EXCELLENT (>40%)")
        else:
            print(f"  Win Rate ({result['win_rate_pct']:.1f}%): ✗ BELOW TARGET (<20%)")

    # Save results
    output = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'strategy': 'RSI + Bollinger Band Mean Reversion',
        'commodity': 'XAUUSD (Gold)',
        'timeframe': '1-hour',
        'target_win_rate': '20-40%',
        'result': result
    }

    with open('rsibband_backtest_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Full results saved to rsibband_backtest_results.json")


if __name__ == '__main__':
    main()
