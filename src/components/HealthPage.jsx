import React, { useState } from 'react';
import '../styles/Health.css';

// General educational content only — not medical advice. Every category below
// is deliberately limited to well-established, low-risk lifestyle information,
// and every card carries its own "seek a doctor" guidance. This intentionally
// does not attempt to give condition-specific treatment protocols.

const CONDITION_TRACKS = [
  { icon: '⚖️', title: 'Weight Management', text: 'Consistent movement, adequate protein, and regular sleep are commonly discussed lifestyle factors for healthy weight management.' },
  { icon: '🩸', title: 'Metabolic Health & Diabetes', text: 'Regular activity and consistent meal timing are frequently cited lifestyle factors in metabolic health discussions.' },
  { icon: '🎗️', title: 'PCOS', text: 'Regular exercise and balanced, consistent meals are commonly discussed alongside PCOS lifestyle management.' },
  { icon: '❤️', title: 'Heart Health', text: 'Regular movement, sleep quality, and stress management are widely recognized general factors in cardiovascular wellness.' },
  { icon: '🦋', title: 'Thyroid', text: 'Consistent sleep and activity levels are commonly discussed general wellness factors alongside thyroid care.' },
  { icon: '🦴', title: 'Bone Health', text: 'Weight-bearing exercise and adequate calcium and vitamin D intake are commonly cited factors in bone health.' },
  { icon: '🫁', title: 'Fatty Liver (General Wellness)', text: 'Reducing added sugar and maintaining regular movement are commonly discussed general lifestyle factors.' },
  { icon: '🌱', title: 'Fertility Support', text: 'Sleep quality, stress management, and balanced nutrition are commonly discussed general wellness factors.' },
  { icon: '💧', title: 'Kidney Health', text: 'Staying well hydrated and maintaining healthy blood pressure are commonly cited general wellness factors.' }
];

const RECOVERY_CATEGORIES = [
  {
    id: 'soreness',
    title: 'Muscle Soreness (DOMS)',
    icon: '💪',
    tips: [
      'Light movement (an easy walk) often eases soreness more than complete rest',
      'Gentle stretching once muscles feel warmed up, not cold',
      'Stay hydrated — soreness can feel worse when dehydrated',
      'A warm shower or bath can help muscles relax',
      'Allow 48-72 hours before hard-training the same muscle group again'
    ],
    redFlags: 'Swelling that keeps increasing, dark urine, or pain severe enough to limit basic movement for more than a few days — see a doctor rather than continuing to self-treat.'
  },
  {
    id: 'sprains',
    title: 'Minor Sprains & Strains',
    icon: '🩹',
    tips: [
      'Rest the area and avoid putting weight on it if it hurts to do so',
      'Ice for 15-20 minutes at a time during the first 24-48 hours',
      'Compression with an elastic bandage can help limit swelling',
      'Elevate the area above heart level when possible',
      'Gentle range-of-motion work once swelling has visibly gone down'
    ],
    redFlags: "Inability to bear any weight, visible deformity, numbness or tingling, or a popping sound at the time of injury — these need a doctor's evaluation, not home care."
  },
  {
    id: 'stiffness',
    title: 'Joint Stiffness',
    icon: '🦿',
    tips: [
      'A short warm-up before activity, even 5 minutes, reduces stiffness',
      'Regular gentle movement tends to help more than prolonged inactivity',
      'Alternating between sitting and standing during long desk sessions',
      'Consistent, moderate activity most days rather than occasional intense sessions'
    ],
    redFlags: 'Joint swelling with redness and warmth, or stiffness that comes with fever, is worth a same-week doctor visit rather than home management.'
  },
  {
    id: 'headaches',
    title: 'Tension Headaches',
    icon: '🤕',
    tips: [
      'Check hydration first — mild dehydration is a common contributor',
      'A regular sleep schedule tends to reduce frequency over time',
      'Short screen breaks during long work sessions',
      'Gentle neck and shoulder stretches if tension is felt there',
      'Moderating caffeine intake and avoiding sudden withdrawal'
    ],
    redFlags: "A sudden, severe headache unlike any before, one with vision changes, confusion, stiff neck, or fever needs emergency care immediately — don't wait this one out at home."
  },
  {
    id: 'back-discomfort',
    title: 'Lower Back Discomfort',
    icon: '🧍',
    tips: [
      'Gentle walking is usually better than prolonged bed rest',
      'Core-supportive movement like planks, once pain has eased',
      'Avoid long unbroken periods of sitting',
      'Whichever of heat or cold feels more soothing to you is reasonable to use'
    ],
    redFlags: 'Numbness or weakness in the legs, or any loss of bladder or bowel control, is a medical emergency — seek care immediately rather than resting at home.'
  },
  {
    id: 'fatigue',
    title: 'General Fatigue',
    icon: '😴',
    tips: [
      'Prioritize a consistent sleep and wake time over sleeping in on weekends',
      'Check for overtraining if fatigue follows a hard training block',
      'Hydration and regular meals — skipped meals often show up as afternoon fatigue',
      'Short daylight exposure earlier in the day can help regulate energy'
    ],
    redFlags: 'Fatigue with chest pain, shortness of breath, or fainting needs emergency evaluation, not a rest day.'
  }
];

