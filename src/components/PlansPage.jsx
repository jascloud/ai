import React, { useState } from 'react';
import '../styles/Plans.css';
import CoachesPreview from './CoachesPreview';

const PLANS = [
  {
    id: 'basic',
    name: 'Basic',
    price: 99,
    tagline: 'Get moving',
    features: [
      'Daily meal suggestions',
      'Full exercise library access (1,000+ exercises)',
      'Unlimited workout logging',
      '1,000+ recipe collection',
      'Community Telegram tips channel'
    ]
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 199,
    tagline: 'Most popular',
    featured: true,
    features: [
      'Everything in Basic',
      'Personalized daily meal plans',
      'All international cuisines unlocked',
      'Progress tracking & analytics',
      'WhatsApp motivation group access'
    ]
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 299,
    tagline: 'Go all in',
    features: [
      'Everything in Pro',
      'Custom workout routines',
      'Downloadable meal plans',
      'Early access to new recipes',
      'Priority WhatsApp support'
    ]
  },
  {
    id: 'elite',
    name: 'Elite',
    price: 999,
    tagline: '1:1 coaching',
    elite: true,
    features: [
      'Everything in Premium',
      'Matched with a certified personal coach',
      'Weekly video check-ins',
      'Custom weekly plan revisions',
      'Direct WhatsApp line to your coach'
    ]
  }
];

const COUPONS = {
  FIT10: 0.10,
  WELCOME20: 0.20
};

export default function PlansPage({ user, onSubscribe }) {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [couponInput, setCouponInput] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [couponMessage, setCouponMessage] = useState('');
  const [subscribing, setSubscribing] = useState(null);

  const annualDiscount = 0.2; // 20% off when billed annually

  const applyCoupon = () => {
    const code = couponInput.trim().toUpperCase();
    if (COUPONS[code]) {
      setAppliedCoupon(code);
      setCouponMessage(`Code ${code} applied — extra ${COUPONS[code] * 100}% off`);
    } else {
      setAppliedCoupon(null);
      setCouponMessage(code ? 'Invalid code' : '');
    }
  };

  const getPrice = (basePrice) => {
    let price = basePrice;
    if (billingCycle === 'annual') {
      price = price * 12 * (1 - annualDiscount);
    }
    if (appliedCoupon) {
      price = price * (1 - COUPONS[appliedCoupon]);
    }
    return Math.round(price);
  };

  const handleSubscribe = async (planId) => {
    setSubscribing(planId);
    await onSubscribe(planId, billingCycle);
    setSubscribing(null);
  };

  const isCurrentPlan = (planId) => user?.plan === planId;

  return (
    <div className="plans-page">
      <div className="plans-header">
        <h1>Choose Your Plan</h1>
        <p className="plans-subtitle">Personalized fitness and nutrition, priced for everyone</p>
      </div>

      <div className="billing-toggle">
        <button
          className={`toggle-btn ${billingCycle === 'monthly' ? 'active' : ''}`}
          onClick={() => setBillingCycle('monthly')}
        >
          Monthly
        </button>
        <button
          className={`toggle-btn ${billingCycle === 'annual' ? 'active' : ''}`}
          onClick={() => setBillingCycle('annual')}
        >
          Annual <span className="save-badge">Save 20%</span>
        </button>
      </div>

      <div className="coupon-bar">
        <input
          type="text"
          placeholder="Have a discount code? (try FIT10)"
          value={couponInput}
          onChange={(e) => setCouponInput(e.target.value)}
        />
        <button className="btn btn-secondary" onClick={applyCoupon}>Apply</button>
      </div>
      {couponMessage && (
        <p className={`coupon-message ${appliedCoupon ? 'success' : 'error'}`}>{couponMessage}</p>
      )}

      <div className="plans-grid">
        {PLANS.map(plan => {
          const price = getPrice(plan.price);
          const period = billingCycle === 'annual' ? '/year' : '/month';

          return (
            <div key={plan.id} className={`plan-card ${plan.featured ? 'featured' : ''} ${plan.elite ? 'elite' : ''}`}>
              {plan.featured && <div className="featured-badge">Most Popular</div>}
              {plan.elite && <div className="featured-badge elite-badge">1:1 Coaching</div>}
              <h3>{plan.name}</h3>
              <p className="plan-tagline">{plan.tagline}</p>

              <div className="plan-price">
                <span className="currency">₹</span>
                <span className="amount">{price}</span>
                <span className="period">{period}</span>
              </div>
              {billingCycle === 'annual' && (
                <p className="price-note">≈ ₹{Math.round(price / 12)}/month billed yearly</p>
              )}

              <ul className="plan-features">
                {plan.features.map((feature, i) => (
                  <li key={i}>
                    <span className="check">✓</span> {feature}
                  </li>
                ))}
              </ul>

              <button
                className={`btn ${plan.featured ? 'btn-primary' : 'btn-secondary'} btn-full`}
                disabled={isCurrentPlan(plan.id) || subscribing === plan.id}
                onClick={() => handleSubscribe(plan.id)}
              >
                {isCurrentPlan(plan.id) ? 'Current Plan' : subscribing === plan.id ? 'Activating...' : 'Subscribe'}
              </button>
            </div>
          );
        })}
      </div>

      {user?.plan && user.plan !== 'free' && (
        <div className="current-plan-banner">
          You're on the <strong>{user.plan}</strong> plan ({user.billing_cycle}), renews {user.plan_expiry}.
        </div>
      )}

      <CoachesPreview />
    </div>
  );
}
