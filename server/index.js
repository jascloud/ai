import express from 'express';
import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { v4 as uuidv4 } from 'uuid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3001;

// Middleware
app.use(express.json());
app.use(express.static(join(__dirname, '../dist')));

// Initialize SQLite database
const db = new sqlite3.Database(join(__dirname, '../data/fitness.db'));

// Create tables
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      name TEXT,
      email TEXT UNIQUE,
      password TEXT,
      age INTEGER,
      height REAL,
      weight REAL,
      goal TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS workouts (
      id TEXT PRIMARY KEY,
      user_id TEXT,
      type TEXT,
      duration INTEGER,
      calories INTEGER,
      date DATE,
      notes TEXT,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS recipes (
      id TEXT PRIMARY KEY,
      name TEXT,
      category TEXT,
      cuisine TEXT,
      prep_time INTEGER,
      cook_time INTEGER,
      servings INTEGER,
      calories INTEGER,
      ingredients TEXT,
      instructions TEXT,
      image_url TEXT,
      cuisine_type TEXT
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS user_meals (
      id TEXT PRIMARY KEY,
      user_id TEXT,
      recipe_id TEXT,
      date DATE,
      meal_type TEXT,
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (recipe_id) REFERENCES recipes(id)
    )
  `);
});

// API Routes

// Get all recipes
app.get('/api/recipes', (req, res) => {
  db.all('SELECT * FROM recipes', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows.map(row => ({
        ...row,
        ingredients: JSON.parse(row.ingredients),
        instructions: JSON.parse(row.instructions)
      })));
    }
  });
});

// Get single recipe
app.get('/api/recipes/:id', (req, res) => {
  db.get('SELECT * FROM recipes WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Recipe not found' });
    } else {
      res.json({
        ...row,
        ingredients: JSON.parse(row.ingredients),
        instructions: JSON.parse(row.instructions)
      });
    }
  });
});

// Get user workouts
app.get('/api/workouts/:userId', (req, res) => {
  db.all('SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC', [req.params.userId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

// Add workout
app.post('/api/workouts', (req, res) => {
  const { userId, type, duration, calories, date, notes } = req.body;
  const id = uuidv4();

  db.run(
    'INSERT INTO workouts (id, user_id, type, duration, calories, date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [id, userId, type, duration, calories, date, notes],
    (err) => {
      if (err) {
        res.status(500).json({ error: err.message });
      } else {
        res.json({ id, userId, type, duration, calories, date, notes });
      }
    }
  );
});

// Get user profile
app.get('/api/users/:id', (req, res) => {
  db.get('SELECT * FROM users WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'User not found' });
    } else {
      res.json(row);
    }
  });
});

// Seed sample recipes
app.post('/api/seed-recipes', (req, res) => {
  const sampleRecipes = [
    {
      id: uuidv4(),
      name: 'Quinoa Khichdi',
      category: 'Lunch',
      cuisine: 'Indian',
      prep_time: 10,
      cook_time: 20,
      servings: 2,
      calories: 280,
      ingredients: JSON.stringify(['1 cup quinoa', '1 cup dal', '2 tbsp ghee', '1 tsp cumin', 'Salt to taste']),
      instructions: JSON.stringify(['Toast quinoa', 'Add dal and water', 'Cook for 20 minutes', 'Season with ghee and cumin']),
      cuisine_type: 'High Protein'
    },
    {
      id: uuidv4(),
      name: 'Masala Oats',
      category: 'Breakfast',
      cuisine: 'Indian Fusion',
      prep_time: 5,
      cook_time: 5,
      servings: 1,
      calories: 180,
      ingredients: JSON.stringify(['1 cup oats', '1 cup milk', '1 tbsp peanut butter', 'Turmeric', 'Chili powder']),
      instructions: JSON.stringify(['Cook oats with milk', 'Add peanut butter', 'Season with turmeric and chili']),
      cuisine_type: 'Quick Breakfast'
    },
    {
      id: uuidv4(),
      name: 'Spinach Dal Tadka',
      category: 'Lunch',
      cuisine: 'Indian',
      prep_time: 15,
      cook_time: 30,
      servings: 4,
      calories: 220,
      ingredients: JSON.stringify(['2 cups moong dal', '400g spinach', '3 tbsp oil', 'Ginger', 'Garlic', 'Cumin', 'Turmeric']),
      instructions: JSON.stringify(['Pressure cook dal', 'Saute spinach with ginger-garlic', 'Mix with dal', 'Add tadka with cumin']),
      cuisine_type: 'Vegetarian'
    },
    {
      id: uuidv4(),
      name: 'Grilled Chicken Tikka Bowl',
      category: 'Dinner',
      cuisine: 'Indian',
      prep_time: 20,
      cook_time: 15,
      servings: 2,
      calories: 380,
      ingredients: JSON.stringify(['500g chicken breast', 'Yogurt', 'Lemon juice', 'Ginger-garlic paste', 'Spices']),
      instructions: JSON.stringify(['Marinate chicken', 'Grill for 15 minutes', 'Serve with brown rice and vegetables']),
      cuisine_type: 'High Protein'
    }
  ];

  let completed = 0;
  sampleRecipes.forEach(recipe => {
    db.run(
      'INSERT OR IGNORE INTO recipes (id, name, category, cuisine, prep_time, cook_time, servings, calories, ingredients, instructions, cuisine_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [recipe.id, recipe.name, recipe.category, recipe.cuisine, recipe.prep_time, recipe.cook_time, recipe.servings, recipe.calories, recipe.ingredients, recipe.instructions, recipe.cuisine_type],
      () => {
        completed++;
        if (completed === sampleRecipes.length) {
          res.json({ message: 'Recipes seeded successfully' });
        }
      }
    );
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
