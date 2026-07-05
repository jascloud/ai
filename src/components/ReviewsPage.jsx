import React, { useEffect, useState } from 'react';
import '../styles/Reviews.css';

const STAR_FILTERS = [null, 5, 4, 3, 2, 1];

function Stars({ rating }) {
  return (
    <span className="stars" aria-label={`${rating} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map(n => (
        <span key={n} className={n <= rating ? 'star filled' : 'star'}>★</span>
      ))}
    </span>
  );
}

export default function ReviewsPage() {
  const [summary, setSummary] = useState({ average: 0, totalAll: 0, distribution: {} });
  const [reviews, setReviews] = useState([]);
  const [page, setPage] = useState(1);
  const [ratingFilter, setRatingFilter] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    setReviews([]);
    setPage(1);
    setHasMore(true);
    fetchReviews(1, ratingFilter, true);
  }, [ratingFilter]);

  const fetchReviews = async (pageToLoad, rating, replace) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: pageToLoad, limit: 12 });
      if (rating) params.set('rating', rating);
      const response = await fetch(`/api/reviews?${params.toString()}`);
      const data = await response.json();

      setSummary({ average: data.average, totalAll: data.totalAll, distribution: data.distribution });
      setReviews(prev => replace ? data.reviews : [...prev, ...data.reviews]);
      setHasMore(pageToLoad * data.limit < data.total);
      setPage(pageToLoad);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => fetchReviews(page + 1, ratingFilter, false);

  const distTotal = Object.values(summary.distribution || {}).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="reviews-page">
      <div className="reviews-header">
        <h1>Member Reviews</h1>
        <p className="reviews-subtitle">What OJAS members are saying</p>
      </div>

      <div className="reviews-summary">
        <div className="summary-score">
          <div className="score-value">{summary.average || '—'}</div>
          <Stars rating={Math.round(summary.average || 0)} />
          <p className="score-total">{summary.totalAll || 0} reviews</p>
        </div>

        <div className="summary-distribution">
          {[5, 4, 3, 2, 1].map(star => {
            const count = summary.distribution?.[star] || 0;
            const pct = Math.round((count / distTotal) * 100);
            return (
              <button
                key={star}
                className={`dist-row ${ratingFilter === star ? 'active' : ''}`}
                onClick={() => setRatingFilter(ratingFilter === star ? null : star)}
              >
                <span className="dist-label">{star}★</span>
                <span className="dist-bar-track">
                  <span className="dist-bar-fill" style={{ width: `${pct}%` }} />
                </span>
                <span className="dist-count">{count}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="filter-bar">
        {STAR_FILTERS.map(star => (
          <button
            key={star ?? 'all'}
            className={`filter-btn ${ratingFilter === star ? 'active' : ''}`}
            onClick={() => setRatingFilter(star)}
          >
            {star ? `${star}★` : 'All'}
          </button>
        ))}
      </div>

      <div className="reviews-grid">
        {reviews.map(review => (
          <div key={review.id} className="review-card">
            <div className="review-card-header">
              <div className="review-avatar">{review.name.charAt(0)}</div>
              <div className="review-identity">
                <div className="review-name">
                  {review.name}
                  {review.verified ? <span className="verified-badge" title="Verified member">✓</span> : null}
                </div>
                <div className="review-location">{review.location}</div>
              </div>
              <span className="plan-chip">{review.plan}</span>
            </div>

            <Stars rating={review.rating} />
            <h3 className="review-title">{review.title}</h3>
            <p className="review-body">{review.body}</p>
            <div className="review-date">{new Date(review.created_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })}</div>
          </div>
        ))}
      </div>

      {reviews.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h3>No reviews match this filter</h3>
          <p>Try a different star rating.</p>
        </div>
      )}

      {hasMore && (
        <button className="btn btn-secondary load-more" onClick={loadMore} disabled={loading}>
          {loading ? 'Loading...' : 'Load More Reviews'}
        </button>
      )}
    </div>
  );
}
