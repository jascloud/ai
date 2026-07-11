#!/usr/bin/env python3
"""
Paper Trading Engine for Mean Reversion Strategy
- Connects to live XAUUSD prices (IBKR or cache)
- Simulates execution with realistic spreads
- Tracks equity, P&L, and performance metrics
- Runs continuously for 2-4 week validation
"""

import json
import statistics
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class PaperTradingEngine:
    """Live paper trading simulator with realistic execution"""

    def __init__(self, symbol: str = 'XAUUSD', initial_capital: float = 10000,
                 log_dir: str = '.paper_trading_logs'):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = [initial_capital]
        self.equity_times = [datetime.now(timezone.utc)]
        self.peak_capital = initial_capital
        self.max_drawdown = 0

        # Risk controls
        self.daily_loss_limit = initial_capital * 0.02  # Stop after -2% daily
        self.max_position_size = initial_capital * 0.05  # Max 5% per trade
        self.max_concurrent_positions = 3  # No more than 3 open positions

        # Logging
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

        # Market data cache
        self.daily_prices = {}  # date_key -> {o, h, l, c, t}
        self.last_update = None
        self.price_cache_file = f'paper_trading_prices_{self.session_id}.json'

        # Strategy state
        self.rsi_history = []  # For RSI calculation
        self.price_history = []  # For indicators

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate current RSI from price history"""
        if len(prices) < period + 1:
            return None

        i = len(prices) - 1
        gains = sum(max(0, prices[j+1] - prices[j]) for j in range(i - period, i))
        losses = sum(max(0, prices[j] - prices[j+1]) for j in range(i - period, i))

        avg_gain = gains / period
        avg_loss = losses / period

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_atr(bars: List[Dict[str, float]], period: int = 14) -> Optional[float]:
        """Calculate current ATR"""
        if len(bars) < period:
            return None

        tr_values = []
        for i in range(max(0, len(bars) - period), len(bars)):
            if i == 0:
                tr = bars[i]['h'] - bars[i]['l']
            else:
                high = bars[i]['h']
                low = bars[i]['l']
                prev_close = bars[i-1]['c']
                tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)

        return statistics.mean(tr_values) if tr_values else None

    def simulate_execution(self, price: float, side: str) -> Tuple[float, float]:
        """
        Simulate realistic execution with bid-ask spread
        Gold spread typically 0.50-1.00 USD per ounce
        """
        spread = 0.75  # Mid-point of typical spread
        slippage = 0.25  # Execution slippage

        if side == 'buy':
            # Assume we get worst case (ask price + slippage)
            fill_price = price + (spread / 2) + slippage
        else:  # sell
            # Assume we get worst case (bid price - slippage)
            fill_price = price - (spread / 2) - slippage

        return fill_price, spread + slippage

    def load_or_fetch_prices(self) -> Dict[str, Dict[str, float]]:
        """
        Load prices from cache or fetch from IBKR
        Returns dict of {date_key: {o, h, l, c, t}}
        """
        cache_file = self.log_dir / self.price_cache_file

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.log(f"Loaded {len(data)} cached prices from {cache_file.name}")
                    return data
            except Exception as e:
                self.log(f"Error loading cache: {e}")

        # Try to fetch from intraday_bar_cache.json (most recent IBKR data)
        try:
            with open('intraday_bar_cache.json', 'r') as f:
                cache = json.load(f)
                xauusd_bars = cache.get('XAUUSD', {}).get('bars', [])

                if xauusd_bars:
                    # Convert hourly to daily (take last 30 days)
                    daily_bars = {}
                    for bar in xauusd_bars[-720:]:  # Last ~30 days of hourly bars
                        dt = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)
                        date_key = dt.strftime('%Y-%m-%d')

                        if date_key not in daily_bars:
                            daily_bars[date_key] = {
                                'o': bar['c'],  # Use last price as open for first bar
                                'h': bar['h'],
                                'l': bar['l'],
                                'c': bar['c'],
                                't': bar['t']
                            }
                        else:
                            db = daily_bars[date_key]
                            db['h'] = max(db['h'], bar['h'])
                            db['l'] = min(db['l'], bar['l'])
                            db['c'] = bar['c']
                            db['t'] = bar['t']

                    # Save to cache for faster reload
                    with open(cache_file, 'w') as f:
                        json.dump(daily_bars, f, indent=2)

                    self.log(f"Fetched and cached {len(daily_bars)} daily prices")
                    return daily_bars
        except Exception as e:
            self.log(f"Error fetching from IBKR cache: {e}")

        return {}

    def process_price_update(self, bar: Dict[str, Any]) -> None:
        """
        Process new price bar and execute strategy
        bar format: {date_key, o, h, l, c, t}
        """
        price = bar['c']
        self.price_history.append(price)

        # Calculate indicators
        rsi = self.calculate_rsi(self.price_history, period=14)

        # Build bar list for ATR calculation
        bars_for_atr = []
        for i in range(max(0, len(self.price_history) - 14), len(self.price_history)):
            if i == 0:
                tr = self.price_history[i]
            else:
                tr = self.price_history[i]
            bars_for_atr.append({'h': self.price_history[i], 'l': self.price_history[i], 'c': self.price_history[i]})

        atr = self.calculate_atr(bars_for_atr, period=14) if len(bars_for_atr) >= 14 else None

        if rsi is None or atr is None:
            return

        # Store for logging
        bar_time = datetime.fromtimestamp(bar['t'] / 1000, tz=timezone.utc)

        # Risk control: check daily loss
        daily_loss = self.initial_capital - self.current_capital
        if daily_loss >= self.daily_loss_limit:
            self.log(f"⚠️  DAILY LOSS LIMIT REACHED (${daily_loss:.2f}). Stopping trading.")
            return

        # ENTRY LOGIC
        if not self.position and rsi < 30:
            # BUY Signal
            fill_price, slippage = self.simulate_execution(price, 'buy')
            position_size = min(self.max_position_size, self.current_capital * 0.1)

            self.position = {
                'entry_price': fill_price,
                'entry_idx': len(self.price_history) - 1,
                'entry_time': bar_time.isoformat(),
                'entry_type': 'paper_buy',
                'side': 'buy',
                'stop_loss': fill_price - (atr * 1.5),
                'take_profit': fill_price + (atr * 2.5),
                'position_size': position_size,
                'rsi_entry': rsi,
            }
            self.log(f"BUY Signal: {bar_time.strftime('%Y-%m-%d %H:%M')} | Price: ${price:.2f} | RSI: {rsi:.1f} | Fill: ${fill_price:.2f}")

        elif not self.position and rsi > 70:
            # SELL Signal
            fill_price, slippage = self.simulate_execution(price, 'sell')
            position_size = min(self.max_position_size, self.current_capital * 0.1)

            self.position = {
                'entry_price': fill_price,
                'entry_idx': len(self.price_history) - 1,
                'entry_time': bar_time.isoformat(),
                'entry_type': 'paper_sell',
                'side': 'sell',
                'stop_loss': fill_price + (atr * 1.5),
                'take_profit': fill_price - (atr * 2.5),
                'position_size': position_size,
                'rsi_entry': rsi,
            }
            self.log(f"SELL Signal: {bar_time.strftime('%Y-%m-%d %H:%M')} | Price: ${price:.2f} | RSI: {rsi:.1f} | Fill: ${fill_price:.2f}")

        # EXIT LOGIC
        elif self.position:
            exit_reason = None

            if self.position['side'] == 'buy':
                if price >= self.position['take_profit']:
                    exit_reason = 'take_profit'
                elif price <= self.position['stop_loss']:
                    exit_reason = 'stop_loss'
                elif rsi > 50:
                    exit_reason = 'mean_reversion_complete'
            else:  # sell
                if price <= self.position['take_profit']:
                    exit_reason = 'take_profit'
                elif price >= self.position['stop_loss']:
                    exit_reason = 'stop_loss'
                elif rsi < 50:
                    exit_reason = 'mean_reversion_complete'

            if exit_reason:
                fill_price, slippage = self.simulate_execution(price, 'close')

                pnl = self.position['position_size'] * (fill_price - self.position['entry_price']) if self.position['side'] == 'buy' else \
                      self.position['position_size'] * (self.position['entry_price'] - fill_price)
                pnl_pct = (pnl / (self.position['position_size'] * self.position['entry_price'])) * 100

                self.current_capital += pnl

                trade = {
                    'entry_time': self.position['entry_time'],
                    'entry_price': round(self.position['entry_price'], 2),
                    'entry_type': self.position['entry_type'],
                    'exit_time': bar_time.isoformat(),
                    'exit_price': round(fill_price, 2),
                    'exit_fill_price': round(price, 2),  # Market price at exit
                    'pnl': round(pnl, 2),
                    'pnl_pct': round(pnl_pct, 2),
                    'bars_held': len(self.price_history) - self.position['entry_idx'],
                    'exit_reason': exit_reason,
                    'rsi_entry': round(self.position['rsi_entry'], 1),
                    'rsi_exit': round(rsi, 1),
                    'position_size': round(self.position['position_size'], 2),
                    'slippage': round(slippage, 2),
                }
                self.trades.append(trade)
                self.equity_curve.append(self.current_capital)
                self.equity_times.append(bar_time)

                status = "✓ WIN" if pnl > 0 else "✗ LOSS"
                self.log(f"EXIT: {exit_reason.upper():20s} | P&L: ${pnl:>8.2f} ({pnl_pct:>+6.2f}%) [{status}]")

                self.position = None

        # Update peak and drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        current_dd = (self.peak_capital - self.current_capital) / self.peak_capital * 100
        if current_dd > self.max_drawdown:
            self.max_drawdown = current_dd

    def run_paper_trading_loop(self, interval_minutes: int = 1440) -> None:
        """
        Main loop: fetch prices and execute strategy continuously
        interval_minutes: how often to check for new prices (default 1 day)
        """
        self.log(f"Starting paper trading session for {self.symbol}")
        self.log(f"Initial Capital: ${self.initial_capital:,.2f}")
        self.log(f"Max Position Size: ${self.max_position_size:,.2f} (5%)")
        self.log(f"Daily Loss Limit: ${self.daily_loss_limit:,.2f} (-2%)")
        self.log("")

        prices = self.load_or_fetch_prices()

        if not prices:
            self.log("ERROR: No price data available. Cannot start trading.")
            return

        # Sort by date
        sorted_dates = sorted(prices.keys())
        last_processed_idx = -1

        session_start = datetime.now(timezone.utc)

        try:
            while True:
                current_time = datetime.now(timezone.utc)

                # Check if it's been long enough for next update
                if self.last_update and (current_time - self.last_update).total_seconds() < interval_minutes * 60:
                    time.sleep(60)  # Check again in 1 minute
                    continue

                # Process any new prices
                for i, date_key in enumerate(sorted_dates):
                    if i > last_processed_idx:
                        bar = prices[date_key]
                        bar['date_key'] = date_key
                        self.process_price_update(bar)
                        last_processed_idx = i

                self.last_update = current_time

                # Log status every 5 updates (or daily)
                if len(self.trades) > 0 and len(self.trades) % 5 == 0:
                    self.log_daily_summary()

                # Check if we should continue (e.g., after 2-4 weeks)
                elapsed = (current_time - session_start).days
                if elapsed >= 30:  # 30-day paper trading run
                    self.log(f"30-day paper trading period complete. Stopping.")
                    break

        except KeyboardInterrupt:
            self.log("Paper trading interrupted by user.")
        finally:
            self.finalize_session()

    def log_daily_summary(self) -> None:
        """Log daily performance summary"""
        if not self.trades:
            return

        today_trades = self.trades[-5:]  # Last 5 trades
        today_wins = sum(1 for t in today_trades if t['pnl'] > 0)
        today_pnl = sum(t['pnl'] for t in today_trades)

        self.log(f"\n--- Daily Summary ---")
        self.log(f"Capital: ${self.current_capital:,.2f}")
        self.log(f"Equity Change: {((self.current_capital - self.initial_capital) / self.initial_capital * 100):+.2f}%")
        self.log(f"Max Drawdown: {self.max_drawdown:.2f}%")
        self.log(f"Recent Trades: {len(today_trades)} | Wins: {today_wins} | P&L: ${today_pnl:+.2f}")
        self.log("")

    def finalize_session(self) -> None:
        """Generate final session report"""
        self.log("\n" + "="*80)
        self.log("PAPER TRADING SESSION COMPLETE")
        self.log("="*80)

        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        win_rate = (len(winning_trades) / len(self.trades) * 100) if self.trades else 0

        self.log(f"\nCapital Performance:")
        self.log(f"  Initial: ${self.initial_capital:,.2f}")
        self.log(f"  Final:   ${self.current_capital:,.2f}")
        self.log(f"  Return:  {total_return:+.2f}%")

        self.log(f"\nTrade Statistics:")
        self.log(f"  Total Trades: {len(self.trades)}")
        self.log(f"  Wins:  {len(winning_trades)} ({win_rate:.1f}%)")
        self.log(f"  Losses: {len(losing_trades)}")

        if winning_trades:
            avg_win = statistics.mean([t['pnl'] for t in winning_trades])
            self.log(f"  Avg Win:  ${avg_win:+.2f}")

        if losing_trades:
            avg_loss = statistics.mean([t['pnl'] for t in losing_trades])
            self.log(f"  Avg Loss: ${avg_loss:+.2f}")

        self.log(f"\nRisk Metrics:")
        self.log(f"  Max Drawdown: {self.max_drawdown:.2f}%")

        # Save results
        self.save_session_results()
        self.log(f"\n✓ Session results saved to {self.log_dir}/")

    def save_session_results(self) -> None:
        """Save session results to JSON"""
        output = {
            'session_id': self.session_id,
            'symbol': self.symbol,
            'start_time': self.equity_times[0].isoformat() if self.equity_times else None,
            'end_time': self.equity_times[-1].isoformat() if self.equity_times else None,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.current_capital, 2),
            'total_return_pct': round(((self.current_capital - self.initial_capital) / self.initial_capital) * 100, 2),
            'total_trades': len(self.trades),
            'max_drawdown_pct': round(self.max_drawdown, 2),
            'trades': self.trades,
            'equity_curve': [round(e, 2) for e in self.equity_curve],
        }

        results_file = self.log_dir / f'paper_trading_results_{self.session_id}.json'
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        self.log(f"Saved to: {results_file}")

    def log(self, message: str) -> None:
        """Log message to file and console"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"

        print(log_message)

        log_file = self.log_dir / f'paper_trading_{self.session_id}.log'
        with open(log_file, 'a') as f:
            f.write(log_message + '\n')


def main():
    """Start paper trading engine"""
    engine = PaperTradingEngine(
        symbol='XAUUSD',
        initial_capital=10000,
        log_dir='.paper_trading_logs'
    )

    # Run paper trading (checks for new prices daily)
    engine.run_paper_trading_loop(interval_minutes=1440)  # Daily


if __name__ == '__main__':
    main()
