import React from 'react';
import '../styles/Footer.css';

// Brand narrative written for this demo — OJAS is a fictional company created for this project.
const STATS = [
  { value: '1994', label: 'Founded' },
  { value: '2M+', label: 'Members Worldwide' },
  { value: '30+', label: 'Countries' },
  { value: '4.8/5', label: 'Average Rating' }
];

const SOCIAL_LINKS = [
  { name: 'Instagram', icon: '📷', handle: '@ojas.fit' },
  { name: 'TikTok', icon: '🎵', handle: '@ojas.fit' },
  { name: 'YouTube', icon: '▶️', handle: 'OJAS Fit' }
];

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-content">
        <section className="footer-story">
          <h2 className="footer-brand">OJAS</h2>
          <p>
            Founded in 1994 as a single training studio, OJAS has grown into a global fitness
            and nutrition platform trusted by members across more than 30 countries. Our name
            comes from the Ayurvedic idea of ojas — vital energy — and it still shapes how we
            build every plan: train with intent, eat real food, and recover like it matters.
          </p>
        </section>

        <div className="footer-stats">
          {STATS.map((stat, i) => (
            <div key={i} className="footer-stat">
              <div className="footer-stat-value">{stat.value}</div>
              <div className="footer-stat-label">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="footer-bottom">
          <div className="footer-social">
            {SOCIAL_LINKS.map((social, i) => (
              <span key={i} className="social-pill" title={`${social.name}: ${social.handle}`}>
                <span className="social-icon">{social.icon}</span>
                {social.handle}
              </span>
            ))}
          </div>
          <p className="footer-copyright">
            © 1994–2026 OJAS. This is a demo application — brand history and figures shown here are fictional.
          </p>
        </div>
      </div>
    </footer>
  );
}
