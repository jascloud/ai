import React from 'react';

// Fictional coach personas created for OJAS — not real people, no photos used.
const COACHES = [
  { name: 'Coach Arav Malhotra', specialty: 'Strength & Conditioning', bio: 'Builds progressive strength programs for lifters at every level.', avatar: '🏋️' },
  { name: 'Coach Naomi Bekele', specialty: 'Marathon & Endurance', bio: 'Coaches distance runners from first 5K to marathon block.', avatar: '🏃' },
  { name: 'Coach Priya Nambiar', specialty: 'Nutrition & Metabolic Health', bio: 'Builds sustainable eating plans around your actual kitchen.', avatar: '🥗' },
  { name: 'Coach Sana Yamamoto', specialty: 'Yoga & Mobility', bio: 'Blends breathwork and mobility work for long-term recovery.', avatar: '🧘' }
];

export default function CoachesPreview() {
  return (
    <section className="coaches-preview">
      <div className="coaches-header">
        <h2>Meet Your Coaches</h2>
        <p className="coaches-subtitle">Illustrative coach profiles created for this demo — matched 1:1 on the Elite plan</p>
      </div>

      <div className="coaches-grid">
        {COACHES.map((coach, i) => (
          <div key={i} className="coach-card">
            <div className="coach-avatar">{coach.avatar}</div>
            <div className="coach-name">{coach.name}</div>
            <div className="coach-specialty">{coach.specialty}</div>
            <p className="coach-bio">{coach.bio}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
