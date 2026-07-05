import express from 'express';
import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { mkdirSync } from 'fs';
import { v4 as uuidv4 } from 'uuid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(express.json());
app.use(express.static(join(__dirname, '../dist')));

// Initialize SQLite database
const dataDir = join(__dirname, '../data');
mkdirSync(dataDir, { recursive: true });
const dbPath = process.env.DB_PATH || join(dataDir, 'fitness.db');
const db = new sqlite3.Database(dbPath);

const DEMO_USER_ID = 'demo-user-1';

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
      plan TEXT DEFAULT 'free',
      billing_cycle TEXT,
      plan_expiry DATE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Migrations for databases created before subscriptions existed
  db.run(`ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'`, () => {});
  db.run(`ALTER TABLE users ADD COLUMN billing_cycle TEXT`, () => {});
  db.run(`ALTER TABLE users ADD COLUMN plan_expiry DATE`, () => {});

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
      country TEXT,
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

  db.run(`ALTER TABLE recipes ADD COLUMN country TEXT DEFAULT 'India'`, () => {});

  db.run(`
    CREATE TABLE IF NOT EXISTS exercises (
      id TEXT PRIMARY KEY,
      name TEXT,
      category TEXT,
      muscle_group TEXT,
      difficulty TEXT,
      equipment TEXT,
      duration_min INTEGER,
      calories_per_min INTEGER,
      instructions TEXT,
      tips TEXT
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

  db.run(`
    CREATE TABLE IF NOT EXISTS reviews (
      id TEXT PRIMARY KEY,
      name TEXT,
      location TEXT,
      rating INTEGER,
      title TEXT,
      body TEXT,
      plan TEXT,
      verified INTEGER,
      created_at DATE
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS blogs (
      id TEXT PRIMARY KEY,
      title TEXT,
      slug TEXT UNIQUE,
      author TEXT,
      category TEXT,
      content TEXT,
      image_url TEXT,
      published_at DATE,
      read_time_min INTEGER
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS shop_products (
      id TEXT PRIMARY KEY,
      name TEXT,
      category TEXT,
      price REAL,
      currency TEXT DEFAULT 'INR',
      description TEXT,
      image_url TEXT,
      in_stock INTEGER DEFAULT 1,
      created_at DATE
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS nutrition_plans (
      id TEXT PRIMARY KEY,
      name TEXT,
      description TEXT,
      duration_days INTEGER,
      goal TEXT,
      image_url TEXT,
      daily_calories INTEGER,
      macros TEXT,
      created_at DATE
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS workout_programs (
      id TEXT PRIMARY KEY,
      name TEXT,
      description TEXT,
      difficulty TEXT,
      duration_weeks INTEGER,
      focus_area TEXT,
      image_url TEXT,
      free_tier INTEGER DEFAULT 1,
      created_at DATE
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS coaching_agents (
      id TEXT PRIMARY KEY,
      user_id TEXT,
      agent_type TEXT,
      expertise TEXT,
      last_interaction TEXT,
      created_at DATE,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Demo user so the app works out of the box
  db.run(
    `INSERT OR IGNORE INTO users (id, name, email, plan) VALUES (?, ?, ?, ?)`,
    [DEMO_USER_ID, 'Demo User', 'demo@ojas.fit', 'free']
  );

  // Chained so each seed's transaction fully completes before the next begins
  // (they share one connection, so overlapping BEGIN/COMMIT would conflict).
  seedRecipes(() => seedExercises(() => seedReviews(1000, () => seedBlogs(() => seedShop(() => seedNutrition(() => seedWorkouts(() => seedCoachingAgents())))))));
});

// ---------------------------------------------------------------------------
// Seed data
// ---------------------------------------------------------------------------

function seedRecipes(done) {
  done = done || (() => {});
  const recipes = [
    // India
    { id: 'india-breakfast-masala-oats', name: 'Masala Oats', category: 'Breakfast', cuisine: 'Indian Fusion', country: 'India', prep_time: 5, cook_time: 5, servings: 1, calories: 180, cuisine_type: 'Quick Breakfast',
      ingredients: ['1 cup oats', '1 cup milk', '1 tbsp peanut butter', 'Turmeric', 'Chili powder'],
      instructions: ['Cook oats with milk', 'Add peanut butter', 'Season with turmeric and chili'] },
    { id: 'india-lunch-quinoa-khichdi', name: 'Quinoa Khichdi', category: 'Lunch', cuisine: 'Indian', country: 'India', prep_time: 10, cook_time: 20, servings: 2, calories: 280, cuisine_type: 'High Protein',
      ingredients: ['1 cup quinoa', '1 cup dal', '2 tbsp ghee', '1 tsp cumin', 'Salt to taste'],
      instructions: ['Toast quinoa', 'Add dal and water', 'Cook for 20 minutes', 'Season with ghee and cumin'] },
    { id: 'india-lunch-spinach-dal-tadka', name: 'Spinach Dal Tadka', category: 'Lunch', cuisine: 'Indian', country: 'India', prep_time: 15, cook_time: 30, servings: 4, calories: 220, cuisine_type: 'Vegetarian',
      ingredients: ['2 cups moong dal', '400g spinach', '3 tbsp oil', 'Ginger', 'Garlic', 'Cumin', 'Turmeric'],
      instructions: ['Pressure cook dal', 'Saute spinach with ginger-garlic', 'Mix with dal', 'Add tadka with cumin'] },
    { id: 'india-dinner-chicken-tikka-bowl', name: 'Grilled Chicken Tikka Bowl', category: 'Dinner', cuisine: 'Indian', country: 'India', prep_time: 20, cook_time: 15, servings: 2, calories: 380, cuisine_type: 'High Protein',
      ingredients: ['500g chicken breast', 'Yogurt', 'Lemon juice', 'Ginger-garlic paste', 'Spices'],
      instructions: ['Marinate chicken', 'Grill for 15 minutes', 'Serve with brown rice and vegetables'] },
    { id: 'india-snack-sprouted-chaat', name: 'Sprouted Moong Chaat', category: 'Snack', cuisine: 'Indian', country: 'India', prep_time: 10, cook_time: 0, servings: 2, calories: 150, cuisine_type: 'Low Calorie',
      ingredients: ['2 cups sprouted moong', 'Onion', 'Tomato', 'Lemon juice', 'Chaat masala', 'Coriander'],
      instructions: ['Mix sprouts with chopped vegetables', 'Add lemon juice and chaat masala', 'Garnish with coriander'] },

    // Italy
    { id: 'italy-breakfast-ricotta-toast', name: 'Ricotta & Berry Toast', category: 'Breakfast', cuisine: 'Italian', country: 'Italy', prep_time: 5, cook_time: 5, servings: 1, calories: 240, cuisine_type: 'Quick Breakfast',
      ingredients: ['2 slices whole grain bread', '1/2 cup ricotta', 'Mixed berries', 'Honey', 'Mint'],
      instructions: ['Toast the bread', 'Spread ricotta generously', 'Top with berries and a drizzle of honey'] },
    { id: 'italy-lunch-caprese-farro-salad', name: 'Caprese Farro Salad', category: 'Lunch', cuisine: 'Italian', country: 'Italy', prep_time: 15, cook_time: 20, servings: 2, calories: 320, cuisine_type: 'Vegetarian',
      ingredients: ['1 cup farro', 'Cherry tomatoes', 'Fresh mozzarella', 'Basil', 'Olive oil', 'Balsamic glaze'],
      instructions: ['Cook farro until tender', 'Toss with tomatoes, mozzarella and basil', 'Finish with olive oil and balsamic'] },
    { id: 'italy-dinner-zucchini-bolognese', name: 'Zucchini Turkey Bolognese', category: 'Dinner', cuisine: 'Italian', country: 'Italy', prep_time: 15, cook_time: 30, servings: 3, calories: 390, cuisine_type: 'High Protein',
      ingredients: ['Zucchini noodles', '400g ground turkey', 'Tomato passata', 'Garlic', 'Basil', 'Parmesan'],
      instructions: ['Brown the turkey with garlic', 'Simmer with passata for 20 minutes', 'Serve over zucchini noodles with parmesan'] },
    { id: 'italy-snack-bruschetta', name: 'Bruschetta al Pomodoro', category: 'Snack', cuisine: 'Italian', country: 'Italy', prep_time: 10, cook_time: 5, servings: 2, calories: 140, cuisine_type: 'Low Calorie',
      ingredients: ['Baguette slices', 'Tomatoes', 'Garlic', 'Basil', 'Olive oil'],
      instructions: ['Toast baguette slices', 'Rub with garlic', 'Top with diced tomato and basil'] },

    // Mexico
    { id: 'mexico-breakfast-huevos-rancheros', name: 'Huevos Rancheros Bowl', category: 'Breakfast', cuisine: 'Mexican', country: 'Mexico', prep_time: 10, cook_time: 10, servings: 1, calories: 300, cuisine_type: 'High Protein',
      ingredients: ['2 eggs', 'Black beans', 'Salsa', 'Corn tortilla', 'Avocado', 'Cotija cheese'],
      instructions: ['Fry the eggs', 'Warm the beans and salsa', 'Layer over a tortilla and top with avocado'] },
    { id: 'mexico-lunch-black-bean-corn-salad', name: 'Black Bean & Corn Salad Bowl', category: 'Lunch', cuisine: 'Mexican', country: 'Mexico', prep_time: 15, cook_time: 0, servings: 2, calories: 340, cuisine_type: 'Vegetarian',
      ingredients: ['Black beans', 'Corn', 'Bell pepper', 'Lime', 'Cilantro', 'Cumin'],
      instructions: ['Combine beans, corn and diced pepper', 'Dress with lime juice and cumin', 'Toss with fresh cilantro'] },
    { id: 'mexico-dinner-chicken-fajita-bowl', name: 'Grilled Chicken Fajita Bowl', category: 'Dinner', cuisine: 'Mexican', country: 'Mexico', prep_time: 15, cook_time: 20, servings: 2, calories: 400, cuisine_type: 'High Protein',
      ingredients: ['Chicken breast', 'Bell peppers', 'Onion', 'Fajita spice mix', 'Brown rice', 'Lime'],
      instructions: ['Marinate and grill chicken', 'Char peppers and onion', 'Serve over rice with lime'] },
    { id: 'mexico-snack-guacamole-jicama', name: 'Guacamole with Jicama Sticks', category: 'Snack', cuisine: 'Mexican', country: 'Mexico', prep_time: 10, cook_time: 0, servings: 2, calories: 160, cuisine_type: 'Low Calorie',
      ingredients: ['2 avocados', 'Lime', 'Red onion', 'Cilantro', 'Jicama'],
      instructions: ['Mash avocado with lime juice', 'Fold in onion and cilantro', 'Serve with sliced jicama'] },

    // Japan
    { id: 'japan-breakfast-tamagoyaki-rice', name: 'Tamagoyaki with Rice', category: 'Breakfast', cuisine: 'Japanese', country: 'Japan', prep_time: 10, cook_time: 10, servings: 1, calories: 280, cuisine_type: 'High Protein',
      ingredients: ['3 eggs', 'Soy sauce', 'Mirin', 'Steamed rice', 'Nori'],
      instructions: ['Whisk eggs with soy sauce and mirin', 'Cook in thin layers, rolling as you go', 'Slice and serve over rice with nori'] },
    { id: 'japan-lunch-salmon-onigiri-bento', name: 'Salmon Onigiri Bento', category: 'Lunch', cuisine: 'Japanese', country: 'Japan', prep_time: 20, cook_time: 15, servings: 2, calories: 350, cuisine_type: 'High Protein',
      ingredients: ['Salmon fillet', 'Sushi rice', 'Nori', 'Sesame seeds', 'Pickled ginger'],
      instructions: ['Grill and flake the salmon', 'Mix through the rice', 'Shape into onigiri and wrap with nori'] },
    { id: 'japan-dinner-teriyaki-tofu-stirfry', name: 'Teriyaki Tofu Stir-fry', category: 'Dinner', cuisine: 'Japanese', country: 'Japan', prep_time: 15, cook_time: 15, servings: 2, calories: 360, cuisine_type: 'Vegetarian',
      ingredients: ['Firm tofu', 'Broccoli', 'Carrots', 'Teriyaki sauce', 'Sesame oil', 'Brown rice'],
      instructions: ['Pan-sear tofu until golden', 'Stir-fry vegetables', 'Toss everything in teriyaki sauce and serve over rice'] },
    { id: 'japan-snack-edamame', name: 'Edamame with Sea Salt', category: 'Snack', cuisine: 'Japanese', country: 'Japan', prep_time: 5, cook_time: 5, servings: 2, calories: 120, cuisine_type: 'Low Calorie',
      ingredients: ['2 cups edamame pods', 'Sea salt'],
      instructions: ['Steam or boil edamame for 5 minutes', 'Toss with sea salt while hot'] },

    // Thailand
    { id: 'thailand-breakfast-basil-egg-rice', name: 'Thai Basil Egg Rice', category: 'Breakfast', cuisine: 'Thai', country: 'Thailand', prep_time: 10, cook_time: 10, servings: 1, calories: 310, cuisine_type: 'High Protein',
      ingredients: ['Jasmine rice', '2 eggs', 'Thai basil', 'Garlic', 'Chili', 'Fish sauce'],
      instructions: ['Fry garlic and chili', 'Scramble in the eggs', 'Toss with rice, basil and fish sauce'] },
    { id: 'thailand-lunch-som-tam-shrimp', name: 'Som Tam Papaya Salad with Grilled Shrimp', category: 'Lunch', cuisine: 'Thai', country: 'Thailand', prep_time: 20, cook_time: 10, servings: 2, calories: 280, cuisine_type: 'Low Calorie',
      ingredients: ['Green papaya', 'Grilled shrimp', 'Lime', 'Peanuts', 'Chili', 'Fish sauce'],
      instructions: ['Shred the green papaya', 'Pound with lime, chili and fish sauce', 'Top with grilled shrimp and peanuts'] },
    { id: 'thailand-dinner-green-curry-chicken', name: 'Green Curry Chicken with Brown Rice', category: 'Dinner', cuisine: 'Thai', country: 'Thailand', prep_time: 15, cook_time: 25, servings: 3, calories: 420, cuisine_type: 'High Protein',
      ingredients: ['Chicken thigh', 'Green curry paste', 'Coconut milk', 'Thai eggplant', 'Basil', 'Brown rice'],
      instructions: ['Fry curry paste until fragrant', 'Add coconut milk and chicken', 'Simmer with eggplant and basil, serve over rice'] },
    { id: 'thailand-snack-mango-sticky-rice', name: 'Mango Sticky Rice Bites', category: 'Snack', cuisine: 'Thai', country: 'Thailand', prep_time: 15, cook_time: 20, servings: 4, calories: 180, cuisine_type: 'Low Calorie',
      ingredients: ['Sticky rice', 'Mango', 'Coconut milk', 'Sugar', 'Sesame seeds'],
      instructions: ['Steam sticky rice', 'Mix with warm coconut milk', 'Shape into bites and top with mango'] },

    // Mediterranean (Greece)
    { id: 'mediterranean-breakfast-yogurt-parfait', name: 'Greek Yogurt Parfait with Honey & Walnuts', category: 'Breakfast', cuisine: 'Greek', country: 'Mediterranean', prep_time: 5, cook_time: 0, servings: 1, calories: 260, cuisine_type: 'Quick Breakfast',
      ingredients: ['Greek yogurt', 'Honey', 'Walnuts', 'Figs'],
      instructions: ['Layer yogurt with honey', 'Top with crushed walnuts and sliced figs'] },
    { id: 'mediterranean-lunch-chickpea-salad', name: 'Mediterranean Chickpea Salad', category: 'Lunch', cuisine: 'Greek', country: 'Mediterranean', prep_time: 15, cook_time: 0, servings: 2, calories: 330, cuisine_type: 'Vegetarian',
      ingredients: ['Chickpeas', 'Cucumber', 'Feta', 'Olives', 'Red onion', 'Olive oil', 'Lemon'],
      instructions: ['Combine chickpeas with chopped vegetables', 'Add crumbled feta and olives', 'Dress with olive oil and lemon'] },
    { id: 'mediterranean-dinner-grilled-fish', name: 'Grilled Fish with Lemon & Herbs', category: 'Dinner', cuisine: 'Greek', country: 'Mediterranean', prep_time: 10, cook_time: 15, servings: 2, calories: 380, cuisine_type: 'High Protein',
      ingredients: ['White fish fillets', 'Lemon', 'Oregano', 'Olive oil', 'Garlic', 'Roasted vegetables'],
      instructions: ['Marinate fish in lemon, oregano and olive oil', 'Grill until flaky', 'Serve with roasted vegetables'] },
    { id: 'mediterranean-snack-hummus-cucumber', name: 'Hummus with Cucumber', category: 'Snack', cuisine: 'Greek', country: 'Mediterranean', prep_time: 5, cook_time: 0, servings: 2, calories: 140, cuisine_type: 'Low Calorie',
      ingredients: ['Hummus', 'Cucumber', 'Paprika', 'Olive oil'],
      instructions: ['Spread hummus in a bowl', 'Drizzle with olive oil and paprika', 'Serve with cucumber sticks'] },

    // USA
    { id: 'usa-breakfast-protein-pancakes', name: 'Protein Pancakes with Berries', category: 'Breakfast', cuisine: 'American', country: 'USA', prep_time: 10, cook_time: 10, servings: 2, calories: 320, cuisine_type: 'High Protein',
      ingredients: ['Protein powder', 'Oats', 'Banana', 'Eggs', 'Mixed berries', 'Maple syrup'],
      instructions: ['Blend batter ingredients', 'Cook pancakes on a hot griddle', 'Top with berries and a drizzle of syrup'] },
    { id: 'usa-lunch-turkey-avocado-wrap', name: 'Turkey & Avocado Power Wrap', category: 'Lunch', cuisine: 'American', country: 'USA', prep_time: 10, cook_time: 0, servings: 1, calories: 380, cuisine_type: 'High Protein',
      ingredients: ['Whole wheat wrap', 'Sliced turkey', 'Avocado', 'Spinach', 'Mustard'],
      instructions: ['Lay turkey and avocado on the wrap', 'Add spinach and mustard', 'Roll tightly and slice'] },
    { id: 'usa-dinner-steak-sweet-potato', name: 'Grilled Steak with Sweet Potato Mash', category: 'Dinner', cuisine: 'American', country: 'USA', prep_time: 10, cook_time: 25, servings: 2, calories: 450, cuisine_type: 'High Protein',
      ingredients: ['Lean steak', 'Sweet potato', 'Rosemary', 'Garlic', 'Green beans'],
      instructions: ['Grill steak to preference', 'Mash boiled sweet potato with rosemary', 'Serve with steamed green beans'] },
    { id: 'usa-snack-trail-mix', name: 'Trail Mix Energy Bites', category: 'Snack', cuisine: 'American', country: 'USA', prep_time: 10, cook_time: 0, servings: 4, calories: 170, cuisine_type: 'Low Calorie',
      ingredients: ['Oats', 'Almonds', 'Dried cranberries', 'Honey', 'Dark chocolate chips'],
      instructions: ['Mix all ingredients together', 'Roll into bite-sized balls', 'Chill for 30 minutes before serving'] },

    // China
    { id: 'china-breakfast-congee', name: 'Light Congee with Ginger & Scallion', category: 'Breakfast', cuisine: 'Chinese', country: 'China', prep_time: 5, cook_time: 30, servings: 2, calories: 250, cuisine_type: 'Quick Breakfast',
      ingredients: ['Rice', 'Ginger', 'Scallion', 'Chicken stock', 'Soy sauce'],
      instructions: ['Simmer rice in stock until creamy', 'Stir in ginger', 'Top with scallion and a splash of soy sauce'] },
    { id: 'china-lunch-kung-pao-chicken', name: 'Kung Pao Chicken with Brown Rice', category: 'Lunch', cuisine: 'Chinese', country: 'China', prep_time: 15, cook_time: 15, servings: 2, calories: 380, cuisine_type: 'High Protein',
      ingredients: ['Chicken breast', 'Peanuts', 'Dried chili', 'Bell pepper', 'Soy sauce', 'Brown rice'],
      instructions: ['Stir-fry chicken until cooked', 'Add peppers, chili and peanuts', 'Toss in sauce and serve over rice'] },
    { id: 'china-dinner-steamed-fish', name: 'Steamed Fish with Ginger & Scallion', category: 'Dinner', cuisine: 'Chinese', country: 'China', prep_time: 10, cook_time: 15, servings: 2, calories: 340, cuisine_type: 'High Protein',
      ingredients: ['White fish', 'Ginger', 'Scallion', 'Soy sauce', 'Sesame oil'],
      instructions: ['Steam fish with ginger for 12 minutes', 'Top with scallion', 'Finish with hot sesame oil and soy sauce'] },
    { id: 'china-snack-edamame-dumplings', name: 'Steamed Edamame Dumplings', category: 'Snack', cuisine: 'Chinese', country: 'China', prep_time: 20, cook_time: 10, servings: 3, calories: 160, cuisine_type: 'Low Calorie',
      ingredients: ['Dumpling wrappers', 'Edamame', 'Ginger', 'Sesame oil', 'Soy sauce'],
      instructions: ['Mash edamame with ginger and sesame oil', 'Fill and fold the wrappers', 'Steam for 10 minutes'] }
  ];

  const allRecipes = recipes.concat(generateBulkRecipes(1000 - recipes.length));

  db.get('SELECT COUNT(*) AS count FROM recipes', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    db.run('BEGIN TRANSACTION');
    allRecipes.forEach(recipe => {
      db.run(
        'INSERT OR IGNORE INTO recipes (id, name, category, cuisine, country, prep_time, cook_time, servings, calories, ingredients, instructions, cuisine_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [recipe.id, recipe.name, recipe.category, recipe.cuisine, recipe.country, recipe.prep_time, recipe.cook_time, recipe.servings, recipe.calories, JSON.stringify(recipe.ingredients), JSON.stringify(recipe.instructions), recipe.cuisine_type]
      );
    });
    db.run('COMMIT', done);
  });
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Procedurally generate additional recipes to reach catalog scale, on top of the
// hand-written signature dishes above. Combinatorial templates, not hand-authored.
function generateBulkRecipes(count) {
  const countryMeta = {
    India: { cuisine: 'Indian', flavors: ['turmeric', 'cumin', 'garam masala', 'coriander'] },
    Italy: { cuisine: 'Italian', flavors: ['basil', 'oregano', 'parmesan', 'garlic'] },
    Mexico: { cuisine: 'Mexican', flavors: ['lime', 'cilantro', 'chili', 'cumin'] },
    Japan: { cuisine: 'Japanese', flavors: ['soy sauce', 'miso', 'sesame', 'ginger'] },
    Thailand: { cuisine: 'Thai', flavors: ['lemongrass', 'chili', 'fish sauce', 'basil'] },
    Mediterranean: { cuisine: 'Greek', flavors: ['olive oil', 'oregano', 'feta', 'lemon'] },
    USA: { cuisine: 'American', flavors: ['smoked paprika', 'black pepper', 'maple', 'rosemary'] },
    China: { cuisine: 'Chinese', flavors: ['ginger', 'scallion', 'soy sauce', 'five spice'] }
  };
  const countries = Object.keys(countryMeta);
  const categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const proteins = ['chicken', 'paneer', 'tofu', 'salmon', 'lentils', 'eggs', 'shrimp', 'turkey', 'chickpeas', 'mushroom', 'black beans', 'cottage cheese'];
  const methods = ['Grilled', 'Roasted', 'Steamed', 'Stir-Fried', 'Baked', 'Sauteed', 'Slow-Cooked', 'Pan-Seared', 'Poached', 'Charred'];
  const sides = ['brown rice', 'quinoa', 'whole wheat roti', 'rice noodles', 'couscous', 'sweet potato mash', 'buckwheat', 'barley', 'cauliflower rice', 'soba noodles'];
  const dietTags = ['High Protein', 'Vegetarian', 'Quick Breakfast', 'Low Calorie', 'Balanced'];
  const calorieBase = { Breakfast: 260, Lunch: 380, Dinner: 430, Snack: 150 };

  const rng = makeRng(2024);
  const recipes = [];

  for (let i = 0; i < count; i++) {
    const country = pick(rng, countries);
    const meta = countryMeta[country];
    const category = pick(rng, categories);
    const protein = pick(rng, proteins);
    const method = pick(rng, methods);
    const side = pick(rng, sides);
    const flavor1 = pick(rng, meta.flavors);
    const flavor2 = pick(rng, meta.flavors);
    const dietTag = pick(rng, dietTags);

    const calories = Math.round(calorieBase[category] + (rng() - 0.5) * 120);
    const prepTime = 5 + Math.floor(rng() * 15);
    const cookTime = 10 + Math.floor(rng() * 25);
    const servings = 1 + Math.floor(rng() * 4);

    recipes.push({
      id: `gen-recipe-${i}`,
      name: `${method} ${capitalize(protein)} with ${capitalize(side)}`,
      category,
      cuisine: meta.cuisine,
      country,
      prep_time: prepTime,
      cook_time: cookTime,
      servings,
      calories,
      cuisine_type: dietTag,
      ingredients: [capitalize(protein), capitalize(side), capitalize(flavor1), capitalize(flavor2), 'Salt to taste'],
      instructions: [
        `Prepare the ${side}`,
        `${method} the ${protein} with ${flavor1} and ${flavor2}`,
        'Combine and serve warm'
      ]
    });
  }

  return recipes;
}

function seedExercises(done) {
  done = done || (() => {});
  const exercises = [
    // Strength
    { id: 'ex-pushups', name: 'Push-ups', category: 'Strength', muscle_group: 'Chest, Triceps, Shoulders', difficulty: 'Beginner', equipment: 'None', duration_min: 10, calories_per_min: 8,
      instructions: ['Start in a plank with hands under shoulders', 'Lower chest to the floor keeping core tight', 'Push back up to full extension', 'Repeat for 3 sets of 12-15'], tips: 'Keep your body in a straight line from head to heels.' },
    { id: 'ex-dumbbell-squats', name: 'Dumbbell Squats', category: 'Strength', muscle_group: 'Legs, Glutes', difficulty: 'Intermediate', equipment: 'Dumbbells', duration_min: 15, calories_per_min: 9,
      instructions: ['Hold a dumbbell in each hand at your sides', 'Lower into a squat keeping knees over toes', 'Drive through your heels to stand', 'Repeat for 4 sets of 10-12'], tips: 'Keep your chest up throughout the movement.' },
    { id: 'ex-bent-over-rows', name: 'Bent-over Rows', category: 'Strength', muscle_group: 'Back, Biceps', difficulty: 'Intermediate', equipment: 'Dumbbells', duration_min: 15, calories_per_min: 8,
      instructions: ['Hinge at the hips holding dumbbells', 'Pull elbows back squeezing shoulder blades', 'Lower with control', 'Repeat for 3 sets of 12'], tips: 'Keep a flat back to protect your spine.' },
    { id: 'ex-deadlifts', name: 'Deadlifts', category: 'Strength', muscle_group: 'Full Body, Posterior Chain', difficulty: 'Advanced', equipment: 'Barbell', duration_min: 20, calories_per_min: 10,
      instructions: ['Stand with feet hip-width, bar over midfoot', 'Hinge down and grip the bar', 'Drive through your heels to stand tall', 'Repeat for 4 sets of 6-8'], tips: 'Keep the bar close to your shins throughout the lift.' },

    // Cardio
    { id: 'ex-jumping-jacks', name: 'Jumping Jacks', category: 'Cardio', muscle_group: 'Full Body', difficulty: 'Beginner', equipment: 'None', duration_min: 10, calories_per_min: 10,
      instructions: ['Start standing with feet together', 'Jump feet out while raising arms overhead', 'Jump back to start', 'Continue for 3 sets of 1 minute'], tips: 'Land softly on the balls of your feet.' },
    { id: 'ex-running-intervals', name: 'Running Intervals', category: 'Cardio', muscle_group: 'Legs, Cardiovascular', difficulty: 'Intermediate', equipment: 'None', duration_min: 25, calories_per_min: 12,
      instructions: ['Warm up with 5 minutes easy jogging', 'Sprint for 30 seconds, walk for 90 seconds', 'Repeat for 8 rounds', 'Cool down with a light jog'], tips: 'Adjust sprint intensity to your fitness level.' },
    { id: 'ex-jump-rope', name: 'Jump Rope', category: 'Cardio', muscle_group: 'Full Body, Cardiovascular', difficulty: 'Intermediate', equipment: 'Skipping Rope', duration_min: 15, calories_per_min: 13,
      instructions: ['Hold the rope handles at hip height', 'Jump just high enough to clear the rope', 'Keep a steady rhythm', 'Continue for 3 sets of 3 minutes'], tips: 'Keep elbows close to your body for control.' },
    { id: 'ex-stair-climbing', name: 'Stair Climbing', category: 'Cardio', muscle_group: 'Legs, Cardiovascular', difficulty: 'Beginner', equipment: 'None', duration_min: 20, calories_per_min: 9,
      instructions: ['Climb stairs at a brisk, steady pace', 'Use the handrail only for balance', 'Walk down to recover', 'Repeat for 20 minutes'], tips: 'Land on the whole foot, not just your toes.' },

    // Yoga
    { id: 'ex-surya-namaskar', name: 'Surya Namaskar (Sun Salutation)', category: 'Yoga', muscle_group: 'Full Body', difficulty: 'Beginner', equipment: 'Mat', duration_min: 15, calories_per_min: 6,
      instructions: ['Flow through the 12-pose sun salutation sequence', 'Sync breath with each movement', 'Complete 6-8 rounds'], tips: 'Move slowly and focus on breath, not speed.' },
    { id: 'ex-downward-dog-flow', name: 'Downward Dog Flow', category: 'Yoga', muscle_group: 'Shoulders, Hamstrings', difficulty: 'Beginner', equipment: 'Mat', duration_min: 10, calories_per_min: 4,
      instructions: ['Start on hands and knees', 'Lift hips up and back into an inverted V', 'Pedal heels to stretch calves', 'Hold and breathe for 5-8 breaths, repeat 3 times'], tips: 'Keep a slight bend in the knees if hamstrings are tight.' },
    { id: 'ex-warrior-sequence', name: 'Warrior Sequence', category: 'Yoga', muscle_group: 'Legs, Balance', difficulty: 'Intermediate', equipment: 'Mat', duration_min: 15, calories_per_min: 5,
      instructions: ['Move through Warrior I, II and III on each side', 'Hold each pose for 5 breaths', 'Focus on a steady gaze for balance'], tips: 'Engage your core to support each transition.' },
    { id: 'ex-yin-yoga-stretch', name: 'Yin Yoga Stretch', category: 'Yoga', muscle_group: 'Full Body, Flexibility', difficulty: 'Beginner', equipment: 'Mat', duration_min: 20, calories_per_min: 3,
      instructions: ['Hold each passive stretch for 2-3 minutes', 'Relax muscles and let gravity deepen the stretch', 'Breathe slowly throughout'], tips: 'This is a cool-down practice — never force a stretch.' },

    // Core
    { id: 'ex-plank-hold', name: 'Plank Hold', category: 'Core', muscle_group: 'Abs, Core', difficulty: 'Beginner', equipment: 'None', duration_min: 10, calories_per_min: 6,
      instructions: ['Rest on forearms and toes, body in a straight line', 'Brace your core and squeeze glutes', 'Hold for 30-60 seconds', 'Repeat for 4 sets'], tips: 'Do not let your hips sag or pike up.' },
    { id: 'ex-russian-twists', name: 'Russian Twists', category: 'Core', muscle_group: 'Obliques', difficulty: 'Intermediate', equipment: 'None or Dumbbell', duration_min: 10, calories_per_min: 7,
      instructions: ['Sit with knees bent, lean back slightly', 'Rotate torso side to side, tapping the floor', 'Keep chest lifted throughout', 'Repeat for 3 sets of 20 twists'], tips: 'Move slower to increase difficulty rather than rushing.' },
    { id: 'ex-bicycle-crunches', name: 'Bicycle Crunches', category: 'Core', muscle_group: 'Abs', difficulty: 'Beginner', equipment: 'None', duration_min: 10, calories_per_min: 7,
      instructions: ['Lie on your back, hands behind head', 'Bring opposite elbow to opposite knee', 'Alternate sides in a pedaling motion', 'Repeat for 3 sets of 20'], tips: 'Avoid pulling on your neck — let your abs do the work.' },
    { id: 'ex-hanging-leg-raises', name: 'Hanging Leg Raises', category: 'Core', muscle_group: 'Lower Abs', difficulty: 'Advanced', equipment: 'Pull-up Bar', duration_min: 12, calories_per_min: 8,
      instructions: ['Hang from a pull-up bar with straight arms', 'Raise legs to hip height or higher', 'Lower with control', 'Repeat for 4 sets of 10'], tips: 'Avoid swinging — control the movement both ways.' },

    // Flexibility
    { id: 'ex-hamstring-stretch', name: 'Hamstring Stretch Series', category: 'Flexibility', muscle_group: 'Legs', difficulty: 'Beginner', equipment: 'Mat', duration_min: 10, calories_per_min: 3,
      instructions: ['Sit with one leg extended, other bent inward', 'Hinge forward from the hips over the extended leg', 'Hold for 30-45 seconds each side'], tips: 'Keep your back long instead of rounding forward.' },
    { id: 'ex-hip-opener-flow', name: 'Hip Opener Flow', category: 'Flexibility', muscle_group: 'Hips', difficulty: 'Beginner', equipment: 'Mat', duration_min: 12, calories_per_min: 3,
      instructions: ['Move through pigeon pose and butterfly stretch', 'Hold each position for 45-60 seconds', 'Breathe deeply to release tension'], tips: 'Use a cushion under the hip for extra support in pigeon pose.' },
    { id: 'ex-shoulder-neck-mobility', name: 'Shoulder & Neck Mobility', category: 'Flexibility', muscle_group: 'Upper Body', difficulty: 'Beginner', equipment: 'None', duration_min: 8, calories_per_min: 2,
      instructions: ['Roll shoulders forward and backward 10 times', 'Gently tilt head side to side and forward', 'Cross-body arm stretches for each side'], tips: 'Great as a desk break during the workday.' },
    { id: 'ex-full-body-cooldown', name: 'Full Body Cool-down Stretch', category: 'Flexibility', muscle_group: 'Full Body', difficulty: 'Beginner', equipment: 'Mat', duration_min: 15, calories_per_min: 3,
      instructions: ['Move through a full-body static stretch sequence', 'Hold each stretch for 30 seconds', 'Finish with deep, slow breathing'], tips: 'Best done immediately after a workout while muscles are warm.' },

    // HIIT
    { id: 'ex-burpee-circuit', name: 'Burpee Circuit', category: 'HIIT', muscle_group: 'Full Body', difficulty: 'Advanced', equipment: 'None', duration_min: 15, calories_per_min: 14,
      instructions: ['Drop into a squat and kick feet back to plank', 'Perform a push-up', 'Jump feet back in and leap up', 'Repeat for 30 seconds on, 30 seconds off, 8 rounds'], tips: 'Scale by removing the push-up or the jump if needed.' },
    { id: 'ex-mountain-climbers-tabata', name: 'Mountain Climbers Tabata', category: 'HIIT', muscle_group: 'Core, Cardiovascular', difficulty: 'Intermediate', equipment: 'None', duration_min: 12, calories_per_min: 12,
      instructions: ['Start in a plank position', 'Drive knees rapidly toward your chest, alternating', 'Work 20 seconds, rest 10 seconds', 'Repeat for 8 rounds'], tips: 'Keep hips low and steady to protect your lower back.' },
    { id: 'ex-kettlebell-swings', name: 'Kettlebell Swings', category: 'HIIT', muscle_group: 'Full Body, Posterior Chain', difficulty: 'Intermediate', equipment: 'Kettlebell', duration_min: 15, calories_per_min: 13,
      instructions: ['Hinge at the hips holding the kettlebell', 'Snap hips forward to swing it to shoulder height', 'Let it swing back between your legs', 'Repeat for 5 sets of 15'], tips: 'Power comes from your hips, not your arms.' },
    { id: 'ex-box-jumps', name: 'Box Jumps', category: 'HIIT', muscle_group: 'Legs, Power', difficulty: 'Advanced', equipment: 'Box or Step', duration_min: 12, calories_per_min: 12,
      instructions: ['Stand facing a sturdy box', 'Swing arms and jump onto the box, landing softly', 'Step back down and reset', 'Repeat for 5 sets of 8'], tips: 'Choose a box height you can land on safely with soft knees.' }
  ];

  const allExercises = exercises.concat(generateBulkExercises(1000 - exercises.length));

  db.get('SELECT COUNT(*) AS count FROM exercises', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    db.run('BEGIN TRANSACTION');
    allExercises.forEach(ex => {
      db.run(
        'INSERT OR IGNORE INTO exercises (id, name, category, muscle_group, difficulty, equipment, duration_min, calories_per_min, instructions, tips) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [ex.id, ex.name, ex.category, ex.muscle_group, ex.difficulty, ex.equipment, ex.duration_min, ex.calories_per_min, JSON.stringify(ex.instructions), ex.tips]
      );
    });
    db.run('COMMIT', done);
  });
}

// Procedurally generate additional exercises to reach library scale, on top of the
// hand-written signature exercises above. Combinatorial templates, not hand-authored.
function generateBulkExercises(count) {
  const categoryMeta = {
    Strength: { muscleGroups: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Glutes'], equipment: ['Dumbbells', 'Barbell', 'Resistance Band', 'Kettlebell', 'Bodyweight'], baseCal: 8 },
    Cardio: { muscleGroups: ['Full Body', 'Legs', 'Cardiovascular'], equipment: ['None', 'Jump Rope', 'Treadmill', 'Bike'], baseCal: 11 },
    Yoga: { muscleGroups: ['Full Body', 'Hips', 'Shoulders', 'Spine'], equipment: ['Mat', 'Block', 'Strap'], baseCal: 4 },
    Core: { muscleGroups: ['Abs', 'Obliques', 'Lower Back'], equipment: ['None', 'Mat', 'Stability Ball'], baseCal: 7 },
    Flexibility: { muscleGroups: ['Hamstrings', 'Hips', 'Shoulders', 'Full Body'], equipment: ['Mat', 'Strap', 'None'], baseCal: 3 },
    HIIT: { muscleGroups: ['Full Body', 'Legs', 'Core'], equipment: ['None', 'Kettlebell', 'Box or Step', 'Dumbbells'], baseCal: 13 }
  };
  const categories = Object.keys(categoryMeta);
  const baseMovements = {
    Strength: ['Press', 'Row', 'Squat', 'Lunge', 'Curl', 'Raise', 'Pull-Up', 'Dip', 'Deadlift', 'Press-Up'],
    Cardio: ['Sprint', 'Jog', 'Jump', 'Climb', 'Cycle', 'Shuffle', 'Skip', 'Step-Up'],
    Yoga: ['Flow', 'Salutation', 'Pose Sequence', 'Balance Pose', 'Twist', 'Backbend'],
    Core: ['Crunch', 'Plank', 'Twist', 'Raise', 'Hold', 'Rollout'],
    Flexibility: ['Stretch', 'Mobility Drill', 'Release', 'Opener'],
    HIIT: ['Circuit', 'Tabata', 'Burpee Set', 'Sprint Interval', 'Complex']
  };
  const variations = ['Incline', 'Decline', 'Single-Leg', 'Banded', 'Tempo', 'Pulse', 'Weighted', 'Bodyweight', 'Explosive', 'Isometric'];
  const difficulties = ['Beginner', 'Intermediate', 'Advanced'];

  const rng = makeRng(7331);
  const exercises = [];

  for (let i = 0; i < count; i++) {
    const category = pick(rng, categories);
    const meta = categoryMeta[category];
    const movement = pick(rng, baseMovements[category]);
    const variation = pick(rng, variations);
    const muscleGroup = pick(rng, meta.muscleGroups);
    const equipment = pick(rng, meta.equipment);
    const difficulty = pick(rng, difficulties);

    const duration = 8 + Math.floor(rng() * 15);
    const caloriesPerMin = Math.max(2, Math.round(meta.baseCal + (rng() - 0.5) * 4));

    exercises.push({
      id: `gen-exercise-${i}`,
      name: `${variation} ${movement}`,
      category,
      muscle_group: muscleGroup,
      difficulty,
      equipment,
      duration_min: duration,
      calories_per_min: caloriesPerMin,
      instructions: [
        `Set up for a ${variation.toLowerCase()} ${movement.toLowerCase()}, using ${equipment === 'None' ? 'just your bodyweight' : equipment.toLowerCase()}`,
        `Perform the movement with controlled form, focusing on the ${muscleGroup.toLowerCase()}`,
        `Complete 3-4 sets, resting 30-60 seconds between sets`
      ],
      tips: `Keep form strict before adding intensity — the ${variation.toLowerCase()} variation raises difficulty on its own.`
    });
  }

  return exercises;
}

// Deterministic PRNG (mulberry32) so the generated review set is stable across restarts
function makeRng(seed) {
  let a = seed;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function pick(rng, arr) {
  return arr[Math.floor(rng() * arr.length)];
}

function seedReviews(targetCount = 1000, done) {
  done = done || (() => {});
  const firstNames = [
    'Priya', 'Rohan', 'Ananya', 'Vikram', 'Sneha', 'Arjun', 'Kavya', 'Aditya', 'Meera', 'Karan',
    'Isha', 'Rahul', 'Divya', 'Nikhil', 'Pooja', 'Sameer', 'Tanvi', 'Aman', 'Riya', 'Yash',
    'Sofia', 'Liam', 'Emma', 'Noah', 'Olivia', 'Mateo', 'Chloe', 'Lucas', 'Amara', 'Hiroshi',
    'Yuki', 'Wei', 'Ling', 'Carlos', 'Valentina', 'Giulia', 'Marco', 'Fatima', 'Omar', 'Layla',
    'Ethan', 'Grace', 'Diego', 'Camila', 'Jonas', 'Elena', 'Ravi', 'Anjali', 'Suresh', 'Lakshmi'
  ];
  const lastNames = [
    'Sharma', 'Verma', 'Iyer', 'Nair', 'Gupta', 'Reddy', 'Singh', 'Kapoor', 'Mehta', 'Joshi',
    'Rao', 'Bose', 'Chatterjee', 'Patel', 'Desai', 'Rossi', 'Romano', 'Silva', 'Garcia', 'Muller',
    'Tanaka', 'Kim', 'Chen', 'Wang', 'Santos', 'Costa', 'Al-Farsi', 'Novak', 'Dubois', 'Andersson'
  ];
  const locations = [
    'Mumbai, India', 'Bengaluru, India', 'Delhi, India', 'Pune, India', 'Chennai, India',
    'Hyderabad, India', 'Kolkata, India', 'Jaipur, India', 'Ahmedabad, India', 'Kochi, India',
    'Milan, Italy', 'Rome, Italy', 'Mexico City, Mexico', 'Guadalajara, Mexico', 'Tokyo, Japan',
    'Osaka, Japan', 'Bangkok, Thailand', 'Chiang Mai, Thailand', 'Athens, Greece', 'Barcelona, Spain',
    'New York, USA', 'Los Angeles, USA', 'Austin, USA', 'Shanghai, China', 'Beijing, China',
    'Toronto, Canada', 'London, UK', 'Dubai, UAE', 'Singapore', 'Sydney, Australia'
  ];
  const plans = ['Basic', 'Pro', 'Premium'];
  const features = [
    'the daily meal plan', 'the exercise library', 'the workout tracker', 'the international recipes',
    'the yoga routines', 'the HIIT circuits', 'the calorie tracking', 'the meal variety', 'the subscription value'
  ];
  const results = [
    'dropped 6 kilos', 'finally stuck to a routine', 'built real strength', 'felt more energetic every morning',
    'stopped getting bored with the same meals', 'hit a new personal best on my run', 'improved my flexibility',
    'started sleeping better', 'noticed real muscle gain', 'kept up a streak for the first time'
  ];
  const timeframes = ['in 6 weeks', 'in two months', 'over the last quarter', 'in just 30 days', 'within a season', 'after three months'];

  const titles5 = [
    'Exactly what I needed', 'Worth every rupee', 'Best fitness decision this year', 'Finally a plan that sticks',
    'Genuinely life-changing', 'My trainer friends are jealous', 'Can\'t imagine training without it', 'This app gets it'
  ];
  const titles4 = [
    'Really solid, small nitpicks', 'Great value overall', 'Does what it promises', 'Happy with the results',
    'Would recommend to a friend', 'Good plan, minor rough edges'
  ];
  const titles3 = [
    'Decent, but room to grow', 'It\'s okay for the price', 'Some parts better than others', 'Mixed feelings'
  ];
  const titles2 = ['Not quite there yet', 'Expected a bit more'];
  const titles1 = ['Did not work for me'];

  function bodyFor(rating, feature, result, timeframe, plan) {
    if (rating === 5) {
      return pick(rngBody, [
        `Switched to the ${plan} plan and ${result} ${timeframe}. ${feature[0].toUpperCase()}${feature.slice(1)} is the reason I actually stayed consistent.`,
        `I've tried a lot of fitness apps and this is the one that stuck. ${feature[0].toUpperCase()}${feature.slice(1)} kept things interesting, and I ${result} ${timeframe}.`,
        `Honestly did not expect to enjoy meal planning this much. Between ${feature} and steady logging, I ${result} ${timeframe}.`,
        `This replaced two separate apps for me. ${feature[0].toUpperCase()}${feature.slice(1)} alone was worth upgrading, and I ${result} ${timeframe}.`
      ]);
    }
    if (rating === 4) {
      return pick(rngBody, [
        `${feature[0].toUpperCase()}${feature.slice(1)} is genuinely good and I ${result} ${timeframe}. Wish there were a couple more filter options, but no complaints beyond that.`,
        `Solid experience overall — I ${result} ${timeframe} using the ${plan} plan. A few screens feel a little busy but nothing that gets in the way.`,
        `Really happy with ${feature}. Took a couple of weeks to find my rhythm, then I ${result} ${timeframe}.`
      ]);
    }
    if (rating === 3) {
      return pick(rngBody, [
        `${feature[0].toUpperCase()}${feature.slice(1)} is fine, though I expected a bit more personalization at the ${plan} tier. Still, I ${result} ${timeframe}.`,
        `Mixed experience — some weeks the plan clicked, other weeks it felt generic. Did eventually see progress and ${result} ${timeframe}.`
      ]);
    }
    if (rating === 2) {
      return pick(rngBody, [
        `${feature[0].toUpperCase()}${feature.slice(1)} needs work — recommendations repeated too often for my taste. Saw only minor change ${timeframe}.`
      ]);
    }
    return pick(rngBody, [
      `Didn't click for me. ${feature[0].toUpperCase()}${feature.slice(1)} felt generic and I didn't see much change ${timeframe}.`
    ]);
  }

  const rng = makeRng(42);
  const rngBody = makeRng(1337);
  const reviews = [];

  for (let i = 0; i < targetCount; i++) {
    const r = rng();
    let rating;
    if (r < 0.55) rating = 5;
    else if (r < 0.85) rating = 4;
    else if (r < 0.95) rating = 3;
    else if (r < 0.99) rating = 2;
    else rating = 1;

    const name = `${pick(rng, firstNames)} ${pick(rng, lastNames)}`;
    const location = pick(rng, locations);
    const plan = pick(rng, plans);
    const feature = pick(rng, features);
    const result = pick(rng, results);
    const timeframe = pick(rng, timeframes);
    const titlePool = { 5: titles5, 4: titles4, 3: titles3, 2: titles2, 1: titles1 }[rating];
    const title = pick(rng, titlePool);
    const body = bodyFor(rating, feature, result, timeframe, plan);
    const verified = rng() < 0.82;

    const daysAgo = Math.floor(rng() * 730);
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);
    const createdAt = date.toISOString().split('T')[0];

    reviews.push({
      id: `review-${i}`,
      name, location, rating, title, body, plan,
      verified: verified ? 1 : 0,
      created_at: createdAt
    });
  }

  db.get('SELECT COUNT(*) AS count FROM reviews', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    db.run('BEGIN TRANSACTION');
    reviews.forEach(rev => {
      db.run(
        'INSERT OR IGNORE INTO reviews (id, name, location, rating, title, body, plan, verified, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [rev.id, rev.name, rev.location, rev.rating, rev.title, rev.body, rev.plan, rev.verified, rev.created_at]
      );
    });
    db.run('COMMIT', done);
  });
}

// Seed Blogs
function seedBlogs(done) {
  done = done || (() => {});
  const blogs = [
    { id: 'blog-1', title: 'Nutrition 101: Understanding Macros', slug: 'nutrition-101-macros', author: 'Dr. Priya Sharma', category: 'Nutrition', content: 'A comprehensive guide to understanding proteins, carbs, and fats in your diet...', image_url: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&h=600&fit=crop', published_at: new Date(Date.now() - 7*24*60*60*1000).toISOString().split('T')[0], read_time_min: 8 },
    { id: 'blog-2', title: '10-Minute Morning Yoga Routine', slug: '10-min-morning-yoga', author: 'Yogi Ananya', category: 'Yoga', content: 'Start your day right with this energizing yoga flow that takes just 10 minutes...', image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=600&fit=crop', published_at: new Date(Date.now() - 5*24*60*60*1000).toISOString().split('T')[0], read_time_min: 6 },
    { id: 'blog-3', title: 'Recovery: Why Rest Days Matter', slug: 'recovery-rest-days', author: 'Coach Vikram', category: 'Training', content: 'Recovery is where the magic happens. Learn why rest days are crucial for progress...', image_url: 'https://images.unsplash.com/photo-1518611505868-d4c8e8c1f20f?w=800&h=600&fit=crop', published_at: new Date(Date.now() - 3*24*60*60*1000).toISOString().split('T')[0], read_time_min: 5 },
    { id: 'blog-4', title: 'Meal Prep Sunday: Indian Edition', slug: 'meal-prep-sunday-indian', author: 'Chef Meera', category: 'Nutrition', content: 'Prepare a week of healthy Indian meals in just 2 hours...', image_url: 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800&h=600&fit=crop', published_at: new Date(Date.now() - 10*24*60*60*1000).toISOString().split('T')[0], read_time_min: 7 },
    { id: 'blog-5', title: 'HIIT Workouts: Maximize Results', slug: 'hiit-maximize-results', author: 'Coach Rohan', category: 'Training', content: 'High-intensity interval training is one of the most efficient workout styles...', image_url: 'https://images.unsplash.com/photo-1552539618-7cdf54baf82f?w=800&h=600&fit=crop', published_at: new Date(Date.now() - 14*24*60*60*1000).toISOString().split('T')[0], read_time_min: 9 }
  ];

  const allBlogs = blogs.concat(generateBulkBlogs(95)); // Total 100 blogs

  db.get('SELECT COUNT(*) AS count FROM blogs', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    allBlogs.forEach(blog => {
      db.run(
        'INSERT OR IGNORE INTO blogs (id, title, slug, author, category, content, image_url, published_at, read_time_min) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [blog.id, blog.title, blog.slug, blog.author, blog.category, blog.content, blog.image_url, blog.published_at, blog.read_time_min]
      );
    });
    done();
  });
}

function generateBulkBlogs(count) {
  const categories = ['Nutrition', 'Training', 'Yoga', 'Recovery', 'Lifestyle', 'Mental Health'];
  const topics = {
    Nutrition: ['protein intake', 'hydration tips', 'superfoods', 'meal timing', 'diet myths'],
    Training: ['strength gains', 'cardio efficiency', 'form tips', 'progressive overload', 'cross-training'],
    Yoga: ['flexibility work', 'breathing techniques', 'meditation', 'alignment cues', 'pose progression'],
    Recovery: ['sleep hygiene', 'stress management', 'stretching routines', 'massage therapy', 'active recovery'],
    Lifestyle: ['habit building', 'motivation hacks', 'work-life balance', 'travel fitness', 'tracking progress'],
    'Mental Health': ['mindfulness', 'anxiety relief', 'goal setting', 'body confidence', 'holistic wellness']
  };
  const authors = ['Dr. Sharma', 'Coach Vikram', 'Yogi Ananya', 'Chef Meera', 'Dr. Gupta', 'Wellness Expert Rohan'];
  const rng = makeRng(3141);

  return Array.from({ length: count }, (_, i) => {
    const category = pick(rng, categories);
    const topic = pick(rng, topics[category]);
    return {
      id: `blog-${i + 6}`,
      title: `${category}: Deep Dive into ${topic}`,
      slug: `${category.toLowerCase()}-${topic.replace(/\s+/g, '-')}`,
      author: pick(rng, authors),
      category,
      content: `Learn everything you need to know about ${topic} for optimal fitness and wellness...`,
      image_url: `https://images.unsplash.com/photo-${1000000000 + i}?w=800&h=600&fit=crop`,
      published_at: new Date(Date.now() - Math.floor(rng() * 365) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      read_time_min: 5 + Math.floor(rng() * 10)
    };
  });
}

// Seed Shop Products
function seedShop(done) {
  done = done || (() => {});
  const products = [
    { id: 'prod-1', name: 'OJAS Yoga Mat Pro', category: 'Equipment', price: 1299, description: 'Premium non-slip yoga mat with alignment marks', image_url: 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=800&h=600&fit=crop', in_stock: 1 },
    { id: 'prod-2', name: 'Protein Powder - Vanilla', category: 'Supplements', price: 1499, description: 'Plant-based protein with 25g per serving', image_url: 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=800&h=600&fit=crop', in_stock: 1 },
    { id: 'prod-3', name: 'OJAS Water Bottle', category: 'Accessories', price: 599, description: 'Insulated 1L water bottle with time markers', image_url: 'https://images.unsplash.com/photo-1602143407151-7e6650489147?w=800&h=600&fit=crop', in_stock: 1 },
    { id: 'prod-4', name: 'Resistance Band Set', category: 'Equipment', price: 799, description: 'Set of 5 latex-free resistance bands', image_url: 'https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=800&h=600&fit=crop', in_stock: 1 },
    { id: 'prod-5', name: 'Meditation Cushion', category: 'Recovery', price: 1199, description: 'Ergonomic cushion for meditation practice', image_url: 'https://images.unsplash.com/photo-1529919050490-b06fa7e5db2a?w=800&h=600&fit=crop', in_stock: 1 }
  ];

  const allProducts = products.concat(generateBulkProducts(95)); // Total 100 products

  db.get('SELECT COUNT(*) AS count FROM shop_products', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    allProducts.forEach(prod => {
      db.run(
        'INSERT OR IGNORE INTO shop_products (id, name, category, price, description, image_url, in_stock) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [prod.id, prod.name, prod.category, prod.price, prod.description, prod.image_url, prod.in_stock]
      );
    });
    done();
  });
}

function generateBulkProducts(count) {
  const categories = ['Equipment', 'Supplements', 'Accessories', 'Recovery', 'Apparel'];
  const items = {
    Equipment: ['Dumbbells', 'Kettlebell', 'Resistance Band', 'Pull-up Bar', 'Exercise Ball', 'Foam Roller'],
    Supplements: ['Protein Powder', 'BCAA', 'Creatine', 'Multivitamin', 'Omega-3', 'Pre-Workout'],
    Accessories: ['Water Bottle', 'Gym Bag', 'Towel', 'Gloves', 'Headphones', 'Phone Holder'],
    Recovery: ['Massage Gun', 'Compression Sleeve', 'Foam Roller', 'Stretching Strap', 'Ice Pack'],
    Apparel: ['Yoga Pants', 'Sports Bra', 'Running Shoes', 'Tank Top', 'Shorts']
  };
  const rng = makeRng(2718);

  return Array.from({ length: count }, (_, i) => {
    const category = pick(rng, categories);
    const item = pick(rng, items[category]);
    const price = 299 + Math.floor(rng() * 2000);
    return {
      id: `prod-${i + 6}`,
      name: `OJAS ${item}`,
      category,
      price,
      description: `Premium ${item.toLowerCase()} for optimal performance`,
      image_url: `https://images.unsplash.com/photo-${1500000000 + i}?w=800&h=600&fit=crop`,
      in_stock: Math.random() > 0.1 ? 1 : 0
    };
  });
}

// Seed Nutrition Plans
function seedNutrition(done) {
  done = done || (() => {});
  const plans = [
    { id: 'nut-1', name: 'Weight Loss Warrior', description: 'High protein, calorie-deficit plan', duration_days: 30, goal: 'Weight Loss', image_url: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&h=600&fit=crop', daily_calories: 1800, macros: JSON.stringify({protein: 150, carbs: 180, fat: 60}), created_at: new Date().toISOString().split('T')[0] },
    { id: 'nut-2', name: 'Muscle Builder', description: 'High calorie, high protein for gains', duration_days: 30, goal: 'Muscle Gain', image_url: 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&h=600&fit=crop', daily_calories: 2800, macros: JSON.stringify({protein: 200, carbs: 350, fat: 90}), created_at: new Date().toISOString().split('T')[0] },
    { id: 'nut-3', name: 'Indian Vegan', description: 'Plant-based nutrition for wellness', duration_days: 30, goal: 'Wellness', image_url: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&h=600&fit=crop', daily_calories: 2000, macros: JSON.stringify({protein: 120, carbs: 280, fat: 55}), created_at: new Date().toISOString().split('T')[0] },
    { id: 'nut-4', name: 'Endurance Athlete', description: 'Optimized for stamina', duration_days: 30, goal: 'Endurance', image_url: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&h=600&fit=crop', daily_calories: 2600, macros: JSON.stringify({protein: 140, carbs: 380, fat: 70}), created_at: new Date().toISOString().split('T')[0] },
    { id: 'nut-5', name: 'Balanced Living', description: 'Sustainable nutrition for life', duration_days: 30, goal: 'Maintenance', image_url: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&h=600&fit=crop', daily_calories: 2200, macros: JSON.stringify({protein: 130, carbs: 275, fat: 73}), created_at: new Date().toISOString().split('T')[0] }
  ];

  const allPlans = plans.concat(generateBulkNutrition(95)); // Total 100 plans

  db.get('SELECT COUNT(*) AS count FROM nutrition_plans', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    allPlans.forEach(plan => {
      db.run(
        'INSERT OR IGNORE INTO nutrition_plans (id, name, description, duration_days, goal, image_url, daily_calories, macros, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [plan.id, plan.name, plan.description, plan.duration_days, plan.goal, plan.image_url, plan.daily_calories, plan.macros, plan.created_at]
      );
    });
    done();
  });
}

function generateBulkNutrition(count) {
  const goals = ['Weight Loss', 'Muscle Gain', 'Endurance', 'Wellness', 'Maintenance'];
  const rng = makeRng(1618);

  return Array.from({ length: count }, (_, i) => {
    const goal = pick(rng, goals);
    const calorieBase = { 'Weight Loss': 1800, 'Muscle Gain': 2800, 'Endurance': 2600, 'Wellness': 2000, 'Maintenance': 2200 };
    const calories = calorieBase[goal] + Math.floor((rng() - 0.5) * 400);
    const protein = Math.round(calories * 0.35 / 4);
    const carbs = Math.round(calories * 0.45 / 4);
    const fat = Math.round(calories * 0.20 / 9);

    return {
      id: `nut-${i + 6}`,
      name: `${goal} Plan ${i + 1}`,
      description: `Customized nutrition for ${goal.toLowerCase()}`,
      duration_days: 30,
      goal,
      image_url: `https://images.unsplash.com/photo-${2000000000 + i}?w=800&h=600&fit=crop`,
      daily_calories: calories,
      macros: JSON.stringify({protein, carbs, fat}),
      created_at: new Date().toISOString().split('T')[0]
    };
  });
}

// Seed Workout Programs
function seedWorkouts(done) {
  done = done || (() => {});
  const programs = [
    { id: 'wp-1', name: 'Full Body 4x/week', description: 'Complete body training for all levels', difficulty: 'Beginner', duration_weeks: 12, focus_area: 'Strength', image_url: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&h=600&fit=crop', free_tier: 1 },
    { id: 'wp-2', name: 'HIIT Bootcamp', description: 'High intensity fat burning program', difficulty: 'Intermediate', duration_weeks: 8, focus_area: 'Cardio', image_url: 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=800&h=600&fit=crop', free_tier: 1 },
    { id: 'wp-3', name: 'Yoga Flow 21-Day', description: 'Mindful movement and flexibility', difficulty: 'Beginner', duration_weeks: 3, focus_area: 'Flexibility', image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=600&fit=crop', free_tier: 1 },
    { id: 'wp-4', name: 'Advanced Strength', description: 'Periodized strength building', difficulty: 'Advanced', duration_weeks: 16, focus_area: 'Strength', image_url: 'https://images.unsplash.com/photo-1540497905036-3b5e22d1e8c0?w=800&h=600&fit=crop', free_tier: 0 },
    { id: 'wp-5', name: 'Endurance Builder', description: 'Build stamina and cardiovascular strength', difficulty: 'Intermediate', duration_weeks: 10, focus_area: 'Cardio', image_url: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&h=600&fit=crop', free_tier: 1 }
  ];

  const allPrograms = programs.concat(generateBulkWorkouts(95)); // Total 100 programs

  db.get('SELECT COUNT(*) AS count FROM workout_programs', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    allPrograms.forEach(prog => {
      db.run(
        'INSERT OR IGNORE INTO workout_programs (id, name, description, difficulty, duration_weeks, focus_area, image_url, free_tier, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [prog.id, prog.name, prog.description, prog.difficulty, prog.duration_weeks, prog.focus_area, prog.image_url, prog.free_tier, prog.created_at]
      );
    });
    done();
  });
}

function generateBulkWorkouts(count) {
  const focuses = ['Strength', 'Cardio', 'Flexibility', 'Endurance', 'Power'];
  const difficulties = ['Beginner', 'Intermediate', 'Advanced'];
  const rng = makeRng(5000);

  return Array.from({ length: count }, (_, i) => {
    const focus = pick(rng, focuses);
    const difficulty = pick(rng, difficulties);
    const weeks = 4 + Math.floor(rng() * 12);
    return {
      id: `wp-${i + 6}`,
      name: `${focus} - ${difficulty} (${weeks}w)`,
      description: `${difficulty} level ${focus.toLowerCase()} program designed for optimal results`,
      difficulty,
      duration_weeks: weeks,
      focus_area: focus,
      image_url: `https://images.unsplash.com/photo-${2500000000 + i}?w=800&h=600&fit=crop`,
      free_tier: rng() > 0.3 ? 1 : 0,
      created_at: new Date().toISOString().split('T')[0]
    };
  });
}

// Seed Coaching Agents
function seedCoachingAgents(done) {
  done = done || (() => {});
  const agents = [
    { id: 'agent-1', user_id: DEMO_USER_ID, agent_type: 'Personal Trainer', expertise: 'Strength Training', last_interaction: new Date().toISOString().split('T')[0], created_at: new Date().toISOString().split('T')[0] },
    { id: 'agent-2', user_id: DEMO_USER_ID, agent_type: 'Nutrition Coach', expertise: 'Meal Planning', last_interaction: new Date().toISOString().split('T')[0], created_at: new Date().toISOString().split('T')[0] },
    { id: 'agent-3', user_id: DEMO_USER_ID, agent_type: 'Recovery Specialist', expertise: 'Sleep & Wellness', last_interaction: new Date().toISOString().split('T')[0], created_at: new Date().toISOString().split('T')[0] }
  ];

  db.get('SELECT COUNT(*) AS count FROM coaching_agents', (err, row) => {
    if (err || (row && row.count > 0)) return done();
    agents.forEach(agent => {
      db.run(
        'INSERT OR IGNORE INTO coaching_agents (id, user_id, agent_type, expertise, last_interaction, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        [agent.id, agent.user_id, agent.agent_type, agent.expertise, agent.last_interaction, agent.created_at]
      );
    });
    done();
  });
}

// ---------------------------------------------------------------------------
// Recipes / Meals
// ---------------------------------------------------------------------------

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

// Deterministic "random" pick so a day's plan is stable but changes daily
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
  }
  return hash;
}

app.get('/api/daily-plan/:userId', (req, res) => {
  const { userId } = req.params;
  const date = req.query.date || new Date().toISOString().split('T')[0];
  const country = req.query.country && req.query.country !== 'All' ? req.query.country : null;

  const countryClause = country ? ' AND country = ?' : '';
  const params = country ? [country] : [];

  const categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const plan = {};
  let remaining = categories.length;
  let failed = false;

  categories.forEach(category => {
    db.all(`SELECT * FROM recipes WHERE category = ?${countryClause}`, [category, ...params], (err, rows) => {
      if (err) {
        failed = true;
      } else if (rows.length > 0) {
        const index = hashString(`${userId}-${date}-${category}`) % rows.length;
        const row = rows[index];
        plan[category.toLowerCase()] = {
          ...row,
          ingredients: JSON.parse(row.ingredients),
          instructions: JSON.parse(row.instructions)
        };
      } else {
        plan[category.toLowerCase()] = null;
      }

      remaining--;
      if (remaining === 0) {
        if (failed) {
          res.status(500).json({ error: 'Failed to generate daily plan' });
        } else {
          res.json({ date, country: country || 'All', plan });
        }
      }
    });
  });
});

// ---------------------------------------------------------------------------
// Exercises
// ---------------------------------------------------------------------------

app.get('/api/exercises', (req, res) => {
  db.all('SELECT * FROM exercises', (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows.map(row => ({
        ...row,
        instructions: JSON.parse(row.instructions)
      })));
    }
  });
});

// ---------------------------------------------------------------------------
// Reviews
// ---------------------------------------------------------------------------

app.get('/api/reviews', (req, res) => {
  const page = Math.max(parseInt(req.query.page, 10) || 1, 1);
  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 12, 1), 50);
  const ratingFilter = req.query.rating ? parseInt(req.query.rating, 10) : null;
  const offset = (page - 1) * limit;

  const whereClause = ratingFilter ? 'WHERE rating = ?' : '';
  const params = ratingFilter ? [ratingFilter] : [];

  db.get(`SELECT COUNT(*) AS count FROM reviews ${whereClause}`, params, (countErr, countRow) => {
    if (countErr) return res.status(500).json({ error: countErr.message });

    db.all(
      `SELECT * FROM reviews ${whereClause} ORDER BY created_at DESC LIMIT ? OFFSET ?`,
      [...params, limit, offset],
      (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });

        db.all('SELECT rating, COUNT(*) AS count FROM reviews GROUP BY rating', (distErr, distRows) => {
          if (distErr) return res.status(500).json({ error: distErr.message });

          const distribution = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
          let total = 0;
          let sum = 0;
          distRows.forEach(d => {
            distribution[d.rating] = d.count;
            total += d.count;
            sum += d.rating * d.count;
          });

          res.json({
            reviews: rows,
            page,
            limit,
            total: countRow.count,
            totalAll: total,
            average: total > 0 ? Math.round((sum / total) * 10) / 10 : 0,
            distribution
          });
        });
      }
    );
  });
});

// ---------------------------------------------------------------------------
// Workouts
// ---------------------------------------------------------------------------

app.get('/api/workouts/:userId', (req, res) => {
  db.all('SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC', [req.params.userId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

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

// ---------------------------------------------------------------------------
// Users & Subscriptions
// ---------------------------------------------------------------------------

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

const PLAN_PRICING = {
  basic: 99,
  pro: 199,
  premium: 299,
  elite: 999
};

app.post('/api/subscribe', (req, res) => {
  const { userId, planId, billingCycle } = req.body;

  if (!PLAN_PRICING[planId]) {
    return res.status(400).json({ error: 'Invalid plan' });
  }

  const cycle = billingCycle === 'annual' ? 'annual' : 'monthly';
  const expiry = new Date();
  if (cycle === 'annual') {
    expiry.setFullYear(expiry.getFullYear() + 1);
  } else {
    expiry.setMonth(expiry.getMonth() + 1);
  }
  const planExpiry = expiry.toISOString().split('T')[0];

  db.run(
    'UPDATE users SET plan = ?, billing_cycle = ?, plan_expiry = ? WHERE id = ?',
    [planId, cycle, planExpiry, userId],
    (err) => {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      db.get('SELECT * FROM users WHERE id = ?', [userId], (getErr, row) => {
        if (getErr) {
          res.status(500).json({ error: getErr.message });
        } else {
          res.json(row);
        }
      });
    }
  );
});

// ---------------------------------------------------------------------------
// Blogs
// ---------------------------------------------------------------------------

app.get('/api/blogs', (req, res) => {
  const page = Math.max(parseInt(req.query.page, 10) || 1, 1);
  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 12, 1), 50);
  const category = req.query.category;
  const offset = (page - 1) * limit;

  const whereClause = category ? 'WHERE category = ?' : '';
  const params = category ? [category] : [];

  db.get(`SELECT COUNT(*) AS count FROM blogs ${whereClause}`, params, (countErr, countRow) => {
    if (countErr) return res.status(500).json({ error: countErr.message });

    db.all(
      `SELECT * FROM blogs ${whereClause} ORDER BY published_at DESC LIMIT ? OFFSET ?`,
      [...params, limit, offset],
      (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ blogs: rows, page, limit, total: countRow.count });
      }
    );
  });
});

app.get('/api/blogs/:id', (req, res) => {
  db.get('SELECT * FROM blogs WHERE id = ? OR slug = ?', [req.params.id, req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Blog not found' });
    } else {
      res.json(row);
    }
  });
});

// ---------------------------------------------------------------------------
// Shop
// ---------------------------------------------------------------------------

app.get('/api/shop', (req, res) => {
  const category = req.query.category;
  const whereClause = category ? 'WHERE category = ?' : '';
  const params = category ? [category] : [];

  db.all(`SELECT * FROM shop_products ${whereClause}`, params, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

app.get('/api/shop/:id', (req, res) => {
  db.get('SELECT * FROM shop_products WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Product not found' });
    } else {
      res.json(row);
    }
  });
});

// ---------------------------------------------------------------------------
// Nutrition Plans
// ---------------------------------------------------------------------------

app.get('/api/nutrition-plans', (req, res) => {
  const goal = req.query.goal;
  const whereClause = goal ? 'WHERE goal = ?' : '';
  const params = goal ? [goal] : [];

  db.all(`SELECT * FROM nutrition_plans ${whereClause}`, params, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows.map(row => ({
        ...row,
        macros: JSON.parse(row.macros)
      })));
    }
  });
});

app.get('/api/nutrition-plans/:id', (req, res) => {
  db.get('SELECT * FROM nutrition_plans WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Plan not found' });
    } else {
      res.json({
        ...row,
        macros: JSON.parse(row.macros)
      });
    }
  });
});

