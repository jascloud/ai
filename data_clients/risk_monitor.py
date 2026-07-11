#!/usr/bin/env python3
"""
Phase 1 — Real-time position/exposure risk monitor.

This is NOT a real-data client (no external API, no rate limit needed)
— it's a pure local hard-stop gate that runs before any BUY is executed,
in both backtest and (eventually) live/paper-trading paths. Per the
explicit non-goal in this phase ("no live-capital execution wiring"),
this only guards the paths that already exist (backtest fills); it's
built now so the same gate is in place unchanged when live execution is
ever wired up later.

Limits enforced (mirrors the existing Portfolio Manager constraints
already reported in analyze() output, now actually checked before a
trade executes rather than just stated):
  - max_position_pct   : no single position may exceed this fraction of
                          total capital (existing 5% Kelly cap).
  - max_total_exposure_pct : combined value of all open positions may
                          not exceed this fraction of total capital.
  - max_positions      : hard cap on number of concurrent open symbols.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class RiskLimits:
    max_position_pct: float = 0.05
    max_total_exposure_pct: float = 0.60
    max_positions: int = 10


class PositionRiskMonitor:
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()

    def check_trade(
        self,
        proposed_cost: float,
        capital_before_trade: float,
        open_positions: Dict[str, dict],
        total_capital: float,
    ) -> tuple:
        """Returns (allowed: bool, reason: str). Never raises — a risk
        check that crashes the caller is worse than one that blocks the
        trade and logs why."""

        if total_capital <= 0:
            return False, "total_capital is zero or negative — blocking all trades"

        position_pct = proposed_cost / total_capital
        if position_pct > self.limits.max_position_pct:
            return False, (
                f"proposed position {position_pct*100:.2f}% of capital exceeds "
                f"max_position_pct {self.limits.max_position_pct*100:.2f}%"
            )

        existing_exposure = sum(p.get("cost", 0.0) for p in open_positions.values())
        total_exposure_after = existing_exposure + proposed_cost
        exposure_pct = total_exposure_after / total_capital
        if exposure_pct > self.limits.max_total_exposure_pct:
            return False, (
                f"total exposure after trade {exposure_pct*100:.2f}% would exceed "
                f"max_total_exposure_pct {self.limits.max_total_exposure_pct*100:.2f}%"
            )

        if len(open_positions) >= self.limits.max_positions:
            return False, (
                f"already at max_positions limit ({self.limits.max_positions} open symbols)"
            )

        if proposed_cost > capital_before_trade:
            return False, (
                f"proposed cost ${proposed_cost:.2f} exceeds available cash ${capital_before_trade:.2f}"
            )

        return True, "within risk limits"
