#!/usr/bin/env python3
"""
Mean Reversion Backtest
Implements a mean reversion trading strategy using Z-score signals.
"""

import argparse
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance is required. Install it with: pip install yfinance")
    sys.exit(1)


class MeanReversionBacktester:
    def __init__(self, symbol, lookback, entry_z, exit_z, start_date=None, end_date=None):
        self.symbol = symbol
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.start_date = start_date or (datetime.now() - timedelta(days=365))
        self.end_date = end_date or datetime.now()

        self.data = None
        self.trades = []
        self.equity_curve = []

    def fetch_data(self):
        """Fetch historical price data."""
        print(f"Fetching data for {self.symbol}...")
        self.data = yf.download(
            self.symbol,
            start=self.start_date,
            end=self.end_date,
            progress=False
        )

        if self.data.empty:
            print(f"Error: No data found for symbol {self.symbol}")
            return False

        self.data['Close'] = self.data['Close'].astype(float)
        return True

    def calculate_signals(self):
        """Calculate Z-score signals based on rolling mean and std."""
        self.data['SMA'] = self.data['Close'].rolling(window=self.lookback).mean()
        self.data['STD'] = self.data['Close'].rolling(window=self.lookback).std()

        # Calculate Z-score
        self.data['Z_Score'] = (self.data['Close'] - self.data['SMA']) / self.data['STD']

        # Generate signals
        self.data['Signal'] = 0  # 0: no position, 1: long position

        return True

    def run_backtest(self):
        """Execute the backtest."""
        if not self.fetch_data():
            return False

        if not self.calculate_signals():
            return False

        # Skip rows with NaN values (from rolling calculations)
        backtest_data = self.data.dropna().copy()

        position = False
        entry_price = 0
        entry_idx = 0

        for idx, (date, row) in enumerate(backtest_data.iterrows()):
            z_score = row['Z_Score']
            close = row['Close']

            # Entry signal
            if not position and z_score < self.entry_z:
                position = True
                entry_price = close
                entry_idx = idx
                entry_date = date

            # Exit signal
            elif position and z_score > self.exit_z:
                position = False
                exit_price = close
                exit_date = date

                pnl = exit_price - entry_price
                pnl_pct = (pnl / entry_price) * 100
                holding_days = (exit_date - entry_date).days

                self.trades.append({
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'exit_date': exit_date,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'holding_days': holding_days
                })

        # Close any open position at the end
        if position:
            exit_price = backtest_data.iloc[-1]['Close']
            exit_date = backtest_data.index[-1]

            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100
            holding_days = (exit_date - entry_date).days

            self.trades.append({
                'entry_date': entry_date,
                'entry_price': entry_price,
                'exit_date': exit_date,
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'holding_days': holding_days
            })

        return True

    def calculate_metrics(self):
        """Calculate performance metrics."""
        if not self.trades:
            return {
                'num_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_pnl_per_trade': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'avg_holding_days': 0
            }

        trades_df = pd.DataFrame(self.trades)

        winning_trades = (trades_df['pnl'] > 0).sum()
        losing_trades = (trades_df['pnl'] < 0).sum()
        num_trades = len(trades_df)

        metrics = {
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / num_trades * 100) if num_trades > 0 else 0.0,
            'total_pnl': trades_df['pnl'].sum(),
            'total_pnl_pct': trades_df['pnl_pct'].sum(),
            'avg_pnl_per_trade': trades_df['pnl'].mean(),
            'best_trade': trades_df['pnl'].max(),
            'worst_trade': trades_df['pnl'].min(),
            'avg_holding_days': trades_df['holding_days'].mean()
        }

        return metrics

    def print_results(self):
        """Print backtest results."""
        metrics = self.calculate_metrics()

        print("\n" + "="*60)
        print(f"Mean Reversion Backtest Results - {self.symbol}")
        print("="*60)
        print(f"Period: {self.start_date.date()} to {self.end_date.date()}")
        print(f"Lookback: {self.lookback} days")
        print(f"Entry Z-Score: {self.entry_z}")
        print(f"Exit Z-Score: {self.exit_z}")
        print("-"*60)
        print(f"Total Trades: {metrics['num_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print("-"*60)
        print(f"Total P&L: ${metrics['total_pnl']:.2f}")
        print(f"Total P&L %: {metrics['total_pnl_pct']:.2f}%")
        print(f"Avg P&L per Trade: ${metrics['avg_pnl_per_trade']:.2f}")
        print(f"Best Trade: ${metrics['best_trade']:.2f}")
        print(f"Worst Trade: ${metrics['worst_trade']:.2f}")
        print(f"Avg Holding Days: {metrics['avg_holding_days']:.1f}")
        print("="*60)

        if self.trades and len(self.trades) <= 10:
            print("\nTrade Details:")
            print("-"*60)
            for i, trade in enumerate(self.trades, 1):
                print(f"\nTrade {i}:")
                print(f"  Entry:  {trade['entry_date'].date()} @ ${trade['entry_price']:.2f}")
                print(f"  Exit:   {trade['exit_date'].date()} @ ${trade['exit_price']:.2f}")
                print(f"  P&L:    ${trade['pnl']:.2f} ({trade['pnl_pct']:+.2f}%)")
                print(f"  Days:   {trade['holding_days']}")


def main():
    parser = argparse.ArgumentParser(
        description="Mean Reversion Backtest Strategy"
    )
    parser.add_argument('--symbol', required=True, help='Stock symbol (e.g., TSLA)')
    parser.add_argument('--lookback', type=int, default=30, help='Lookback period in days (default: 30)')
    parser.add_argument('--entry_z', type=float, default=-2.0, help='Entry Z-score threshold (default: -2.0)')
    parser.add_argument('--exit_z', type=float, default=0.0, help='Exit Z-score threshold (default: 0.0)')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')

    args = parser.parse_args()

    start_date = None
    end_date = None

    if args.start:
        try:
            start_date = datetime.strptime(args.start, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid start date format. Use YYYY-MM-DD")
            sys.exit(1)

    if args.end:
        try:
            end_date = datetime.strptime(args.end, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid end date format. Use YYYY-MM-DD")
            sys.exit(1)

    backtester = MeanReversionBacktester(
        args.symbol,
        args.lookback,
        args.entry_z,
        args.exit_z,
        start_date,
        end_date
    )

    if backtester.run_backtest():
        backtester.print_results()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
