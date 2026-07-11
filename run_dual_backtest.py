#!/usr/bin/env python3
"""
Dual-mode backtest orchestrator: runs both entry modes (indicator vs.
engulfing) over the same symbols/window and produces a side-by-side
comparison report.

Unlike a config-driven `run_single_backtest(config)` entry point, this
drives the real MomentumBacktester class directly (backtest_momentum_agent.py)
-- there's no separate function to wire up, the class already does
everything this needs via __init__(entry_mode=...) + run_all_backtests().

MomentumBacktester's `num_backtests` runs N *non-overlapping* historical
windows walking backward from today, not N repeated evaluations of one
window. For period=120_days, num_backtests=20 that means
60 + 20*120 = 2,460 trading days of real history (~10 years) must be
fetchable from the configured data source -- this script computes and
prints that requirement up front instead of silently attempting a fetch
that may take a long time or exceed what's available.
"""

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from backtest_momentum_agent import MomentumBacktester
from market_data import MarketDataError

SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


def run_mode(entry_mode: str, capital: float, period: str, num_backtests: int,
             symbols: List[str]) -> Dict[str, Any]:
    """Runs one entry mode's full backtest suite via the real
    MomentumBacktester and returns its summary dict, or an error record
    (never a fabricated result) if real data can't support the request."""
    try:
        backtester = MomentumBacktester(
            initial_capital=capital,
            time_period=period,
            num_backtests=num_backtests,
            symbols=symbols,
            entry_mode=entry_mode,
        )
        return backtester.run_all_backtests()
    except MarketDataError as e:
        return {"error": str(e), "entry_mode": entry_mode}


def summarize_exit_reasons(summary: Dict[str, Any]) -> Dict[str, int]:
    """Tallies exit_reason across every trade in every backtest_result."""
    totals: Dict[str, int] = {}
    for result in summary.get("backtest_results", []):
        for trade in result.get("trades", []):
            reason = trade.get("exit_reason")
            if reason:
                totals[reason] = totals.get(reason, 0) + 1
    return totals


def summarize_mode(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Rolls a MomentumBacktester summary dict into mean/median/stdev
    return, win rate, trade counts, and exit-reason breakdown -- the
    per-run metrics needed for the comparison report."""
    if "error" in summary:
        return {"error": summary["error"]}

    results = summary.get("backtest_results", [])
    returns = [r["metrics"]["total_return"] for r in results]
    win_rates = [r["metrics"]["win_rate"] for r in results]
    trade_counts = [r["metrics"]["total_trades"] for r in results]

    return {
        "runs": len(results),
        "mean_return_pct": round(statistics.fmean(returns) * 100, 4) if returns else None,
        "median_return_pct": round(statistics.median(returns) * 100, 4) if returns else None,
        "stdev_return_pct": round(statistics.pstdev(returns) * 100, 4) if len(returns) > 1 else None,
        "mean_win_rate_pct": round(statistics.fmean(win_rates) * 100, 4) if win_rates else None,
        "mean_trades_per_run": round(statistics.fmean(trade_counts), 2) if trade_counts else None,
        "total_trades_all_runs": sum(trade_counts),
        "exit_reason_totals": summarize_exit_reasons(summary),
    }


def main():
    parser = argparse.ArgumentParser(description="Dual-mode (indicator vs. engulfing) backtest comparison")
    parser.add_argument("--indicator-runs", type=int, default=5,
                         help="Number of non-overlapping backtest windows for indicator mode")
    parser.add_argument("--engulfing-runs", type=int, default=20,
                         help="Number of non-overlapping backtest windows for engulfing mode "
                              "(higher trade frequency from the intraday trigger warrants more runs)")
    parser.add_argument("--period", type=str, default="120_days",
                         help="Backtest window size (both modes always use the same period for a fair comparison)")
    parser.add_argument("--capital", type=float, default=1000)
    parser.add_argument("--symbols", type=str, default=",".join(SYMBOLS))
    parser.add_argument("--output", type=str, default="dual_backtest_report.json")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]

    window_days = MomentumBacktester.PERIOD_TRADING_DAYS.get(args.period, 5)
    indicator_days_needed = MomentumBacktester.INDICATOR_LOOKBACK + args.indicator_runs * window_days
    engulfing_days_needed = MomentumBacktester.INDICATOR_LOOKBACK + args.engulfing_runs * window_days

    print("=" * 60)
    print("DUAL-MODE BACKTEST COMPARISON")
    print("=" * 60)
    print(f"Period: {args.period} ({window_days} trading days per run)")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Indicator mode: {args.indicator_runs} runs -> needs ~{indicator_days_needed} real trading days of history")
    print(f"Engulfing mode:  {args.engulfing_runs} runs -> needs ~{engulfing_days_needed} real trading days of history")
    print()

    print("Running indicator-mode backtests...")
    indicator_summary = run_mode("indicator", args.capital, args.period, args.indicator_runs, symbols)

    print("\nRunning engulfing-mode backtests...")
    engulfing_summary = run_mode("engulfing", args.capital, args.period, args.engulfing_runs, symbols)

    report = {
        "generated_at": datetime.now().isoformat(),
        "period": args.period,
        "window_days": window_days,
        "capital": args.capital,
        "symbols": symbols,
        "indicator_mode": summarize_mode(indicator_summary),
        "engulfing_mode": summarize_mode(engulfing_summary),
    }

    Path(args.output).write_text(json.dumps(report, indent=2))
    print(f"\n✓ Comparison report written to {args.output}")
    print(json.dumps({
        "indicator_mode": report["indicator_mode"],
        "engulfing_mode": report["engulfing_mode"],
    }, indent=2))


if __name__ == "__main__":
    main()
