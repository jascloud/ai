import React, { useState } from 'react';
import '../styles/Shop.css';

// Illustrated placeholder products — no product photography available in this
// environment, so each card uses a gradient + icon + the OJAS wordmark instead.
const PRODUCTS = [
  { id: 'tee-black', name: 'OJAS Flame Tee — Black', category: 'Apparel', price: 899, icon: '👕', gradient: 'grad-1' },
  { id: 'tee-crimson', name: 'OJAS Flame Tee — Crimson', category: 'Apparel', price: 899, icon: '👕', gradient: 'grad-2' },
  { id: 'hoodie', name: 'OJAS Performance Hoodie', category: 'Apparel', price: 1799, icon: '🧥', gradient: 'grad-3' },
  { id: 'cap', name: 'OJAS Training Cap', category: 'Apparel', price: 599, icon: '🧢', gradient: 'grad-4' },
  { id: 'bottle', name: 'OJAS Steel Water Bottle', category: 'Gear', price: 749, icon: '🍶', gradient: 'grad-1' },
  { id: 'mat', name: 'OJAS Yoga Mat', category: 'Gear', price: 1499, icon: '🧘', gradient: 'grad-2' },
  { id: 'bands', name: 'OJAS Resistance Band Set', category: 'Gear', price: 999, icon: '🏋️', gradient: 'grad-3' },
  { id: 'duffel', name: 'OJAS Gym Duffel Bag', category: 'Gear', price: 1999, icon: '🎒', gradient: 'grad-4' },
  { id: 'wristbands', name: 'OJAS Wristband Pair', category: 'Accessories', price: 349, icon: '💪', gradient: 'grad-1' },
  { id: 'tote', name: 'OJAS Tote Bag', category: 'Accessories', price: 499, icon: '🛍️', gradient: 'grad-2' }
];

export default function ShopPage() {
  const [cart, setCart] = useState({});
  const [checkoutMessage, setCheckoutMessage] = useState('');

  const addToCart = (productId) => {
    setCart(prev => ({ ...prev, [productId]: (prev[productId] || 0) + 1 }));
    setCheckoutMessage('');
  };

  const removeFromCart = (productId) => {
    setCart(prev => {
      const next = { ...prev };
      if (next[productId] > 1) {
        next[productId] -= 1;
      } else {
        delete next[productId];
      }
      return next;
    });
  };

  const cartItems = Object.entries(cart).map(([id, qty]) => ({
    product: PRODUCTS.find(p => p.id === id),
    qty
  }));
  const cartCount = cartItems.reduce((sum, item) => sum + item.qty, 0);
  const cartTotal = cartItems.reduce((sum, item) => sum + item.product.price * item.qty, 0);

  const handleCheckout = () => {
    setCheckoutMessage('This is a demo store — no real payment was processed. Wire up a payment gateway to go live.');
  };

  return (
    <div className="shop-page">
      <div className="shop-header">
        <h1>OJAS Merch</h1>
        <p className="shop-subtitle">Train in the brand. Demo store — checkout is illustrative only.</p>
      </div>

      <div className="shop-layout">
        <div className="product-grid">
          {PRODUCTS.map(product => (
            <div key={product.id} className="product-card">
              <div className={`product-image ${product.gradient}`}>
                <span className="product-icon">{product.icon}</span>
                <span className="product-wordmark">OJAS</span>
              </div>
              <div className="product-info">
                <span className="product-category">{product.category}</span>
                <h3>{product.name}</h3>
                <div className="product-price">₹{product.price}</div>
                <button className="btn btn-primary btn-full" onClick={() => addToCart(product.id)}>
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>

        <aside className="cart-panel">
          <h2>Your Cart {cartCount > 0 && <span className="cart-count">({cartCount})</span>}</h2>

          {cartItems.length === 0 ? (
            <p className="cart-empty">Your cart is empty.</p>
          ) : (
            <>
              <ul className="cart-list">
                {cartItems.map(({ product, qty }) => (
                  <li key={product.id} className="cart-item">
                    <span className="cart-item-icon">{product.icon}</span>
                    <div className="cart-item-info">
                      <div className="cart-item-name">{product.name}</div>
                      <div className="cart-item-meta">₹{product.price} × {qty}</div>
                    </div>
                    <button className="cart-item-remove" onClick={() => removeFromCart(product.id)} aria-label={`Remove one ${product.name}`}>
                      −
                    </button>
                  </li>
                ))}
              </ul>

              <div className="cart-total">
                <span>Total</span>
                <span>₹{cartTotal}</span>
              </div>

              <button className="btn btn-primary btn-full" onClick={handleCheckout}>
                Checkout
              </button>

              {checkoutMessage && <p className="checkout-message">{checkoutMessage}</p>}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
