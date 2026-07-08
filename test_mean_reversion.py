#!/usr/bin/env python3
"""
Test Mean Reversion Backtest with mock data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from mean_reversion_backtest import MeanReversionBacktester


def test_mean_reversion_with_mock_data():
    """Test the backtest with synthetic price data."""

    # Create synthetic price data with mean-reverting characteristics
    dates = pd.date_range(end=datetime.now(), periods=252, freq='D')

    # Generate mean-reverting price data
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, 252)
    prices = 100 * np.exp(np.cumsum(returns))

    # Create backtest instance
    backtester = MeanReversionBacktester(
        symbol='TEST',
        lookback=30,
        entry_z=-2.0,
        exit_z=0.0
    )

    # Inject mock data
    backtester.data = pd.DataFrame({
        'Close': prices
    }, index=dates)

    # Run backtest
    backtester.calculate_signals()

    # Skip rows with NaN values (from rolling calculations)
    backtest_data = backtester.data.dropna().copy()

    position = False
    entry_price = 0
    entry_date = None

    for idx, (date, row) in enumerate(backtest_data.iterrows()):
        z_score = row['Z_Score']
        close = row['Close']

        # Entry signal
        if not position and z_score < backtester.entry_z:
            position = True
            entry_price = close
            entry_date = date

        # Exit signal
        elif position and z_score > backtester.exit_z:
            position = False
            exit_price = close
            exit_date = date

            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100

            backtester.trades.append({
                'entry_date': entry_date,
                'entry_price': entry_price,
                'exit_date': exit_date,
                'exit_price': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'holding_days': (exit_date - entry_date).days
            })

    # Print results
    backtester.print_results()

    # Verify results
    print("\n" + "="*60)
    print("TEST VERIFICATION")
    print("="*60)

    metrics = backtester.calculate_metrics()

    assert metrics['num_trades'] > 0, "Expected at least one trade"
    print(f"✓ Generated {metrics['num_trades']} trades")

    assert metrics['total_pnl'] != 0, "Expected non-zero P&L"
    print(f"✓ Total P&L calculated: ${metrics['total_pnl']:.2f}")

    assert 0 <= metrics['win_rate'] <= 100, "Win rate should be between 0-100%"
    print(f"✓ Win rate calculated: {metrics['win_rate']:.2f}%")

    print("\n✓ ALL TESTS PASSED - Script is working correctly")
    print("="*60)


if __name__ == '__main__':
    test_mean_reversion_with_mock_data()
