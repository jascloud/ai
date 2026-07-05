import React, { useState } from 'react';
import '../styles/Blog.css';

const ARTICLES = [
  {
    id: 'understanding-ojas',
    title: "Understanding Ojas: What 'Vital Energy' Actually Means in Practice",
    category: 'Philosophy',
    readTime: 5,
    icon: '🔥',
    gradient: 'grad-1',
    excerpt: "Our name comes from an Ayurvedic concept, but what does it mean for your Tuesday workout?",
    body: [
      "In Ayurveda, ojas is described as the refined essence of good digestion, good sleep, and consistent movement — not a mystical energy but the practical byproduct of doing the basics well, repeatedly.",
      "That's the idea we built the app around. A single great workout doesn't build ojas. Neither does one perfect meal. It's the boring, repeatable stuff — a plan you can actually follow on a Tuesday when you're tired — that compounds into something that feels like vitality.",
      "Practically, this means we optimized OJAS for adherence over intensity. A daily plan you'll actually do beats a perfect plan you'll abandon in two weeks."
    ]
  },
  {
    id: 'comfort-food-doesnt-break-plan',
    title: "Why Comfort Food Doesn't Have to Break Your Plan",
    category: 'Nutrition',
    readTime: 4,
    icon: '🍲',
    gradient: 'grad-2',
    excerpt: "Most diet apps ask you to give up the food you grew up with. Here's why that's the wrong trade.",
    body: [
      "The most common reason people abandon a nutrition plan isn't willpower — it's boredom, or a plan that has no room for the food they actually grew up eating.",
      "A grilled chicken breast and a bowl of dal tadka can hit the same calorie and protein targets. The macro math doesn't care which cuisine you use to get there.",
      "This is the entire premise behind building meal variety across cuisines rather than a single fixed template: sustainability comes from flexibility, not restriction."
    ]
  },
  {
    id: 'training-by-feel',
    title: 'The Case for Training by Feel, Not Just by Numbers',
    category: 'Training',
    readTime: 6,
    icon: '📊',
    gradient: 'grad-3',
    excerpt: 'Your program says 4 sets of 8. Your body says something else today. Who wins?',
    body: [
      "Programmed numbers are a starting point, not a contract. A written plan can't know that you slept four hours last night or that your shoulder feels off.",
      "Training by feel means using the planned sets and reps as a default, then adjusting load or volume based on how the first couple of reps actually feel that day — backing off on a rough day, pushing slightly on a good one.",
      "This isn't an excuse to skip hard days. It's a filter for telling the difference between 'this is uncomfortable because it's supposed to be' and 'this is a signal to back off.'"
    ]
  },
  {
    id: 'recovery-days-arent-wasted',
    title: "Recovery Days Aren't Wasted Days",
    category: 'Recovery',
    readTime: 4,
    icon: '💤',
    gradient: 'grad-4',
    excerpt: "The workout doesn't build you. The recovery after it does.",
    body: [
      "Training creates the stimulus; adaptation happens afterward, during rest. Skip the rest and you're left with the stimulus and none of the benefit.",
      "A good recovery day still has structure: light mobility work, a walk, deliberate sleep timing, and eating enough — not just eating 'clean.'",
      "If a rest day makes you anxious, that's worth noticing. Built-in recovery is what makes the next hard session possible."
    ]
  },
  {
    id: 'reading-hunger-signals',
    title: "A Beginner's Guide to Reading Your Own Hunger Signals",
    category: 'Nutrition',
    readTime: 5,
    icon: '🍽️',
    gradient: 'grad-1',
    excerpt: 'Calorie targets are a tool. Your actual hunger is the thing you have to live with daily.',
    body: [
      "Most of us have spent years overriding hunger cues with schedules, boredom, or stress — which makes 'just eat when you're hungry' harder advice than it sounds.",
      "A simpler starting point: before a meal, rate your hunger from 1 (not hungry at all) to 5 (uncomfortably hungry). Aim to eat around a 3, and stop around the same on the way back up.",
      "This isn't a replacement for tracking if tracking works for you — it's a second signal to check your plan against, especially on days the numbers and how you feel don't agree."
    ]
  },
  {
    id: 'four-week-strength-foundation',
    title: 'Building a 4-Week Strength Foundation From Scratch',
    category: 'Training',
    readTime: 7,
    icon: '🏋️',
    gradient: 'grad-2',
    excerpt: 'You don\'t need a complicated program for month one. You need consistency and a few compound lifts.',
    body: [
      "Week 1-2: full-body sessions three times a week — squat pattern, push, pull, and a hinge — at a weight you could do for 12-15 reps, but stop at 8-10. The goal is learning the movement, not fatigue.",
      "Week 3: add a small amount of load or one extra set per exercise. You should feel the difference from week 1 without it feeling like a different program.",
      "Week 4: repeat week 3's structure and pay attention to which exercises felt easiest — that's usually your body telling you where you're ready to progress fastest next month."
    ]
  },
  {
    id: 'traveling-without-losing-routine',
    title: 'Traveling Without Losing Your Routine',
    category: 'Lifestyle',
    readTime: 4,
    icon: '✈️',
    gradient: 'grad-3',
    excerpt: 'The goal on the road isn\'t your best training block. It\'s not losing the last one.',
    body: [
      "Travel breaks routines because it removes your usual environment, not because movement itself becomes impossible. A hotel room has enough floor space for a bodyweight circuit.",
      "Lower the bar on the road: 20 minutes of intentional movement most days beats an all-or-nothing standard that guarantees zero days once the gym isn't available.",
      "On the food side, look for the same patterns you'd build at home — a protein source, a vegetable, a carb — even if the cuisine on your plate has changed completely."
    ]
  },
  {
    id: 'yoga-nervous-system',
    title: "Yoga Isn't Just Flexibility — It's Nervous System Training",
    category: 'Wellness',
    readTime: 5,
    icon: '🧘',
    gradient: 'grad-4',
    excerpt: 'The stretching is real. The bigger effect might be happening somewhere else entirely.',
    body: [
      "It's easy to file yoga under 'flexibility work' and leave it there, but a lot of its effect comes from the breathing pattern layered on top of the poses.",
      "Slow, controlled exhales activate the parasympathetic nervous system — the part responsible for winding you down, not up. That's a different training effect than a HIIT session, and just as trainable.",
      "Pairing a hard training week with two or three short yoga sessions isn't a soft add-on. It's recovery infrastructure that makes the hard sessions sustainable."
    ]
  }
];

