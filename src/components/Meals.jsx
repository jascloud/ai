import React, { useEffect, useState } from 'react';
import '../styles/Meals.css';

const COUNTRIES = ['All', 'India', 'Italy', 'Mexico', 'Japan', 'Thailand', 'Mediterranean', 'USA', 'China'];
const MEAL_ORDER = ['breakfast', 'lunch', 'dinner', 'snack'];
const MEAL_ICONS = { breakfast: '🍳', lunch: '🥗', dinner: '🍽️', snack: '🍡' };

export default function Meals({ recipes, userId }) {
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [countryFilter, setCountryFilter] = useState('All');
  const [dailyPlan, setDailyPlan] = useState(null);

  const categories = ['All', 'High Protein', 'Vegetarian', 'Quick Breakfast', 'Low Calorie'];

  useEffect(() => {
    fetchDailyPlan();
  }, [countryFilter]);

  const fetchDailyPlan = async () => {
    try {
      const response = await fetch(`/api/daily-plan/${userId}?country=${countryFilter}`);
      const data = await response.json();
      setDailyPlan(data.plan);
    } catch (error) {
      console.error('Failed to fetch daily plan:', error);
    }
  };

  const filteredRecipes = recipes.filter(r => {
    const matchesCategory = categoryFilter === 'All' || r.cuisine_type === categoryFilter;
    const matchesCountry = countryFilter === 'All' || r.country === countryFilter;
    return matchesCategory && matchesCountry;
  });

  return (
    <div className="meals-page">
      <div className="explorer-header">
        <h1>Universal Meal Plans</h1>
        <p className="explorer-subtitle">Healthy recipes from India and around the world</p>
      </div>

      <section className="daily-plan-section">
        <h2>Today's Plan</h2>
        <div className="daily-plan-grid">
          {MEAL_ORDER.map(meal => {
            const recipe = dailyPlan?.[meal];
            return (
              <div
                key={meal}
                className={`daily-plan-card ${recipe ? 'clickable' : ''}`}
                onClick={() => recipe && setSelectedRecipe(recipe)}
              >
                <div className="daily-plan-meal">{MEAL_ICONS[meal]} {meal[0].toUpperCase() + meal.slice(1)}</div>
                {recipe ? (
                  <>
                    <h3>{recipe.name}</h3>
                    <p className="daily-plan-meta">{recipe.country} &middot; {recipe.calories} cal</p>
                  </>
                ) : (
                  <p className="daily-plan-empty">No recipe available for this filter</p>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <div className="filter-bar country-bar">
        {COUNTRIES.map(country => (
          <button
            key={country}
            className={`filter-btn ${countryFilter === country ? 'active' : ''}`}
            onClick={() => setCountryFilter(country)}
          >
            {country}
          </button>
        ))}
      </div>

      <div className="filter-bar">
        {categories.map(cat => (
          <button
            key={cat}
            className={`filter-btn secondary ${categoryFilter === cat ? 'active' : ''}`}
            onClick={() => setCategoryFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="explorer-content">
        <div className="recipe-grid">
          {filteredRecipes.map(recipe => (
            <div
              key={recipe.id}
              className="recipe-card"
              onClick={() => setSelectedRecipe(recipe)}
            >
              <div className="recipe-image-placeholder">
                🍛
              </div>
              <div className="recipe-info">
                <div className="recipe-info-header">
                  <h3>{recipe.name}</h3>
                  <span className="country-tag">{recipe.country}</span>
                </div>
                <p className="recipe-cuisine">{recipe.cuisine}</p>

                <div className="recipe-stats">
                  <span className="stat">
                    <span className="stat-icon">⏱️</span>
                    {recipe.prep_time + recipe.cook_time}m
                  </span>
                  <span className="stat">
                    <span className="stat-icon">🔥</span>
                    {recipe.calories}cal
                  </span>
                  <span className="stat">
                    <span className="stat-icon">👥</span>
                    {recipe.servings}
                  </span>
                </div>

                <button className="btn btn-primary btn-full">View Details</button>
              </div>
            </div>
          ))}
        </div>

        {filteredRecipes.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🍽️</div>
            <h3>No recipes match these filters</h3>
            <p>Try a different country or category.</p>
          </div>
        )}

        {selectedRecipe && (
          <div className="recipe-modal-overlay" onClick={() => setSelectedRecipe(null)}>
            <div className="recipe-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={() => setSelectedRecipe(null)}>✕</button>

              <div className="modal-content">
                <h2>{selectedRecipe.name}</h2>
                <p className="modal-cuisine">{selectedRecipe.cuisine} &middot; {selectedRecipe.country}</p>

                <div className="modal-stats-grid">
                  <div className="modal-stat">
                    <div className="stat-icon">⏱️</div>
                    <div>
                      <div className="stat-label">Prep Time</div>
                      <div className="stat-value">{selectedRecipe.prep_time} min</div>
                    </div>
                  </div>
                  <div className="modal-stat">
                    <div className="stat-icon">🍳</div>
                    <div>
                      <div className="stat-label">Cook Time</div>
                      <div className="stat-value">{selectedRecipe.cook_time} min</div>
                    </div>
                  </div>
                  <div className="modal-stat">
                    <div className="stat-icon">🔥</div>
                    <div>
                      <div className="stat-label">Calories</div>
                      <div className="stat-value">{selectedRecipe.calories}</div>
                    </div>
                  </div>
                  <div className="modal-stat">
                    <div className="stat-icon">👥</div>
                    <div>
                      <div className="stat-label">Servings</div>
                      <div className="stat-value">{selectedRecipe.servings}</div>
                    </div>
                  </div>
                </div>

                <div className="modal-section">
                  <h3>Ingredients</h3>
                  <ul className="ingredients-list">
                    {selectedRecipe.ingredients.map((ing, i) => (
                      <li key={i}>{ing}</li>
                    ))}
                  </ul>
                </div>

                <div className="modal-section">
                  <h3>Instructions</h3>
                  <ol className="instructions-list">
                    {selectedRecipe.instructions.map((instr, i) => (
                      <li key={i}>{instr}</li>
                    ))}
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
