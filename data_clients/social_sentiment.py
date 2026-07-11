#!/usr/bin/env python3
"""
Phase 4 — Combined social sentiment (X/Twitter + Reddit + StockTwits).

Per the requirement, these three sources are merged into ONE social
sentiment score/agent rather than run as separate agents that would
each get diluted in the Portfolio Manager average — only
get_combined_social_sentiment() is meant to be called by SentimentAnalyst.

- Twitter/X: cashtag ($AAPL) recent-search volume + sentiment
  (TWITTER_BEARER_TOKEN).
- Reddit: WSB/stocks/investing submissions mentioning the ticker
  (REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET, OAuth2 client-credentials
  flow — app-only, no user login needed).
- StockTwits: symbol stream (keyless, public API) — many messages carry
  a built-in Bullish/Bearish sentiment tag we use directly instead of
  re-scoring the text.

Text-based scoring (Twitter, Reddit) reuses the same finance-tuned
lexicon from news_sentiment.py rather than duplicating it.
"""

import requests

from data_clients.base_client import BaseRealDataClient, DataClientError
from data_clients.news_sentiment import score_text


class TwitterCashtagClient(BaseRealDataClient):
    API_KEY_ENV = "TWITTER_BEARER_TOKEN"
    CACHE_NAMESPACE = "twitter_cashtag"
    CACHE_TTL_SECONDS = 120
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str, max_results: int = 50) -> dict:
        try:
            resp = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"query": f"${symbol} -is:retweet lang:en", "max_results": max_results},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Twitter cashtag search failed for ${symbol}: {e}") from e

        payload = resp.json()
        tweets = payload.get("data", [])
        if not tweets:
            raise DataClientError(f"Twitter returned no recent ${symbol} cashtag mentions")

        return {"symbol": symbol, "tweets": [t.get("text", "") for t in tweets]}


class RedditClient(BaseRealDataClient):
    API_KEY_ENV = "REDDIT_CLIENT_ID"  # presence of the ID gates the flow; secret is checked separately below
    CACHE_NAMESPACE = "reddit_mentions"
    CACHE_TTL_SECONDS = 300
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60.0
    SUBREDDITS = ("wallstreetbets", "stocks", "investing")

    def _get_app_token(self, client_secret: str) -> str:
        try:
            resp = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(self.api_key, client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": "momentum-trading-agent/1.0"},
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"Reddit OAuth token request failed: {e}") from e

        token = resp.json().get("access_token")
        if not token:
            raise DataClientError("Reddit OAuth response had no access_token")
        return token

    def _fetch_live(self, symbol: str) -> dict:
        import os
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        if not client_secret:
            raise DataClientError("REDDIT_CLIENT_SECRET not set in environment")

        token = self._get_app_token(client_secret)
        posts = []
        for sub in self.SUBREDDITS:
            try:
                resp = requests.get(
                    f"https://oauth.reddit.com/r/{sub}/search",
                    headers={"Authorization": f"Bearer {token}", "User-Agent": "momentum-trading-agent/1.0"},
                    params={"q": symbol, "restrict_sr": 1, "sort": "new", "limit": 25, "t": "day"},
                    timeout=15,
                )
                resp.raise_for_status()
                children = resp.json().get("data", {}).get("children", [])
                posts.extend(c["data"]["title"] for c in children if c.get("data", {}).get("title"))
            except requests.RequestException:
                continue  # one subreddit failing doesn't fail the whole client

        if not posts:
            raise DataClientError(f"Reddit returned no {symbol} mentions across {self.SUBREDDITS}")

        return {"symbol": symbol, "posts": posts}


class StockTwitsClient(BaseRealDataClient):
    API_KEY_ENV = None  # public, keyless endpoint
    CACHE_NAMESPACE = "stocktwits_stream"
    CACHE_TTL_SECONDS = 120
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60.0

    def _fetch_live(self, symbol: str) -> dict:
        try:
            resp = requests.get(
                f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json",
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            raise DataClientError(f"StockTwits stream request failed for {symbol}: {e}") from e

        payload = resp.json()
        messages = payload.get("messages", [])
        if not messages:
            raise DataClientError(f"StockTwits returned no messages for {symbol}")

        return {
            "symbol": symbol,
            "messages": [
                {
                    "body": m.get("body", ""),
                    "sentiment": (m.get("entities", {}).get("sentiment") or {}).get("basic"),  # 'Bullish'/'Bearish'/None
                }
                for m in messages
            ],
        }


def get_combined_social_sentiment(symbol: str) -> tuple:
    """Merges Twitter + Reddit + StockTwits into ONE social-sentiment
    reading. Returns (result, data_source, reason).

    result = {sentiment_score (-1..1), social_volume, sources_used}

    data_source is 'real' if at least one sub-source responded,
    'real_partial' noted via sources_used length, or 'degraded' if all
    three failed — never fabricates a combined score from zero sources.
    """
    scores = []
    volume = 0
    sources_used = []
    degraded_reasons = []

    twitter = TwitterCashtagClient()
    tw_data, tw_source, tw_reason = twitter.fetch(symbol=symbol)
    if tw_source in ("real", "cached_real") and tw_data:
        tweet_scores = [score_text(t) for t in tw_data.get("tweets", [])]
        if tweet_scores:
            scores.append(sum(tweet_scores) / len(tweet_scores))
            volume += len(tweet_scores)
            sources_used.append("twitter")
    else:
        degraded_reasons.append(f"twitter: {tw_reason}")

    reddit = RedditClient()
    rd_data, rd_source, rd_reason = reddit.fetch(symbol=symbol)
    if rd_source in ("real", "cached_real") and rd_data:
        post_scores = [score_text(p) for p in rd_data.get("posts", [])]
        if post_scores:
            scores.append(sum(post_scores) / len(post_scores))
            volume += len(post_scores)
            sources_used.append("reddit")
    else:
        degraded_reasons.append(f"reddit: {rd_reason}")

    stocktwits = StockTwitsClient()
    st_data, st_source, st_reason = stocktwits.fetch(symbol=symbol)
    if st_source in ("real", "cached_real") and st_data:
        st_scores = []
        for m in st_data.get("messages", []):
            if m.get("sentiment") == "Bullish":
                st_scores.append(1)
            elif m.get("sentiment") == "Bearish":
                st_scores.append(-1)
            else:
                st_scores.append(score_text(m.get("body", "")))
        if st_scores:
            scores.append(sum(st_scores) / len(st_scores))
            volume += len(st_scores)
            sources_used.append("stocktwits")
    else:
        degraded_reasons.append(f"stocktwits: {st_reason}")

    if not scores:
        return None, "degraded", "; ".join(degraded_reasons)

    combined = {
        "sentiment_score": sum(scores) / len(scores),
        "social_volume": volume,
        "sources_used": sources_used,
        "degraded_reasons": degraded_reasons,
    }
    data_source = "real" if len(sources_used) == 3 else "real_partial"
    return combined, data_source, None
