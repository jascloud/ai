import React, { useEffect, useState } from 'react';

const STORAGE_KEY = 'ojas-health-snapshot';

function bmiCategory(bmi) {
  if (bmi < 18.5) return { label: 'Underweight', color: 'var(--color-info)' };
  if (bmi < 25) return { label: 'Typical range', color: 'var(--color-success)' };
  if (bmi < 30) return { label: 'Above typical range', color: 'var(--color-gold)' };
  return { label: 'Well above typical range', color: 'var(--color-error)' };
}

export default function HealthSnapshot() {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [restingHr, setRestingHr] = useState('');
  const [sleepHours, setSleepHours] = useState('');

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      if (saved.height) setHeight(saved.height);
      if (saved.weight) setWeight(saved.weight);
      if (saved.restingHr) setRestingHr(saved.restingHr);
      if (saved.sleepHours) setSleepHours(saved.sleepHours);
    } catch (e) { /* ignore malformed saved state */ }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ height, weight, restingHr, sleepHours }));
  }, [height, weight, restingHr, sleepHours]);

  const heightM = parseFloat(height) / 100;
  const weightKg = parseFloat(weight);
  const bmi = heightM > 0 && weightKg > 0 ? weightKg / (heightM * heightM) : null;
  const category = bmi ? bmiCategory(bmi) : null;

  return (
    <div className="health-snapshot">
      <div className="snapshot-header">
        <h2>Health Snapshot</h2>
        <p className="snapshot-note">Your own numbers, logged by you — a general reference, not a diagnosis</p>
      </div>

      <div className="snapshot-grid">
        <div className="snapshot-inputs">
          <div className="snapshot-field">
            <label htmlFor="height">Height (cm)</label>
            <input id="height" type="number" min="0" value={height} onChange={(e) => setHeight(e.target.value)} placeholder="170" />
          </div>
          <div className="snapshot-field">
            <label htmlFor="weight">Weight (kg)</label>
            <input id="weight" type="number" min="0" value={weight} onChange={(e) => setWeight(e.target.value)} placeholder="65" />
          </div>
          <div className="snapshot-field">
            <label htmlFor="restingHr">Resting Heart Rate (bpm)</label>
            <input id="restingHr" type="number" min="0" value={restingHr} onChange={(e) => setRestingHr(e.target.value)} placeholder="68" />
          </div>
          <div className="snapshot-field">
            <label htmlFor="sleepHours">Sleep Last Night (hrs)</label>
            <input id="sleepHours" type="number" min="0" step="0.5" value={sleepHours} onChange={(e) => setSleepHours(e.target.value)} placeholder="7.5" />
          </div>
        </div>

        <div className="snapshot-results">
          <div className="snapshot-stat">
            <div className="snapshot-stat-label">BMI</div>
            <div className="snapshot-stat-value">{bmi ? bmi.toFixed(1) : '—'}</div>
            {category && <div className="snapshot-stat-tag" style={{ color: category.color }}>{category.label}</div>}
          </div>
          <div className="snapshot-stat">
            <div className="snapshot-stat-label">Resting HR</div>
            <div className="snapshot-stat-value">{restingHr || '—'}</div>
            <div className="snapshot-stat-tag">Typical adult range: ~60-100 bpm</div>
          </div>
          <div className="snapshot-stat">
            <div className="snapshot-stat-label">Sleep</div>
            <div className="snapshot-stat-value">{sleepHours || '—'}</div>
            <div className="snapshot-stat-tag">General guideline: ~7-9 hrs</div>
          </div>
        </div>
      </div>

      <p className="snapshot-disclaimer">
        BMI, resting heart rate, and sleep ranges shown here are general public-health reference
        points — they don't account for individual factors like muscle mass, medication, or medical
        history. This isn't a diagnosis. Talk to your doctor about what's right for you.
      </p>
    </div>
  );
}