export default function BlogPage() {
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('All');

  const categories = ['All', ...Array.from(new Set(ARTICLES.map(a => a.category)))];
  const filteredArticles = categoryFilter === 'All' ? ARTICLES : ARTICLES.filter(a => a.category === categoryFilter);

  return (
    <div className="blog-page">
      <div className="blog-header">
        <h1>The OJAS Journal</h1>
        <p className="blog-subtitle">Training, nutrition, and recovery — written by the OJAS team</p>
      </div>

      <div className="filter-bar">
        {categories.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${categoryFilter === cat ? 'active' : ''}`}
            onClick={() => setCategoryFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="article-grid">
        {filteredArticles.map(article => (
          <div key={article.id} className="article-card" onClick={() => setSelectedArticle(article)}>
            <div className={`article-image ${article.gradient}`}>
              <span className="article-icon">{article.icon}</span>
            </div>
            <div className="article-info">
              <span className="article-category">{article.category} &middot; {article.readTime} min read</span>
              <h3>{article.title}</h3>
              <p className="article-excerpt">{article.excerpt}</p>
              <button className="btn btn-secondary btn-full">Read Article</button>
            </div>
          </div>
        ))}
      </div>

      {selectedArticle && (
        <div className="article-modal-overlay" onClick={() => setSelectedArticle(null)}>
          <div className="article-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedArticle(null)}>✕</button>
            <div className="modal-content">
              <span className="article-category">{selectedArticle.category} &middot; {selectedArticle.readTime} min read</span>
              <h2>{selectedArticle.title}</h2>
              {selectedArticle.body.map((para, i) => (
                <p key={i} className="article-paragraph">{para}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
