import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import GenerateButton from "../components/GenerateButton";
import SuggestedRecipes from "../components/SuggestedRecipes";
import RecipeCard from "../components/RecipeCard"; // ✅ needed for strict recipe
import WhyChefAI from "../components/WhyChefAI";
import Footer from "../components/Footer";

const defaultRecipes = [
  { 
    recipe_name: "Mediterranean Bowl", 
    final_recipe_name: "Colorful Mediterranean Grain Bowl", 
    cuisine: "Healthy", 
    time: "15 MINS", 
    score: 0.95, 
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", 
    Category: "Veg",
    Instructions: "Cook quinoa, chop vegetables, mix with dressing, add feta.",
    "Detailed_Ingredients": "Quinoa, vegetables, feta, olive oil",
    "Calories (kcal)": 380, 
    "Carbohydrates g": 45,
    "Protein g": 14,
    "Fats g": 18 
  }, 
  {
    recipe_name: "Pantry Pasta Pesto",
    final_recipe_name: "Quick Basil Pesto Pasta", 
    cuisine: "Italian", 
    time: "20 MINS", 
    score: 0.92, 
    image: "https://images.unsplash.com/photo-1525755662778-989d0524087e", 
    Category: "Veg", 
    Instructions: "Cook pasta, blend pesto, mix and serve.", 
    "Detailed_Ingredients": "Pasta, basil, garlic, olive oil", 
    "Calories (kcal)": 520, 
    "Carbohydrates g": 62, 
    "Protein g": 18, 
    "Fats g": 24 
  }, 
  { 
    recipe_name: "Grilled Chicken Bowl", 
    final_recipe_name: "Herb Grilled Chicken Rice Bowl", 
    cuisine: "American",
    time: "25 MINS", 
    score: 0.93, 
    image: "https://images.unsplash.com/photo-1562967916-eb82221dfb92?auto=format&fit=crop&w=800&q=80", 
    Category: "Non-Veg", 
    Instructions: "Grill seasoned chicken, cook rice, sauté vegetables, assemble bowl and serve.", 
    "Detailed_Ingredients": "Chicken breast, rice, bell peppers, olive oil, garlic, herbs, salt, pepper", 
    "Calories (kcal)": 480, 
    "Carbohydrates g": 50, 
    "Protein g": 35, 
    "Fats g": 15 
  }, 
  { 
    recipe_name: "Masala Omelette", 
    final_recipe_name: "Indian Spiced Egg Omelette", 
    cuisine: "Indian", 
    time: "10 MINS", 
    score: 0.90, 
    image: "https://images.unsplash.com/photo-1608039829572-78524f79c4c7", 
    Category: "Non-Veg",
    Instructions: "Beat eggs with spices, add chopped onions and chilies, cook on pan until golden.", 
    "Detailed_Ingredients": "Eggs, onion, green chili, turmeric, salt, oil, coriander leaves", 
    "Calories (kcal)": 220, 
    "Carbohydrates g": 5, 
    "Protein g": 14, 
    "Fats g": 16 
  }, 
  { 
    recipe_name: "Chickpea Salad", 
    final_recipe_name: "Fresh Mediterranean Chickpea Salad",
    cuisine: "Mediterranean", 
    time: "12 MINS", 
    score: 0.88, 
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd", 
    Category: "Veg", 
    Instructions: "Mix chickpeas with chopped vegetables, drizzle olive oil and lemon, toss well.", 
    "Detailed_Ingredients": "Boiled chickpeas, cucumber, tomato, onion, olive oil, lemon juice, salt", 
    "Calories (kcal)": 300, 
    "Carbohydrates g": 40, 
    "Protein g": 12, 
    "Fats g": 10 
  }
];

function Home() {
  const [ingredients, setIngredients] = useState("");
  
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedCookingTime, setSelectedCookingTime] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState("");
  const [allergy, setAllergy] = useState("");
  const [strictRecipes, setStrictRecipes] = useState(null); // 🔥 NEW STATE
  const location = useLocation();
  
  const [recipes, setRecipes] = useState(defaultRecipes);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(null);

  
 // =========================
