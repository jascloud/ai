import React from 'react';
import '../styles/About.css';

// All history, team, and press content below is fictional brand narrative
// written for this demo — OJAS is not a real registered company.
const TIMELINE = [
  { year: '1994', title: 'A single studio', text: 'Jas Singh opens the first OJAS training studio, built on a simple idea: consistency beats intensity.' },
  { year: '2001', title: 'Nutrition joins training', text: 'The first structured nutrition program launches alongside in-studio coaching.' },
  { year: '2008', title: 'Going digital', text: 'Paper logbooks give way to digital workout tracking for studio members.' },
  { year: '2013', title: 'The world enters the menu', text: 'International recipes — starting with Italian and Japanese — join the meal library.' },
  { year: '2019', title: 'OJAS, the app', text: 'The studio model becomes a global app: daily plans, an exercise library, and a subscription model anyone can access.' },
  { year: '2023', title: '1:1 coaching returns', text: 'The Elite tier brings personal coach matching back, this time available anywhere.' },
  { year: '2026', title: 'Where we are now', text: 'A global platform spanning 30+ countries, 1,000+ recipes, and 1,000+ exercises — still built on the same idea from 1994.' }
];

const VALUES = [
  { icon: '🔁', title: 'Consistency Over Intensity', text: "A plan you'll actually repeat beats a perfect plan you'll abandon in two weeks." },
  { icon: '🍛', title: 'Real Food, Real Life', text: "Your plan should fit your kitchen and your culture, not replace them." },
  { icon: '💤', title: 'Recovery Is Training', text: 'Adaptation happens during rest. We build it into every plan, not around it.' },
  { icon: '🌍', title: 'Global by Design', text: 'Fitness advice that only works in one country is just local advice.' }
];

// Leadership team for this demo brand.
const TEAM = [
  { name: 'Jas Singh', role: 'Founder & CEO', avatar: '👤' },
  { name: 'Marcus Webb', role: 'Head of Training', avatar: '👤' },
  { name: 'Farah Haddad', role: 'Head of Nutrition', avatar: '👤' }
];

// Invented publication names — not real news outlets. Written as brand flavor
// text for this demo, not a claim of actual press coverage.
const PRESS = [
  { outlet: 'Global Wellness Report', quote: 'A meal-planning approach other apps will likely be copying within a year.' },
  { outlet: 'FitTech Weekly', quote: 'Quietly solves the cuisine-fatigue problem most nutrition apps never address.' },
  { outlet: 'The Nutrition Times', quote: "Proof that personalization doesn't require abandoning culture." },
  { outlet: 'Active Living Journal', quote: 'One of the more thoughtful entries in a crowded fitness-app category.' }
];

export default function AboutPage() {
  return (
    <div className="about-page">
      <div className="about-header">
        <h1>Our Story</h1>
        <p className="about-subtitle">From one studio in 1994 to a global platform — same idea, bigger reach</p>
      </div>

      <section className="founder-note">
        <div className="founder-avatar">👤</div>
        <blockquote>
          "I opened the first OJAS studio because every plan I'd tried asked me to give something
          up — my food, my schedule, or my patience with a program that didn't fit my life. OJAS is
          the plan I wish had existed then: one that adapts to you, instead of the other way around."
        </blockquote>
        <div className="founder-signature">— Jas Singh, Founder &amp; CEO</div>
      </section>

      <section className="timeline-section">
        <h2>Timeline</h2>
        <div className="timeline">
          {TIMELINE.map((item, i) => (
            <div key={i} className="timeline-item">
              <div className="timeline-year">{item.year}</div>
              <div className="timeline-content">
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="values-section">
        <h2>What We Believe</h2>
        <div className="values-grid">
          {VALUES.map((value, i) => (
            <div key={i} className="value-card">
              <div className="value-icon">{value.icon}</div>
              <h3>{value.title}</h3>
              <p>{value.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="team-section">
        <h2>Leadership</h2>
        <p className="section-note">Illustrative profiles created for this demo</p>
        <div className="team-grid">
          {TEAM.map((member, i) => (
            <div key={i} className="team-card">
              <div className="team-avatar">{member.avatar}</div>
              <div className="team-name">{member.name}</div>
              <div className="team-role">{member.role}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="press-section">
        <h2>In the Press</h2>
        <p className="section-note">Illustrative quotes from invented publications, written for this demo — not real press coverage</p>
        <div className="press-grid">
          {PRESS.map((item, i) => (
            <div key={i} className="press-card">
              <p className="press-quote">&ldquo;{item.quote}&rdquo;</p>
              <div className="press-outlet">{item.outlet}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
