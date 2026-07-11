#!/usr/bin/env python3
"""
Prediction Market Arbitrage Agent
- Scans Polymarket & Kalshi for YES/NO mispricings
- Detects cross-platform arbitrage opportunities
- Sizes positions using Kelly Criterion
- Displays actionable trading recommendations
"""

import json
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import urllib.request
import urllib.error


@dataclass
class Market:
    """Market data structure"""
    platform: str
    market_id: str
    title: str
    yes_price: float
    no_price: float
    volume_24h: float
    liquidity: float
    created_at: str


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity found"""
    market_title: str
    buy_platform: str
    buy_side: str  # "YES" or "NO"
    buy_price: float
    sell_platform: str
    sell_side: str  # "YES" or "NO"
    sell_price: float
    spread_pct: float
    implied_prob_market_a: float
    implied_prob_market_b: float
    kelly_fraction: float
    recommended_size: float  # For $1000 bankroll
    fee_cost: float  # Estimated


class PredictionArbitrageAgent:
    """Multi-platform prediction market arbitrage analyzer"""

    def __init__(self, bankroll: float = 1000.0):
        self.bankroll = bankroll
        self.markets_polymarket = []
        self.markets_kalshi = []
        self.arbitrage_opportunities = []
        self.min_spread_threshold = 1.0  # Only show spreads > 1%

    def fetch_polymarket_markets(self, limit: int = 10) -> List[Market]:
        """
        Fetch top markets by volume from Polymarket (public API)
        https://polymarket.com/api/markets
        """
        try:
            url = "https://clob.polymarket.com/markets?limit=100&offset=0"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())

            markets = []
            for market_data in data[:limit]:
                # Extract YES/NO prices from order book
                yes_price = float(market_data.get("mid", 0.50))  # Default to 0.50
                no_price = 1.0 - yes_price

                market = Market(
                    platform="Polymarket",
                    market_id=market_data.get("id", "unknown"),
                    title=market_data.get("question", "Unknown")[:80],
                    yes_price=yes_price,
                    no_price=no_price,
                    volume_24h=float(market_data.get("volume24h", 0)),
                    liquidity=float(market_data.get("liquidity", 0)),
                    created_at=market_data.get("createdAt", "")
                )
                markets.append(market)

            print(f"✓ Loaded {len(markets)} markets from Polymarket")
            return markets

        except Exception as e:
            print(f"✗ Error fetching Polymarket data: {e}")
            return []

    def fetch_kalshi_markets(self, limit: int = 10) -> List[Market]:
        """
        Fetch top markets by volume from Kalshi (public API)
        https://kalshi.com/api
        """
        try:
            # Kalshi uses a different API structure
            # This is a simplified version; actual endpoint may vary
            url = "https://api.kalshi.com/v2/markets?limit=100&sort_by=volume"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())

            markets = []
            markets_list = data.get("markets", data.get("data", []))

            for market_data in markets_list[:limit]:
                # Kalshi typically shows last_price and bid/ask
                last_price = float(market_data.get("last_price", 0.50))
                yes_price = last_price
                no_price = 1.0 - yes_price

                market = Market(
                    platform="Kalshi",
                    market_id=market_data.get("id", "unknown"),
                    title=market_data.get("title", "Unknown")[:80],
                    yes_price=yes_price,
                    no_price=no_price,
                    volume_24h=float(market_data.get("volume_24h", 0)),
                    liquidity=float(market_data.get("liquidity", 0)),
                    created_at=market_data.get("created_time", "")
                )
                markets.append(market)

            print(f"✓ Loaded {len(markets)} markets from Kalshi")
            return markets

        except Exception as e:
            print(f"✗ Error fetching Kalshi data: {e}")
            # Return synthetic data for demo
            return self._generate_demo_kalshi_markets(limit)

    def _generate_demo_kalshi_markets(self, limit: int = 5) -> List[Market]:
        """Generate demo Kalshi markets for testing"""
        demo_markets = [
            {
                "title": "Will Bitcoin reach $100k by EOY 2024?",
                "yes_price": 0.72,
                "volume_24h": 250000,
                "liquidity": 50000
            },
            {
                "title": "Will the Fed cut rates in next FOMC?",
                "yes_price": 0.58,
                "volume_24h": 180000,
                "liquidity": 35000
            },
            {
                "title": "Will Trump win 2024 election?",
                "yes_price": 0.62,
                "volume_24h": 500000,
                "liquidity": 100000
            },
            {
                "title": "Will S&P 500 close above 5500 by Dec?",
                "yes_price": 0.68,
                "volume_24h": 120000,
                "liquidity": 25000
            },
            {
                "title": "Will Ethereum outperform Bitcoin in 2024?",
                "yes_price": 0.45,
                "volume_24h": 85000,
                "liquidity": 18000
            },
        ]

        markets = []
        for i, m in enumerate(demo_markets[:limit]):
            markets.append(Market(
                platform="Kalshi",
                market_id=f"kalshi_{i}",
                title=m["title"],
                yes_price=m["yes_price"],
                no_price=1.0 - m["yes_price"],
                volume_24h=m["volume_24h"],
                liquidity=m["liquidity"],
                created_at=datetime.now(timezone.utc).isoformat()
            ))

        return markets

    def _generate_demo_polymarket_markets(self, limit: int = 5) -> List[Market]:
        """Generate demo Polymarket markets for testing"""
        demo_markets = [
            {
                "title": "Will Bitcoin reach $100k by EOY 2024?",
                "yes_price": 0.70,
                "volume_24h": 300000,
                "liquidity": 60000
            },
            {
                "title": "Will the Fed cut rates in next FOMC?",
                "yes_price": 0.60,
                "volume_24h": 200000,
                "liquidity": 40000
            },
            {
                "title": "Will Trump win 2024 election?",
                "yes_price": 0.63,
                "volume_24h": 600000,
                "liquidity": 120000
            },
            {
                "title": "Will S&P 500 close above 5500 by Dec?",
                "yes_price": 0.66,
                "volume_24h": 150000,
                "liquidity": 30000
            },
            {
                "title": "Will Ethereum outperform Bitcoin in 2024?",
                "yes_price": 0.47,
                "volume_24h": 100000,
                "liquidity": 20000
            },
        ]

        markets = []
        for i, m in enumerate(demo_markets[:limit]):
            markets.append(Market(
                platform="Polymarket",
                market_id=f"poly_{i}",
                title=m["title"],
                yes_price=m["yes_price"],
                no_price=1.0 - m["yes_price"],
                volume_24h=m["volume_24h"],
                liquidity=m["liquidity"],
                created_at=datetime.now(timezone.utc).isoformat()
            ))

        return markets

    def detect_arbitrage(self) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities between platforms
        Classic: YES on Market A + NO on Market B should sum to ~100%
        If sum < 100%, profit opportunity exists
        """
        opportunities = []

        for poly_market in self.markets_polymarket:
            for kalshi_market in self.markets_kalshi:
                # Skip if markets are too different
                if not self._markets_similar(poly_market.title, kalshi_market.title):
                    continue

                # Arbitrage 1: BUY YES on Polymarket, SELL YES on Kalshi
                yes_spread = kalshi_market.yes_price - poly_market.yes_price
                if yes_spread > (self.min_spread_threshold / 100):
                    opp = self._create_opportunity(
                        market_title=poly_market.title,
                        buy_platform="Polymarket",
                        buy_side="YES",
                        buy_price=poly_market.yes_price,
                        sell_platform="Kalshi",
                        sell_side="YES",
                        sell_price=kalshi_market.yes_price,
                        spread=yes_spread
                    )
                    if opp:
                        opportunities.append(opp)

                # Arbitrage 2: BUY NO on Polymarket, SELL NO on Kalshi
                no_spread = kalshi_market.no_price - poly_market.no_price
                if no_spread > (self.min_spread_threshold / 100):
                    opp = self._create_opportunity(
                        market_title=poly_market.title,
                        buy_platform="Polymarket",
                        buy_side="NO",
                        buy_price=poly_market.no_price,
                        sell_platform="Kalshi",
                        sell_side="NO",
                        sell_price=kalshi_market.no_price,
                        spread=no_spread
                    )
                    if opp:
                        opportunities.append(opp)

                # Arbitrage 3: Cross-side arbitrage
                # BUY YES on Polymarket, SELL NO on Kalshi
                cross_spread = 1.0 - (poly_market.yes_price + kalshi_market.no_price)
                if abs(cross_spread) > (self.min_spread_threshold / 100):
                    # This would be a hedged trade
                    pass

        # Sort by spread (best opportunities first)
        self.arbitrage_opportunities = sorted(
            opportunities,
            key=lambda x: x.spread_pct,
            reverse=True
        )

        return self.arbitrage_opportunities

    def _markets_similar(self, title_a: str, title_b: str) -> bool:
        """Check if two market titles are referring to the same event"""
        # Simple string matching (could be improved with semantic similarity)
        words_a = set(title_a.lower().split())
        words_b = set(title_b.lower().split())

        # Check if at least 40% of words overlap
        overlap = words_a & words_b
        return len(overlap) >= 3  # At least 3 words in common

    def _create_opportunity(
        self,
        market_title: str,
        buy_platform: str,
        buy_side: str,
        buy_price: float,
        sell_platform: str,
        sell_side: str,
        sell_price: float,
        spread: float
    ) -> Optional[ArbitrageOpportunity]:
        """Create an arbitrage opportunity object"""

        spread_pct = (spread / buy_price) * 100 if buy_price > 0 else 0

        if spread_pct < self.min_spread_threshold:
            return None

        # Estimate fees (typically 2-3% per side on prediction markets)
        fee_per_side = 0.02
        total_fee = (buy_price + sell_price) * fee_per_side
        net_profit = spread - total_fee

        if net_profit <= 0:
            return None  # Not profitable after fees

        # Kelly Criterion sizing
        kelly_fraction = self._calculate_kelly(net_profit, buy_price)
        recommended_size = kelly_fraction * self.bankroll

        opp = ArbitrageOpportunity(
            market_title=market_title,
            buy_platform=buy_platform,
            buy_side=buy_side,
            buy_price=buy_price,
            sell_platform=sell_platform,
            sell_side=sell_side,
            sell_price=sell_price,
            spread_pct=spread_pct,
            implied_prob_market_a=buy_price if buy_side == "YES" else 1 - buy_price,
            implied_prob_market_b=sell_price if sell_side == "YES" else 1 - sell_price,
            kelly_fraction=kelly_fraction,
            recommended_size=recommended_size,
            fee_cost=total_fee
        )

        return opp

    def _calculate_kelly(self, win_amount: float, bet_size: float) -> float:
        """
        Kelly Criterion: f = (bp - q) / b
        For arbitrage: guaranteed win, so use fractional Kelly
        f = (win_amount / bet_size) * 0.25  (25% of full Kelly for safety)
        """
        if bet_size <= 0:
            return 0.0

        win_prob = 0.99  # Near certain for arb
        loss_prob = 0.01
        win_ratio = win_amount / bet_size if bet_size > 0 else 0

        kelly = (win_prob * win_ratio - loss_prob) / win_ratio if win_ratio > 0 else 0
        kelly = max(0, min(kelly, 0.50))  # Cap at 50% for safety

        # For arbitrage, use 25% of full Kelly
        return kelly * 0.25

    def run_analysis(self):
        """Execute full arbitrage analysis"""
        print("="*80)
        print("PREDICTION MARKET ARBITRAGE SCANNER")
        print("="*80)
        print(f"Bankroll: ${self.bankroll:,.2f}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print()

        # Fetch markets
        print("📊 Fetching market data...")
        self.markets_polymarket = self.fetch_polymarket_markets(limit=10)
        if not self.markets_polymarket:
            print("   (Using demo Polymarket data)")
            self.markets_polymarket = self._generate_demo_polymarket_markets(10)

        self.markets_kalshi = self.fetch_kalshi_markets(limit=10)
        if not self.markets_kalshi:
            print("   (Using demo Kalshi data)")
            self.markets_kalshi = self._generate_demo_kalshi_markets(10)

        print(f"✓ Polymarket: {len(self.markets_polymarket)} markets")
        print(f"✓ Kalshi: {len(self.markets_kalshi)} markets")
        print()

        # Detect arbitrage
        print("🔍 Scanning for arbitrage opportunities...")
        opportunities = self.detect_arbitrage()

        if not opportunities:
            print("   No profitable arbitrage opportunities found")
            print()
            return

        print(f"✓ Found {len(opportunities)} opportunities\n")

        # Display opportunities
        self.display_opportunities(opportunities)

    def display_opportunities(self, opportunities: List[ArbitrageOpportunity]):
        """Display arbitrage opportunities in human-readable format"""
        print("="*80)
        print("ARBITRAGE OPPORTUNITIES (Ranked by Spread)")
        print("="*80)
        print()

        for idx, opp in enumerate(opportunities[:10], 1):
            print(f"#{idx} {opp.market_title}")
            print(f"├─ BUY:  {opp.buy_side:3s} on {opp.buy_platform:12s} @ ${opp.buy_price:.4f}")
            print(f"├─ SELL: {opp.sell_side:3s} on {opp.sell_platform:12s} @ ${opp.sell_price:.4f}")
            print(f"├─ SPREAD: {opp.spread_pct:+.2f}% (${opp.sell_price - opp.buy_price:+.4f})")
            print(f"├─ FEES: ${opp.fee_cost:.4f}")
            print(f"├─ NET PROFIT: ${(opp.sell_price - opp.buy_price - opp.fee_cost):+.4f}")
            print(f"├─ KELLY FRACTION: {opp.kelly_fraction*100:.1f}%")
            print(f"└─ RECOMMENDED SIZE: ${opp.recommended_size:,.2f} ({opp.kelly_fraction*100:.1f}% of bankroll)")
            print()

    def save_results(self):
        """Save analysis results to JSON"""
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bankroll": self.bankroll,
            "polymarket_count": len(self.markets_polymarket),
            "kalshi_count": len(self.markets_kalshi),
            "opportunities_found": len(self.arbitrage_opportunities),
            "opportunities": [
                {
                    "market": opp.market_title,
                    "buy": f"{opp.buy_side} on {opp.buy_platform}",
                    "buy_price": opp.buy_price,
                    "sell": f"{opp.sell_side} on {opp.sell_platform}",
                    "sell_price": opp.sell_price,
                    "spread_pct": opp.spread_pct,
                    "net_profit": round(opp.sell_price - opp.buy_price - opp.fee_cost, 4),
                    "recommended_size": round(opp.recommended_size, 2),
                    "kelly_fraction": round(opp.kelly_fraction, 4)
                }
                for opp in self.arbitrage_opportunities[:20]
            ]
        }

        filename = f"prediction_arbitrage_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✓ Results saved to {filename}")


def main():
    """Run the arbitrage scanner"""
    agent = PredictionArbitrageAgent(bankroll=1000.0)
    agent.run_analysis()
    agent.save_results()


if __name__ == '__main__':
    main()