// LOAD SAVED STATE (FIXED)
// =========================
useEffect(() => {
  const state = location.state;

  // =========================
  // 1. BACK NAVIGATION RESTORE FROM DETAILS
  // =========================
  if (state?.fromDetails) {
    const hasRecipeState = state && typeof state === "object" && (
      Object.prototype.hasOwnProperty.call(state, "recipes") ||
      Object.prototype.hasOwnProperty.call(state, "strictRecipes")
    );

    if (hasRecipeState) {
      setRecipes(
        Object.prototype.hasOwnProperty.call(state, "recipes")
          ? state.recipes
          : defaultRecipes
      );
      setStrictRecipes(
        Object.prototype.hasOwnProperty.call(state, "strictRecipes")
          ? state.strictRecipes
          : null
      );

      setIngredients(
        Object.prototype.hasOwnProperty.call(state, "ingredients")
          ? state.ingredients
          : ""
      );
      setSelectedCuisine(
        Object.prototype.hasOwnProperty.call(state, "selectedCuisine")
          ? state.selectedCuisine
          : ""
      );
      setSelectedCategory(
        Object.prototype.hasOwnProperty.call(state, "selectedCategory")
          ? state.selectedCategory
          : ""
      );
      setSelectedCookingTime(
        Object.prototype.hasOwnProperty.call(state, "selectedCookingTime")
          ? state.selectedCookingTime
          : ""
      );
      setAllergy(
        Object.prototype.hasOwnProperty.call(state, "allergy")
          ? state.allergy
          : ""
      );
      setMessage(
        Object.prototype.hasOwnProperty.call(state, "message")
          ? state.message
          : ""
      );
      return;
    }

    const saved = localStorage.getItem("recipeSearchState");

    if (saved) {
      try {
        const parsed = JSON.parse(saved);

        setRecipes(parsed.recipes || defaultRecipes);
        setStrictRecipes(parsed.strictRecipes || null);

        setIngredients(parsed.ingredients || "");
        setSelectedCuisine(parsed.selectedCuisine || "");
        setSelectedCategory(parsed.selectedCategory || "");
        setSelectedCookingTime(parsed.selectedCookingTime || "");
        setAllergy(parsed.allergy || "");
        setMessage(parsed.message || "");
      } catch (e) {
        console.error(e);
      }
    }
    return;
  }

  // =========================
  // 2. NORMAL LOCAL STORAGE LOAD
  // =========================
  const savedState = localStorage.getItem("recipeSearchState");

  if (savedState) {
    try {
      const parsed = JSON.parse(savedState);

      setRecipes(parsed.recipes?.length ? parsed.recipes : defaultRecipes);
      setStrictRecipes(parsed.strictRecipes || null);

      setIngredients(parsed.ingredients || "");
      setSelectedCuisine(parsed.selectedCuisine || "");
      setSelectedCategory(parsed.selectedCategory || "");
      setSelectedCookingTime(parsed.selectedCookingTime || "");
      setAllergy(parsed.allergy || "");
      setMessage(parsed.message || "");
      return;
    } catch (e) {
      console.error(e);
    }
  }

  // =========================
  // 3. DEFAULT
  // =========================
  setRecipes(defaultRecipes);
  setStrictRecipes(null);
}, [location]);

// =========================
// SAVE STATE (FIXED)
// =========================

