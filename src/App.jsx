import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import PlansPage from './components/PlansPage';
import Meals from './components/Meals';
import ExercisesPage from './components/ExercisesPage';
import WorkoutTracker from './components/WorkoutTracker';
import ReviewsPage from './components/ReviewsPage';
import Footer from './components/Footer';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'plans', label: 'Plans' },
  { id: 'meals', label: 'Meals' },
  { id: 'exercises', label: 'Exercises' },
  { id: 'workouts', label: 'Workouts' },
  { id: 'reviews', label: 'Reviews' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userId] = useState('demo-user-1');
  const [user, setUser] = useState(null);
  const [recipes, setRecipes] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [workouts, setWorkouts] = useState([]);

  useEffect(() => {
    fetchUser();
    fetchRecipes();
    fetchExercises();
    fetchWorkouts();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      const data = await response.json();
      setUser(data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  };

  const fetchRecipes = async () => {
    try {
      const response = await fetch('/api/recipes');
      const data = await response.json();
      setRecipes(data);
    } catch (error) {
      console.error('Failed to fetch recipes:', error);
    }
  };

  const fetchExercises = async () => {
    try {
      const response = await fetch('/api/exercises');
      const data = await response.json();
      setExercises(data);
    } catch (error) {
      console.error('Failed to fetch exercises:', error);
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

  const handleLogExercise = async (exercise) => {
    await handleAddWorkout({
      type: exercise.category.toLowerCase(),
      duration: exercise.duration_min,
      calories: exercise.calories_per_min * exercise.duration_min,
      date: new Date().toISOString().split('T')[0],
      notes: exercise.name
    });
  };

  const handleSubscribe = async (planId, billingCycle) => {
    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, planId, billingCycle })
      });
      const data = await response.json();
      setUser(data);
    } catch (error) {
      console.error('Failed to subscribe:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🔥</span>
            <span className="logo-text">OJAS</span>
            <span className="logo-tagline">Train. Nourish. Rise.</span>
          </div>
          <nav className="nav-tabs">
            {NAV_ITEMS.map(item => (
              <button
                key={item.id}
                className={`nav-tab ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && (
          <Dashboard recipes={recipes} workouts={workouts} user={user} onNavigate={setActiveTab} />
        )}
        {activeTab === 'plans' && <PlansPage user={user} onSubscribe={handleSubscribe} />}
        {activeTab === 'meals' && <Meals recipes={recipes} userId={userId} />}
        {activeTab === 'exercises' && <ExercisesPage exercises={exercises} onLogExercise={handleLogExercise} />}
        {activeTab === 'workouts' && <WorkoutTracker workouts={workouts} onAddWorkout={handleAddWorkout} />}
        {activeTab === 'reviews' && <ReviewsPage />}
      </main>

      <Footer />
    </div>
  );
}
