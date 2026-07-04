import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import RecipeExplorer from './components/RecipeExplorer';
import WorkoutTracker from './components/WorkoutTracker';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userId] = useState('demo-user-1');
  const [recipes, setRecipes] = useState([]);
  const [workouts, setWorkouts] = useState([]);

  useEffect(() => {
    fetchRecipes();
    fetchWorkouts();
  }, []);

  const fetchRecipes = async () => {
    try {
      const response = await fetch('/api/recipes');
      const data = await response.json();
      setRecipes(data);
    } catch (error) {
      console.error('Failed to fetch recipes:', error);
    }
  };

  const fetchWorkouts = async () => {
    try {
      const response = await fetch(`/api/workouts/${userId}`);
      const data = await response.json();
      setWorkouts(data);
    } catch (error) {
      console.error('Failed to fetch workouts:', error);
    }
  };

  const handleAddWorkout = async (workout) => {
    try {
      const response = await fetch('/api/workouts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...workout, userId })
      });
      await response.json();
      fetchWorkouts();
    } catch (error) {
      console.error('Failed to add workout:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">💪</span>
            <span className="logo-text">FitCook India</span>
          </div>
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              Dashboard
            </button>
            <button
              className={`nav-tab ${activeTab === 'recipes' ? 'active' : ''}`}
              onClick={() => setActiveTab('recipes')}
            >
              Recipes
            </button>
            <button
              className={`nav-tab ${activeTab === 'workouts' ? 'active' : ''}`}
              onClick={() => setActiveTab('workouts')}
            >
              Workouts
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard recipes={recipes} workouts={workouts} />}
        {activeTab === 'recipes' && <RecipeExplorer recipes={recipes} />}
        {activeTab === 'workouts' && <WorkoutTracker workouts={workouts} onAddWorkout={handleAddWorkout} />}
      </main>
    </div>
  );
}
