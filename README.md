# OJAS — Train. Nourish. Rise.

A global, dark-themed fitness and nutrition platform: personalized subscription plans (including 1:1 coaching), a daily meal plan drawing from 1,000 recipes across the world, a 1,000-exercise library, workout tracking, and 1,000 member reviews.

> **Note:** OJAS is a demo/portfolio brand built for this project. The founding story, member counts, and testimonial personas in the app are fictional flavor text, not real company history or endorsements.

## Features

### 💳 Subscription Plans
- Basic (₹99), Pro (₹199), Premium (₹299), and Elite (₹999, 1:1 coach matching) monthly tiers
- Monthly/annual billing toggle with a 20% annual discount
- Discount code support (`FIT10`, `WELCOME20`)
- Community Telegram/WhatsApp channel access baked into plan features (see Footer for placeholder handles)
- "Meet Your Coaches" preview section with fictional coach personas (illustrated avatars, not real photos)

### 🌍 Universal Meals
- 1,000 recipes across 8 countries: India, Italy, Mexico, Japan, Thailand, Mediterranean, USA, China (33 hand-written signature dishes + procedurally generated variations)
- Auto-generated daily breakfast/lunch/dinner/snack plan, filterable by country
- Search + category filters (High Protein, Vegetarian, Quick Breakfast, Low Calorie, Balanced), with load-more pagination

### 🏋️ Exercise Library
- 1,000 exercises across Strength, Cardio, Yoga, Core, Flexibility, and HIIT (24 hand-written signature exercises + procedurally generated variations)
- Instructions, difficulty, equipment, and coaching tips for each
- Search + filters with load-more pagination
- "Log It" sends the exercise straight into the workout tracker

### 📈 Workout Tracker
- Log workouts and see totals for calories, sessions, and minutes
- History grouped by day

### ⭐ Reviews
- 1,000 generated member reviews with a rating distribution and star filters
- Paginated, load-more browsing

### 📊 Dashboard
- Today's stats, featured recipes, "Voices of OJAS" testimonials, and current plan status

## Tech Stack

- **Frontend**: React + Vite
- **Styling**: Dark-themed CSS with custom-property design tokens, Bebas Neue display type
- **Backend**: Express.js
- **Database**: SQLite (auto-seeds recipes, exercises, and reviews on first run)

## Getting Started

### Prerequisites
- Node.js (v16+)
- npm

### Installation

```bash
git clone https://github.com/jascloud/ai.git
cd ai
npm install
```

### Development

```bash
npm run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:3001

The database seeds itself automatically on first run — no manual setup needed.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── PlansPage.jsx
│   │   ├── Meals.jsx
│   │   ├── ExercisesPage.jsx
│   │   ├── WorkoutTracker.jsx
│   │   ├── ReviewsPage.jsx
│   │   ├── FeaturedVoices.jsx
│   │   └── Footer.jsx
│   ├── styles/
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── server/
│   └── index.js
├── docs/
│   ├── marketing-campaigns.md
│   └── social-media-content-calendar.md
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

## Design System

### Color Palette
- **Primary (Crimson)** `#FF4438` — energy, action
- **Garnet** `#3D0F16` — deep gradient accent
- **Gold** `#F5B841` — premium secondary accent
- **Success** `#3DDC84` — positive states
- **Near-black** `#0B0B0E` / **Surface** `#17171C` — dark ground

### Typography
- **Display**: Bebas Neue (uppercase, condensed) for headings
- **Body**: Inter for content
- **Mono**: IBM Plex Mono for stats and numbers

## API Endpoints

### Recipes / Meals
- `GET /api/recipes` — all recipes
- `GET /api/recipes/:id` — single recipe
- `GET /api/daily-plan/:userId?country=` — generated daily meal plan

### Exercises
- `GET /api/exercises` — all exercises

### Reviews
- `GET /api/reviews?page=&limit=&rating=` — paginated reviews with rating distribution

### Workouts
- `GET /api/workouts/:userId`
- `POST /api/workouts`

### Users / Subscriptions
- `GET /api/users/:id`
- `POST /api/subscribe` — `{ userId, planId, billingCycle }`

## Marketing Collateral

See `docs/marketing-campaigns.md` for campaign concepts and `docs/social-media-content-calendar.md` for ready-to-post Instagram/TikTok content — written for you to use on real accounts you create yourself.

## Future Enhancements

- Real user authentication
- Real payment gateway integration
- AI-powered personalized meal plans
- Wearables integration
- Multi-language support
- Offline mode

## License

MIT License - see LICENSE file for details
