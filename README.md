# FitCook India - Fitness App & Healthy Recipes

A modern, India-focused fitness and recipe application combining personalized workout tracking with a curated collection of healthy Indian and fusion recipes.

## Features

### 🏋️ Fitness Tracking
- Log workouts with multiple exercise types (Yoga, Running, Cycling, Strength Training, Swimming, Walking, Pilates, Zumba)
- Automatic calorie calculation based on workout duration
- Track total calories burned, workouts completed, and time invested
- View workout history organized by date

### 🍛 Recipe Explorer
- Browse curated healthy Indian recipes
- Filter by category (High Protein, Vegetarian, Quick Breakfast, Low Calorie)
- Detailed recipe information with ingredients and instructions
- Calorie tracking and nutrition information
- Add recipes to meal plans

### 📊 Dashboard
- Quick statistics on today's activity
- Featured healthy recipes
- Wellness tips tailored to Indian fitness culture
- Personalized greeting and health summary

## Tech Stack

- **Frontend**: React + Vite
- **Styling**: Modern CSS with CSS custom properties (design tokens)
- **Backend**: Express.js
- **Database**: SQLite
- **Package Manager**: npm

## Getting Started

### Prerequisites
- Node.js (v16+)
- npm

### Installation

1. Clone the repository
```bash
git clone https://github.com/jascloud/ai.git
cd ai
```

2. Install dependencies
```bash
npm install
```

3. Seed sample data (optional)
```bash
curl -X POST http://localhost:3001/api/seed-recipes
```

### Development

Run both frontend and backend concurrently:
```bash
npm run dev
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001

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
│   │   ├── RecipeExplorer.jsx
│   │   └── WorkoutTracker.jsx
│   ├── styles/
│   │   ├── Dashboard.css
│   │   ├── RecipeExplorer.css
│   │   └── WorkoutTracker.css
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── server/
│   └── index.js
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

## Design System

### Color Palette
- **Saffron** (#FF8C42) - Primary action, energy
- **Deep Blue** (#1F3A5F) - Trust, health
- **Turmeric Gold** (#D4A574) - Secondary accent
- **Sage Green** (#6BA887) - Growth, wellness
- **Warm Off-white** (#FBF8F3) / **Deep Charcoal** (#1A1A1A) - Backgrounds

### Typography
- **Display**: Inter Bold for headings
- **Body**: Inter Regular for content
- **Mono**: IBM Plex Mono for data and numbers

## API Endpoints

### Recipes
- `GET /api/recipes` - Get all recipes
- `GET /api/recipes/:id` - Get single recipe

### Workouts
- `GET /api/workouts/:userId` - Get user's workouts
- `POST /api/workouts` - Add new workout

### Users
- `GET /api/users/:id` - Get user profile

### Admin
- `POST /api/seed-recipes` - Seed sample recipes

## India Market Features

- Workouts include traditional Indian practices (Yoga)
- Recipes feature authentic Indian ingredients and fusion options
- Cultural wellness tips (Ayurvedic eating, yoga benefits)
- Support for Indian health practices and measurements
- Warmth and celebration of Indian food culture

## Future Enhancements

- User authentication and personalization
- Integration with Indian payment gateways (Razorpay)
- AI-powered personalized meal plans
- Social features and community challenges
- Mobile app version
- Integration with wearables and fitness trackers
- Multi-language support (Hindi, regional languages)
- Offline mode

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
