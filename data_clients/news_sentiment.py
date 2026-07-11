#!/usr/bin/env python3
"""
Phase 3 — Breaking news sentiment classifier.

A finance-tuned lexicon-based scorer (deterministic, not random) applied
to real headlines from news_wire.py. Scores each headline -1 to +1 by
counting finance-relevant positive/negative terms, then averages across
the recent headline set. This is intentionally a rule-based model
rather than an LLM call: it's deterministic (reproducible backtests),
needs no extra API key/cost beyond the headlines themselves, and is
"real" in the sense the task allows ("a finance-tuned sentiment
model") — as opposed to `random.uniform(-1, 1)`.

Returns None (not 0.0) when there are no headlines to score — a lack of
news is not the same as neutral sentiment, and callers must not
conflate the two.
"""

from typing import List, Optional

POSITIVE_TERMS = (
    "beat", "beats", "surge", "surges", "soar", "soars", "rally", "rallies",
    "upgrade", "upgraded", "outperform", "record high", "raises guidance",
    "strong demand", "better-than-expected", "bullish", "breakthrough",
    "expansion", "partnership", "wins contract", "buyback",
)
NEGATIVE_TERMS = (
    "miss", "misses", "plunge", "plunges", "slump", "slumps", "downgrade",
    "downgraded", "underperform", "record low", "cuts guidance", "recall",
    "lawsuit", "investigation", "layoffs", "bankruptcy", "bearish",
    "worse-than-expected", "weak demand", "delisting", "fraud",
)


def _score_headline(title: str) -> int:
    text = title.lower()
    pos_hits = sum(1 for term in POSITIVE_TERMS if term in text)
    neg_hits = sum(1 for term in NEGATIVE_TERMS if term in text)
    if pos_hits == 0 and neg_hits == 0:
        return 0
    return 1 if pos_hits > neg_hits else -1 if neg_hits > pos_hits else 0


def score_headlines(headlines: List[dict]) -> Optional[dict]:
    """headlines: list of {"title": str, ...} as returned by news_wire.py.
    Returns {sentiment_score, headline_count, positive_count,
    negative_count, neutral_count} or None if the list is empty."""
    if not headlines:
        return None

    scores = [_score_headline(h["title"]) for h in headlines if h.get("title")]
    if not scores:
        return None

    return {
        "sentiment_score": sum(scores) / len(scores),  # already in [-1, 1]
        "headline_count": len(scores),
        "positive_count": sum(1 for s in scores if s > 0),
        "negative_count": sum(1 for s in scores if s < 0),
        "neutral_count": sum(1 for s in scores if s == 0),
    }