useEffect(() => {
  const stateToSave = {
    recipes,
    strictRecipes,
    ingredients,
    selectedCuisine,
    selectedCategory,
    selectedCookingTime,
    allergy,
    message
  };

  localStorage.setItem("recipeSearchState", JSON.stringify(stateToSave));
}, [
  recipes,
  strictRecipes,
  ingredients,
  selectedCuisine,
  selectedCategory,
  selectedCookingTime,
  allergy,
  message
]);

  // =========================
  // FETCH RECIPES
  // =========================
  const fetchRecipes = async () => {
    if (!ingredients.trim()) {
      setError("Please enter ingredients first");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ingredients,
        top_k: 5
      };

      if (selectedCuisine) payload.cuisine = selectedCuisine;
      if (selectedCategory) payload.category = selectedCategory;
      if (selectedCookingTime)
        payload.cooking_time_range = selectedCookingTime;
      if (allergy.trim()) payload.allergy = allergy.trim();

      const response = await fetch(
        "http://localhost:5000/search/text",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      );

      const data = await response.json();
      let transformed = [];
     
      

     // =========================
// 🔥 STRICT RECIPE FIRST
// =========================
let strict = null;

if (data.strict_recipes && data.strict_recipes.length > 0) {
  strict = {
    ...data.strict_recipes[0],
    time: data.strict_recipes[0].CookingTime
      ? `${data.strict_recipes[0].CookingTime} mins`
      : "N/A",
    cuisine: data.strict_recipes[0].Cuisine || "Unknown",
    image:
      "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
  };

  setStrictRecipes(strict);
} else {
  setStrictRecipes(null);
}


if (data.recipes && data.recipes.length > 0) {
  transformed = data.recipes
    .map((r) => ({
      ...r,
      time: r.CookingTime ? `${r.CookingTime} mins` : "N/A",
      cuisine: r.Cuisine || "Unknown",
      image:
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
    }))
   
    .filter((r) => !strict || r.recipe_name !== strict.recipe_name);

  setRecipes(transformed);
} else {
  setRecipes([]);
}


      setMessage("Found 5 Recipes");
      localStorage.setItem("recipeSearchState", JSON.stringify({
  recipes: transformed,
  strictRecipes: strict,
  ingredients,
  selectedCuisine,
  selectedCategory,
  selectedCookingTime,
  allergy,
  message: "Found 5 Recipes"
}));
      
    } catch (err) {
      console.error(err);
      setError("Backend error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Navbar />
      <Hero />

      <SearchBar
        ingredients={ingredients}
        setIngredients={setIngredients}
      />

      {/* FILTERS */}
      <div style={styles.filterContainer}>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={styles.input}
        >
          <option value="">Category</option>
          <option value="Veg">Veg</option>
          <option value="Non-Veg">Non-Veg</option>
        </select>

        <select value={selectedCookingTime} onChange={(e) => setSelectedCookingTime(e.target.value)} 
        style={styles.input} >
           <option value="">Cooking Time</option> 
          <option value="1-30">1-30 mins</option>
          <option value="30-80">30-80 mins</option>
          <option value="80-150">80-150 mins</option>
          <option value="150-200">150-200 mins</option>
          <option value="200+">200 mins+</option>
        </select>

        <select
          value={selectedCuisine}
          onChange={(e) => setSelectedCuisine(e.target.value)}
          style={styles.input}
        >
          <option value="">Cuisine</option>
          <option value="Indian">Indian</option>
          <option value="Italian">Italian</option>
          <option value="Chinese">Chinese</option>
          <option value="American">American</option> 
          <option value="French">French</option> 
          <option value="German">German</option> 
          <option value="Continental">Continental</option> 
          <option value="Mexican">Mexican</option> 
          <option value="Thai">Thai</option> 
          <option value="Korean">Korean</option> 
          <option value="Japanese">Japanese</option> 
          <option value="Spanish">Spanish</option> 
          <option value="Greek">Greek</option> 
          <option value="Turkish">Turkish</option> 
          <option value="Brazilian">Brazilian</option>
          <option value="Filipino">Filipino</option> 
          <option value="Vietnamese">Vietnamese</option> 
          <option value="Indonesian">Indonesian</option> 
          <option value="Ethiopian">Ethiopian</option> 
          <option value="Moroccan">Moroccan</option> 
          <option value="Other">Other</option>
        </select>

        <input
          placeholder="Allergy"
          value={allergy}
          onChange={(e) => setAllergy(e.target.value)}
          style={styles.input}
        />
      </div>

      <GenerateButton fetchRecipes={fetchRecipes} />

      {loading && <p style={styles.center}>Loading...</p>}
      {error && <p style={styles.error}>{error}</p>}
      {message && <p style={styles.center}>{message}</p>}

      {/* 🔹 NORMAL RESULTS */}
      <SuggestedRecipes recipes={recipes} strictRecipes={strictRecipes} />

      {/* 🔥 STRICT RESULT */}
      {strictRecipes && (
        <div style={styles.strictContainer}>
          <h2 style={styles.strictTitle}>
            🔥 Perfect Match (Only Your Ingredients)
          </h2>

          <RecipeCard
            recipe={strictRecipes}
            strictRecipes={strictRecipes}
            recipes={recipes}
          />
        </div>
      )}

      <WhyChefAI />
      <Footer />
    </div>
  );
}

const styles = {
  filterContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "15px",
    padding: "20px"
  },
  input: {
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc"
  },
  center: {
    textAlign: "center",
    padding: "10px"
  },
  error: {
    color: "red",
    textAlign: "center"
  },

  // 🔥 STRICT UI
  strictContainer: {
    margin: "40px auto",
    maxWidth: "800px",
    textAlign: "center"
  },
  strictTitle: {
    fontSize: "1.8rem",
    marginBottom: "20px",
    color: "#111"
  }
};

export default Home;