export default function HealthPage() {
  const [view, setView] = useState('conditions');
  const [expandedCategory, setExpandedCategory] = useState(null);

  return (
    <div className="health-page">
      <div className="health-header">
        <h1>Health &amp; Recovery</h1>
        <p className="health-subtitle">General wellness education — not a substitute for professional medical care</p>
      </div>

      <div className="disclaimer-banner">
        <strong>Not medical advice.</strong> OJAS is a fitness and wellness app, not a medical
        provider. The information on this page is general education only, is not a diagnosis or
        treatment plan, and does not replace care from a licensed doctor. If you're experiencing a
        medical emergency, call your local emergency number immediately.
      </div>

      <div className="view-toggle">
        <button className={`toggle-btn ${view === 'conditions' ? 'active' : ''}`} onClick={() => setView('conditions')}>
          Health Tracks
        </button>
        <button className={`toggle-btn ${view === 'recovery' ? 'active' : ''}`} onClick={() => setView('recovery')}>
          Recovery &amp; Self-Care
        </button>
      </div>

      {view === 'conditions' && (
        <section className="conditions-section">
          <p className="section-intro">
            General, lifestyle-level educational categories. None of this is a treatment plan —
            these conditions are diagnosed and managed by qualified healthcare providers.
          </p>
          <div className="condition-grid">
            {CONDITION_TRACKS.map((track, i) => (
              <div key={i} className="condition-card">
                <div className="condition-icon">{track.icon}</div>
                <h3>{track.title}</h3>
                <p>{track.text}</p>
                <div className="condition-tag">Consult your doctor for diagnosis &amp; treatment</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {view === 'recovery' && (
        <section className="recovery-section">
          <p className="section-intro">
            Well-established, low-risk general self-care basics for common everyday aches — organized
            by category, each with guidance on when to stop self-treating and see a doctor instead.
          </p>
          <div className="recovery-grid">
            {RECOVERY_CATEGORIES.map(category => {
              const isExpanded = expandedCategory === category.id;
              return (
                <div key={category.id} className="recovery-card">
                  <button
                    className="recovery-card-header"
                    onClick={() => setExpandedCategory(isExpanded ? null : category.id)}
                  >
                    <span className="recovery-icon">{category.icon}</span>
                    <span className="recovery-title">{category.title}</span>
                    <span className="recovery-toggle">{isExpanded ? '−' : '+'}</span>
                  </button>

                  {isExpanded && (
                    <div className="recovery-body">
                      <ul className="recovery-tips">
                        {category.tips.map((tip, i) => (
                          <li key={i}>{tip}</li>
                        ))}
                      </ul>
                      <div className="red-flag-box">
                        <strong>See a doctor instead if:</strong> {category.redFlags}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
