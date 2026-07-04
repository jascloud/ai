import React, { useState } from 'react';
import '../styles/WorkoutTracker.css';

const WORKOUT_TYPES = [
  { id: 'yoga', name: 'Yoga', icon: '🧘', calories: 150 },
  { id: 'running', name: 'Running', icon: '🏃', calories: 300 },
  { id: 'cycling', name: 'Cycling', icon: '🚴', calories: 250 },
  { id: 'strength', name: 'Strength Training', icon: '🏋️', calories: 280 },
  { id: 'swimming', name: 'Swimming', icon: '🏊', calories: 320 },
  { id: 'walking', name: 'Walking', icon: '🚶', calories: 150 },
  { id: 'pilates', name: 'Pilates', icon: '💪', calories: 180 },
  { id: 'zumba', name: 'Zumba', icon: '💃', calories: 240 }
];

export default function WorkoutTracker({ workouts, onAddWorkout }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    duration: 30,
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const workoutType = WORKOUT_TYPES.find(w => w.id === formData.type);
    const calories = Math.round((workoutType.calories / 30) * formData.duration);

    onAddWorkout({
      type: formData.type,
      duration: formData.duration,
      calories,
      date: formData.date,
      notes: formData.notes
    });

    setFormData({ type: '', duration: 30, date: new Date().toISOString().split('T')[0], notes: '' });
    setShowForm(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Group workouts by date
  const groupedWorkouts = workouts.reduce((acc, workout) => {
    if (!acc[workout.date]) {
      acc[workout.date] = [];
    }
    acc[workout.date].push(workout);
    return acc;
  }, {});

  const sortedDates = Object.keys(groupedWorkouts).sort().reverse();

  const getTotalStats = () => {
    return {
      totalCalories: workouts.reduce((sum, w) => sum + (w.calories || 0), 0),
      totalWorkouts: workouts.length,
      totalMinutes: workouts.reduce((sum, w) => sum + (w.duration || 0), 0)
    };
  };

  const stats = getTotalStats();

  return (
    <div className="workout-tracker">
      <div className="tracker-header">
        <h1>Workout Tracker</h1>
        <p className="tracker-subtitle">Log your fitness activities and track progress</p>
      </div>

      <div className="stats-overview">
        <div className="overview-stat">
          <div className="overview-icon">🔥</div>
          <div>
            <div className="overview-value">{stats.totalCalories}</div>
            <div className="overview-label">Total Calories</div>
          </div>
        </div>
        <div className="overview-stat">
          <div className="overview-icon">💪</div>
          <div>
            <div className="overview-value">{stats.totalWorkouts}</div>
            <div className="overview-label">Total Workouts</div>
          </div>
        </div>
        <div className="overview-stat">
          <div className="overview-icon">⏱️</div>
          <div>
            <div className="overview-value">{stats.totalMinutes}</div>
            <div className="overview-label">Total Minutes</div>
          </div>
        </div>
      </div>

      <div className="tracker-content">
        <button className="btn btn-primary btn-add-workout" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Cancel' : '+ Add Workout'}
        </button>

        {showForm && (
          <form className="workout-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="type">Workout Type</label>
              <div className="workout-type-grid">
                {WORKOUT_TYPES.map(type => (
                  <label key={type.id} className="workout-option">
                    <input
                      type="radio"
                      name="type"
                      value={type.id}
                      checked={formData.type === type.id}
                      onChange={handleChange}
                      required
                    />
                    <span className="workout-option-content">
                      <span className="workout-option-icon">{type.icon}</span>
                      <span className="workout-option-name">{type.name}</span>
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="duration">Duration (minutes)</label>
                <input
                  type="number"
                  id="duration"
                  name="duration"
                  min="5"
                  max="240"
                  value={formData.duration}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="date">Date</label>
                <input
                  type="date"
                  id="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="notes">Notes</label>
              <textarea
                id="notes"
                name="notes"
                placeholder="How did you feel? Any achievements?"
                value={formData.notes}
                onChange={handleChange}
                rows="3"
              />
            </div>

            <button type="submit" className="btn btn-primary btn-full">
              Log Workout
            </button>
          </form>
        )}

        <div className="workouts-list">
          {sortedDates.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🏋️</div>
              <h3>No workouts logged yet</h3>
              <p>Start your fitness journey by logging your first workout!</p>
            </div>
          ) : (
            sortedDates.map(date => (
              <div key={date} className="workout-day-group">
                <h3 className="date-header">{new Date(date).toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</h3>
                <div className="workouts-day">
                  {groupedWorkouts[date].map((workout, idx) => {
                    const workoutType = WORKOUT_TYPES.find(w => w.id === workout.type);
                    return (
                      <div key={idx} className="workout-item">
                        <div className="workout-icon">{workoutType?.icon}</div>
                        <div className="workout-details">
                          <div className="workout-name">{workoutType?.name}</div>
                          {workout.notes && <div className="workout-notes">{workout.notes}</div>}
                        </div>
                        <div className="workout-stats">
                          <span className="stat-badge">⏱️ {workout.duration}m</span>
                          <span className="stat-badge">🔥 {workout.calories}cal</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
