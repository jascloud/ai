import React, { useState } from 'react';
import '../styles/RecipeExplorer.css';

export default function RecipeExplorer({ recipes }) {
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [filter, setFilter] = useState('All');

  const categories = ['All', 'High Protein', 'Vegetarian', 'Quick Breakfast', 'Low Calorie'];

  const filteredRecipes = filter === 'All'
    ? recipes
    : recipes.filter(r => r.cuisine_type === filter);

  return (
    <div className="recipe-explorer">
      <div className="explorer-header">
        <h1>Indian Healthy Recipes</h1>
        <p className="explorer-subtitle">Discover nutritious traditional and fusion recipes</p>
      </div>

      <div className="filter-bar">
        {categories.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${filter === cat ? 'active' : ''}`}
            onClick={() => setFilter(cat)}
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
                <h3>{recipe.name}</h3>
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

        {selectedRecipe && (
          <div className="recipe-modal-overlay" onClick={() => setSelectedRecipe(null)}>
            <div className="recipe-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={() => setSelectedRecipe(null)}>✕</button>

              <div className="modal-content">
                <h2>{selectedRecipe.name}</h2>
                <p className="modal-cuisine">{selectedRecipe.cuisine}</p>

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

                <div className="modal-actions">
                  <button className="btn btn-primary">Add to Meal Plan</button>
                  <button className="btn btn-secondary">Save Recipe</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
