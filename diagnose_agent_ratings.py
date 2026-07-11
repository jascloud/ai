#!/usr/bin/env python3
"""
Rating-distribution diagnostic for the momentum trading agent's
Portfolio Manager aggregation.

Purpose: confirm whether a strong REAL Technical Analyst signal actually
reaches a BUY/SELL decision, or gets diluted/suppressed by the other
(simulated, until later phases replace them) agents averaged alongside
it. This drives the actual agent classes from backtest_momentum_agent.py
(not a hand-rolled statistical model), so results reflect real code
behavior rather than a theoretical approximation that could drift from
the implementation.

Method: for each Technical Analyst rating level 1-5, hold Technical's
rating fixed at that level and run N_TRIALS trials in which every OTHER
agent's `.analyze()` runs for real (sampling whatever randomness or real
data path it currently has). Feed the same sampled set of analyses into
both:
  - PortfolioManager.legacy_flat_decision  (the ORIGINAL flat-mean,
    4.0/2.0-threshold logic, preserved for comparison only)
  - PortfolioManager.analyze               (the current live logic)
so the before/after comparison is apples-to-apples on identical inputs.

"Clearance rate" = fraction of trials at Technical=5 (max real BUY
signal) where the decision was actually BUY. This is the headline
number: it answers "does real signal reach the Portfolio Manager, or
does it get drowned out."

Every run appends a phase-tagged entry to
agent_rating_diagnostics_summary.json so clearance-rate drift is
auditable phase over phase, rather than re-written each time.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np

import backtest_momentum_agent as bta

N_TRIALS_DEFAULT = 3000
SUMMARY_FILE = "agent_rating_diagnostics_summary.json"
DUMMY_SYMBOL = "DIAG"
DUMMY_PRICE_DATA = {'prices': [100.0] * 60, 'current_price': 100.0}


def _technical_analysis(rating: int) -> Dict[str, Any]:
    """Synthetic Technical Analyst output held at a fixed rating level —
    this is the one deliberately-controlled variable in the diagnostic.
    Everything else below runs the real agent code."""
    return {
        'name': 'Technical Analyst',
        'rating': rating,
        'action': 'BUY' if rating >= 4 else 'SELL' if rating <= 2 else 'HOLD',
        'confidence': abs((rating - 3) / 2),
        'data_source': 'real_market_data',
        'agent_role': 'technical',
    }


def _run_other_agents(agents: List[Any]) -> List[Dict[str, Any]]:
    """Runs every configured non-Technical, non-PortfolioManager agent's
    real .analyze() method once, tagging each result with its agent name."""
    out = []
    for agent in agents:
        if isinstance(agent, bta.TechnicalAnalyst) or isinstance(agent, bta.PortfolioManager):
            continue
        result = agent.analyze(DUMMY_SYMBOL, DUMMY_PRICE_DATA)
        result.setdefault('name', agent.name)
        out.append(result)
    return out


def run_diagnostic(agents: List[Any], n_trials: int = N_TRIALS_DEFAULT) -> Dict[str, Any]:
    portfolio_manager = next(a for a in agents if isinstance(a, bta.PortfolioManager))

    by_rating: Dict[int, Dict[str, List[str]]] = {}

    for technical_rating in (1, 2, 3, 4, 5):
        legacy_decisions = []
        current_decisions = []
        weighted_ratings = []
        flat_ratings = []

        for _ in range(n_trials):
            other_analyses = _run_other_agents(agents)
            all_analyses = [_technical_analysis(technical_rating)] + other_analyses

            legacy = bta.PortfolioManager.legacy_flat_decision(all_analyses)
            current = portfolio_manager.analyze(DUMMY_SYMBOL, DUMMY_PRICE_DATA, all_analyses)

            legacy_decisions.append(legacy['decision'])
            current_decisions.append(current['decision'])
            weighted_ratings.append(current['weighted_avg_rating'])
            flat_ratings.append(current['flat_avg_rating'])

        by_rating[technical_rating] = {
            'legacy_buy_rate': legacy_decisions.count('BUY') / n_trials,
            'legacy_sell_rate': legacy_decisions.count('SELL') / n_trials,
            'legacy_hold_rate': legacy_decisions.count('HOLD') / n_trials,
            'current_buy_rate': current_decisions.count('BUY') / n_trials,
            'current_sell_rate': current_decisions.count('SELL') / n_trials,
            'current_hold_rate': current_decisions.count('HOLD') / n_trials,
            'avg_weighted_rating': float(np.mean(weighted_ratings)),
            'avg_flat_rating': float(np.mean(flat_ratings)),
        }

    # Headline clearance rate: Technical=5 (max real BUY signal) -> BUY decision
    legacy_clearance_at_5 = by_rating[5]['legacy_buy_rate']
    current_clearance_at_5 = by_rating[5]['current_buy_rate']

    # Mirror image: Technical=1 (max real SELL signal) -> SELL decision
    legacy_clearance_at_1 = by_rating[1]['legacy_sell_rate']
    current_clearance_at_1 = by_rating[1]['current_sell_rate']

    return {
        'n_trials_per_rating_level': n_trials,
        'agents_in_test': [a.name for a in agents if not isinstance(a, bta.PortfolioManager)],
        'by_technical_rating': by_rating,
        'headline': {
            'buy_clearance_at_technical_5': {
                'legacy_flat_mean_4.0_threshold': legacy_clearance_at_5,
                'weighted_mean_3.5_threshold': current_clearance_at_5,
            },
            'sell_clearance_at_technical_1': {
                'legacy_flat_mean_2.0_threshold': legacy_clearance_at_1,
                'weighted_mean_2.5_threshold': current_clearance_at_1,
            },
        },
    }


def append_to_summary(phase: str, note: str, diagnostic: Dict[str, Any], summary_path: str = SUMMARY_FILE) -> None:
    if os.path.isfile(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)
    else:
        summary = {'entries': []}

    entry = {
        'phase': phase,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'note': note,
        'diagnostic': diagnostic,
    }
    summary['entries'].append(entry)

    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)


def print_report(diagnostic: Dict[str, Any]) -> None:
    headline = diagnostic['headline']
    buy = headline['buy_clearance_at_technical_5']
    sell = headline['sell_clearance_at_technical_1']

    print("\n" + "=" * 70)
    print("AGENT RATING DIAGNOSTIC — CLEARANCE RATE REPORT")
    print("=" * 70)
    print(f"Trials per rating level: {diagnostic['n_trials_per_rating_level']}")
    print(f"Agents in test: {', '.join(diagnostic['agents_in_test'])}")
    print()
    print("BUY clearance when Technical Analyst = 5 (max real BUY signal):")
    print(f"  Legacy flat-mean / 4.0 threshold:    {buy['legacy_flat_mean_4.0_threshold']*100:6.2f}%")
    print(f"  Weighted-mean / 3.5 threshold (now): {buy['weighted_mean_3.5_threshold']*100:6.2f}%")
    print()
    print("SELL clearance when Technical Analyst = 1 (max real SELL signal):")
    print(f"  Legacy flat-mean / 2.0 threshold:    {sell['legacy_flat_mean_2.0_threshold']*100:6.2f}%")
    print(f"  Weighted-mean / 2.5 threshold (now): {sell['weighted_mean_2.5_threshold']*100:6.2f}%")
    print()
    print("Full breakdown by Technical Analyst rating level:")
    for rating, stats in sorted(diagnostic['by_technical_rating'].items()):
        print(f"  Technical={rating}: legacy BUY/HOLD/SELL = "
              f"{stats['legacy_buy_rate']*100:5.1f}% / {stats['legacy_hold_rate']*100:5.1f}% / {stats['legacy_sell_rate']*100:5.1f}%   "
              f"| current BUY/HOLD/SELL = "
              f"{stats['current_buy_rate']*100:5.1f}% / {stats['current_hold_rate']*100:5.1f}% / {stats['current_sell_rate']*100:5.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnose whether real signal reaches the Portfolio Manager")
    parser.add_argument("--phase", type=str, required=True, help="Phase tag, e.g. 'phase_0_aggregation_fix'")
    parser.add_argument("--note", type=str, default="", help="One-paragraph readout for this phase")
    parser.add_argument("--trials", type=int, default=N_TRIALS_DEFAULT, help="Trials per Technical rating level")
    parser.add_argument("--summary-file", type=str, default=SUMMARY_FILE)
    args = parser.parse_args()

    bt = bta.MomentumBacktester(initial_capital=500, time_period="1_week", num_backtests=1)
    diagnostic = run_diagnostic(bt.agents, n_trials=args.trials)
    print_report(diagnostic)
    append_to_summary(args.phase, args.note, diagnostic, args.summary_file)
    print(f"\n✓ Appended to {args.summary_file} under phase '{args.phase}'")