// ---------------------------------------------------------------------------
// Workout Programs
// ---------------------------------------------------------------------------

app.get('/api/workout-programs', (req, res) => {
  const focus = req.query.focus;
  const difficulty = req.query.difficulty;
  const free = req.query.free === 'true';

  let whereClause = [];
  let params = [];

  if (focus) {
    whereClause.push('focus_area = ?');
    params.push(focus);
  }
  if (difficulty) {
    whereClause.push('difficulty = ?');
    params.push(difficulty);
  }
  if (free) {
    whereClause.push('free_tier = 1');
  }

  const where = whereClause.length > 0 ? 'WHERE ' + whereClause.join(' AND ') : '';

  db.all(`SELECT * FROM workout_programs ${where}`, params, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

app.get('/api/workout-programs/:id', (req, res) => {
  db.get('SELECT * FROM workout_programs WHERE id = ?', [req.params.id], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else if (!row) {
      res.status(404).json({ error: 'Program not found' });
    } else {
      res.json(row);
    }
  });
});

// ---------------------------------------------------------------------------
// Agentic Features - AI Coaching
// ---------------------------------------------------------------------------

app.get('/api/coaching-agents/:userId', (req, res) => {
  db.all('SELECT * FROM coaching_agents WHERE user_id = ?', [req.params.userId], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

// AI-powered personalized recommendation endpoint
app.post('/api/ai/recommendations', (req, res) => {
  const { userId, type } = req.body;

  // Simulated AI recommendation logic
  const recommendations = {
    workout: {
      agent: 'Personal Trainer Bot',
      recommendation: 'Based on your activity, try High-Intensity Interval Training 3x/week for maximum efficiency',
      confidence: 0.87,
      generated_at: new Date().toISOString()
    },
    nutrition: {
      agent: 'Nutrition Coach Bot',
      recommendation: 'Your macros suggest increasing protein intake by 15g daily for optimal muscle recovery',
      confidence: 0.92,
      generated_at: new Date().toISOString()
    },
    recovery: {
      agent: 'Recovery Specialist Bot',
      recommendation: 'Your sleep pattern indicates need for 30 minutes of evening yoga to improve sleep quality',
      confidence: 0.85,
      generated_at: new Date().toISOString()
    }
  };

  const rec = recommendations[type] || recommendations.workout;
  res.json(rec);
});

// AI chat endpoint for coaching
app.post('/api/ai/coach-chat', (req, res) => {
  const { userId, message, agentType } = req.body;

  // Simulated coaching response
  const responses = {
    'Personal Trainer': 'Great question! Progressive overload is key. Increase weight by 5-10% every week while maintaining form.',
    'Nutrition Coach': 'For muscle gain, aim for 2.2g of protein per kg of body weight daily. Spread it across 5-6 meals.',
    'Recovery Specialist': 'Aim for 7-9 hours of sleep. Create a bedtime routine: 30 min yoga, meditation, and avoid screens 1 hour before bed.'
  };

  const response = responses[agentType] || 'I\'m here to help! What would you like to know?';

  // Log interaction
  db.run(
    'UPDATE coaching_agents SET last_interaction = ? WHERE user_id = ? AND agent_type = ?',
    [new Date().toISOString().split('T')[0], userId, agentType],
    () => {
      res.json({
        agent: agentType,
        response,
        timestamp: new Date().toISOString()
      });
    }
  );
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
