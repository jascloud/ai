import React, { useEffect, useState } from 'react';
import '../styles/Dashboard.css';

const PLAN_LABELS = { free: 'Free', basic: 'Basic', pro: 'Pro', premium: 'Premium' };

export default function Dashboard({ recipes, workouts, user, onNavigate }) {
  const [todayStats, setTodayStats] = useState({
    caloriesBurned: 0,
    workoutCount: 0,
    recipesLogged: 0
  });

  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    const todayWorkouts = workouts.filter(w => w.date === today);

    const caloriesBurned = todayWorkouts.reduce((sum, w) => sum + (w.calories || 0), 0);
    const workoutCount = todayWorkouts.length;

    setTodayStats({
      caloriesBurned,
      workoutCount,
      recipesLogged: 0
    });
  }, [workouts]);

  const featuredRecipes = recipes.slice(0, 3);

  return (
    <div className="dashboard">
      <section className="welcome-section">
        <h1>Welcome to FitCook India</h1>
        <p className="subtitle">Your personalized fitness and nutrition guide</p>
        <div className="plan-status">
          <span className="plan-badge">{PLAN_LABELS[user?.plan || 'free']} Plan</span>
          {(!user?.plan || user.plan === 'free') && (
            <button className="btn btn-secondary plan-cta" onClick={() => onNavigate?.('plans')}>
              Upgrade from ₹99/month
            </button>
          )}
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-content">
            <div className="stat-value">{todayStats.caloriesBurned}</div>
            <div className="stat-label">Calories Burned Today</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💪</div>
          <div className="stat-content">
            <div className="stat-value">{todayStats.workoutCount}</div>
            <div className="stat-label">Workouts Today</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🥗</div>
          <div className="stat-content">
            <div className="stat-value">{recipes.length}</div>
            <div className="stat-label">Healthy Recipes Available</div>
          </div>
        </div>
      </section>

      <section className="featured-section">
        <h2>Featured Healthy Recipes</h2>
        <div className="recipe-preview-grid">
          {featuredRecipes.map(recipe => (
            <div key={recipe.id} className="recipe-preview-card">
              <div className="recipe-header">
                <h3>{recipe.name}</h3>
                <span className="recipe-tag">{recipe.cuisine_type}</span>
              </div>

              <div className="recipe-meta">
                <span className="meta-item">
                  <span className="meta-icon">⏱️</span>
                  {recipe.prep_time + recipe.cook_time} min
                </span>
                <span className="meta-item">
                  <span className="meta-icon">🔥</span>
                  {recipe.calories} cal
                </span>
                <span className="meta-item">
                  <span className="meta-icon">👥</span>
                  {recipe.servings} servings
                </span>
              </div>

              <p className="recipe-description">{recipe.cuisine}</p>

              <button className="btn btn-primary btn-small">View Recipe</button>
            </div>
          ))}
        </div>
      </section>

      <section className="tips-section">
        <h2>Wellness Tips for Indian Fitness</h2>
        <div className="tips-grid">
          <div className="tip-card">
            <div className="tip-icon">🧘</div>
            <h3>Yoga Benefits</h3>
            <p>Traditional yoga practices improve flexibility, balance, and mental clarity. Start with 20 minutes daily.</p>
          </div>

          <div className="tip-card">
            <div className="tip-icon">🌿</div>
            <h3>Ayurvedic Eating</h3>
            <p>Balance your meals with turmeric, ginger, and spices. Eat according to your body type (dosha).</p>
          </div>

          <div className="tip-card">
            <div className="tip-icon">💧</div>
            <h3>Hydration</h3>
            <p>Drink warm water with lemon in the morning. Stay hydrated throughout the day, especially in Indian heat.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
