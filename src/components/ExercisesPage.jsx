import React, { useEffect, useState } from 'react';
import '../styles/Exercises.css';

const CATEGORIES = ['All', 'Strength', 'Cardio', 'Yoga', 'Core', 'Flexibility', 'HIIT'];
const CATEGORY_ICONS = {
  Strength: '🏋️',
  Cardio: '🏃',
  Yoga: '🧘',
  Core: '🔥',
  Flexibility: '🤸',
  HIIT: '⚡'
};
const PAGE_SIZE = 24;

export default function ExercisesPage({ exercises, onLogExercise }) {
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [difficultyFilter, setDifficultyFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [loggedId, setLoggedId] = useState(null);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const difficulties = ['All', 'Beginner', 'Intermediate', 'Advanced'];

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [categoryFilter, difficultyFilter, searchTerm]);

  const filteredExercises = exercises.filter(ex => {
    const matchesCategory = categoryFilter === 'All' || ex.category === categoryFilter;
    const matchesDifficulty = difficultyFilter === 'All' || ex.difficulty === difficultyFilter;
    const matchesSearch = !searchTerm || ex.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesDifficulty && matchesSearch;
  });

  const visibleExercises = filteredExercises.slice(0, visibleCount);

  const handleLog = async (exercise) => {
    await onLogExercise(exercise);
    setLoggedId(exercise.id);
    setTimeout(() => setLoggedId(null), 2000);
  };

  return (
    <div className="exercises-page">
      <div className="exercises-header">
        <h1>Exercise Library</h1>
        <p className="exercises-subtitle">Strength, cardio, yoga and more — build your own routine</p>
      </div>

      <div className="exercises-search">
        <input
          type="search"
          placeholder={`Search ${exercises.length.toLocaleString()} exercises by name...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="filter-bar">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${categoryFilter === cat ? 'active' : ''}`}
            onClick={() => setCategoryFilter(cat)}
          >
            {cat !== 'All' ? `${CATEGORY_ICONS[cat]} ${cat}` : cat}
          </button>
        ))}
      </div>

      <div className="filter-bar">
        {difficulties.map(diff => (
          <button
            key={diff}
            className={`filter-btn secondary ${difficultyFilter === diff ? 'active' : ''}`}
            onClick={() => setDifficultyFilter(diff)}
          >
            {diff}
          </button>
        ))}
      </div>

      <p className="results-count">{filteredExercises.length.toLocaleString()} exercises match your filters</p>

      <div className="exercise-grid">
        {visibleExercises.map(exercise => (
          <div key={exercise.id} className="exercise-card">
            <div className="exercise-card-header">
              <span className="exercise-icon">{CATEGORY_ICONS[exercise.category]}</span>
              <span className={`difficulty-badge difficulty-${exercise.difficulty.toLowerCase()}`}>
                {exercise.difficulty}
              </span>
            </div>

            <h3>{exercise.name}</h3>
            <p className="exercise-muscle">{exercise.muscle_group}</p>

            <div className="exercise-stats">
              <span className="stat"><span className="stat-icon">⏱️</span>{exercise.duration_min}m</span>
              <span className="stat"><span className="stat-icon">🔥</span>{exercise.calories_per_min * exercise.duration_min} cal</span>
              <span className="stat"><span className="stat-icon">🛠️</span>{exercise.equipment}</span>
            </div>

            <div className="exercise-actions">
              <button className="btn btn-secondary" onClick={() => setSelectedExercise(exercise)}>
                View Details
              </button>
              <button
                className="btn btn-primary"
                onClick={() => handleLog(exercise)}
              >
                {loggedId === exercise.id ? '✓ Logged' : 'Log It'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredExercises.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🏋️</div>
          <h3>No exercises match these filters</h3>
          <p>Try a different category, difficulty, or search term.</p>
        </div>
      )}

      {visibleCount < filteredExercises.length && (
        <button className="btn btn-secondary load-more" onClick={() => setVisibleCount(v => v + PAGE_SIZE)}>
          Load More Exercises ({filteredExercises.length - visibleCount} more)
        </button>
      )}

      {selectedExercise && (
        <div className="exercise-modal-overlay" onClick={() => setSelectedExercise(null)}>
          <div className="exercise-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedExercise(null)}>✕</button>

            <div className="modal-content">
              <h2>{selectedExercise.name}</h2>
              <p className="modal-muscle">{selectedExercise.muscle_group} &middot; {selectedExercise.category}</p>

              <div className="modal-stats-grid">
                <div className="modal-stat">
                  <div className="stat-icon">⏱️</div>
                  <div>
                    <div className="stat-label">Duration</div>
                    <div className="stat-value">{selectedExercise.duration_min} min</div>
                  </div>
                </div>
                <div className="modal-stat">
                  <div className="stat-icon">🔥</div>
                  <div>
                    <div className="stat-label">Calories</div>
                    <div className="stat-value">{selectedExercise.calories_per_min * selectedExercise.duration_min}</div>
                  </div>
                </div>
                <div className="modal-stat">
                  <div className="stat-icon">🛠️</div>
                  <div>
                    <div className="stat-label">Equipment</div>
                    <div className="stat-value modal-stat-text">{selectedExercise.equipment}</div>
                  </div>
                </div>
                <div className="modal-stat">
                  <div className="stat-icon">📊</div>
                  <div>
                    <div className="stat-label">Level</div>
                    <div className="stat-value modal-stat-text">{selectedExercise.difficulty}</div>
                  </div>
                </div>
              </div>

              <div className="modal-section">
                <h3>How to do it</h3>
                <ol className="instructions-list">
                  {selectedExercise.instructions.map((instr, i) => (
                    <li key={i}>{instr}</li>
                  ))}
                </ol>
              </div>

              {selectedExercise.tips && (
                <div className="modal-section tip-box">
                  <h3>Tip</h3>
                  <p>{selectedExercise.tips}</p>
                </div>
              )}

              <button
                className="btn btn-primary btn-full"
                onClick={() => { handleLog(selectedExercise); setSelectedExercise(null); }}
              >
                Log This Workout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
