import React from 'react';
import '../styles/FeaturedVoices.css';

// Fictional personas created for OJAS — not real public figures.
const VOICES = [
  {
    name: 'Kabir Anand',
    role: 'Fictional Strength Coach, OJAS Ambassador',
    quote: "OJAS is the first plan that didn't ask me to choose between my grandmother's dal and my macros. Train hard, eat real food, everywhere I travel.",
    avatar: '🏋️'
  },
  {
    name: 'Meera Iyer',
    role: 'Fictional Yoga & Breathwork Instructor',
    quote: 'The daily plan adapts to how I actually feel — some days it is Surya Namaskar, some days it is a full HIIT circuit. That flexibility is rare.',
    avatar: '🧘'
  },
  {
    name: 'Diego Fontana',
    role: 'Fictional Nutrition Coach, Milan',
    quote: 'My clients used to fall off Indian meal plans because nothing felt familiar. OJAS gave them Italian and Mediterranean options that hit the same targets.',
    avatar: '🍝'
  },
  {
    name: 'Aaliyah Osei',
    role: 'Fictional Marathon Runner, OJAS Ambassador',
    quote: 'Logging a run used to feel like admin. Now it feeds straight into a plan that actually adjusts my next day of meals and recovery work.',
    avatar: '🏃'
  }
];

export default function FeaturedVoices() {
  return (
    <section className="featured-voices">
      <div className="voices-header">
        <h2>Voices of OJAS</h2>
        <p className="voices-subtitle">Illustrative member and ambassador profiles created for this demo</p>
      </div>

      <div className="voices-grid">
        {VOICES.map((voice, i) => (
          <figure key={i} className="voice-card">
            <span className="voice-quote-mark">&ldquo;</span>
            <blockquote>{voice.quote}</blockquote>
            <figcaption>
              <span className="voice-avatar">{voice.avatar}</span>
              <div>
                <div className="voice-name">{voice.name}</div>
                <div className="voice-role">{voice.role}</div>
              </div>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
