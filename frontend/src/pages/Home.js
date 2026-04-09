import { useState } from "react";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import GenerateButton from "../components/GenerateButton";
import SuggestedRecipes from "../components/SuggestedRecipes";
import WhyChefAI from "../components/WhyChefAI";
import Footer from "../components/Footer";

const defaultRecipes = [
  {
    recipe_name: "Mediterranean Bowl",
    cuisine: "Healthy",
    time: "15 MINS",
    score: 0.95,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
  },
  {
    recipe_name: "Pantry Pasta Pesto",
    cuisine: "Italian",
    time: "20 MINS",
    score: 0.92,
    image: "https://images.unsplash.com/photo-1525755662778-989d0524087e"
  },
  {
    recipe_name: "Veg Rice Bowl",
    cuisine: "Asian",
    time: "18 MINS",
    score: 0.89,
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
  },
  {
    recipe_name: "Avocado Toast",
    cuisine: "Breakfast",
    time: "10 MINS",
    score: 0.91,
    image: "https://images.unsplash.com/photo-1588137378633-dea1336ce1e2?w=800"
  },
  {
    recipe_name: "Grilled Veg Salad",
    cuisine: "Healthy",
    time: "12 MINS",
    score: 0.88,
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
  }
];

function Home() {
  const [ingredients, setIngredients] = useState("");

  // NEW FILTER STATES
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedCookingTime, setSelectedCookingTime] = useState("");
  const [selectedCuisine, setSelectedCuisine] = useState("");
  const [allergy, setAllergy] = useState("");

  const [recipes, setRecipes] = useState(defaultRecipes);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecipes = async () => {
    if (!ingredients.trim()) {
      setError("Please enter ingredients first");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ingredients: ingredients,
        top_k: 5
      };

      // Add cuisine only if not ANY
      if (selectedCuisine && selectedCuisine !== "ANY") {
        payload.cuisine = selectedCuisine;
      }

      // Add category if selected
      if (selectedCategory) {
        payload.category = selectedCategory;
      }

      // Add cooking time range if selected
      if (selectedCookingTime) {
        payload.cooking_time_range = selectedCookingTime;
      }

      // Add allergy if entered
      if (allergy.trim()) {
        payload.allergy = allergy.trim();
      }

      const response = await fetch("http://localhost:5000/search/text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.recipes && data.recipes.length > 0) {
        const transformedRecipes = data.recipes.map((recipe) => ({
       // main card data
       recipe_name: recipe.recipe_name || recipe["Recipe name"] || "Unnamed Recipe",
       final_recipe_name: recipe.final_recipe_name || recipe["Final recipe name"] || "",
       cuisine: recipe.Cuisine || "Unknown",
       time: recipe["CookingTime"] || "N/A",
       score: recipe.similarity_score || 0,
       image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", // default image

       // full details for recipe details page
       instructions: recipe.Instructions || "",
       detailed_ingredients: recipe["Detailed_Ingredients"] || "",
       calories: recipe["Calories (kcal)"] || "N/A",
       carbohydrates: recipe["Carbohydrates g"] || "N/A",
        protein: recipe["Protein g"] || "N/A",
       fats: recipe["Fats g"] || "N/A",
       free_sugar: recipe["Free Sugar g"] || "N/A",
       fibre: recipe["Fibre g"] || "N/A",
       sodium: recipe["Sodium mg"] || "N/A",
       calcium: recipe["Calcium mg"] || "N/A",
       iron: recipe["Iron mg"] || "N/A"
      }));

        setRecipes(transformedRecipes);
      } else {
        setError("No recipes found. Try different ingredients or change the filters.");
        setRecipes([]);
      }

      
    } catch (err) {
      console.error("Error fetching recipes:", err);
      setError("Failed to fetch recipes. Make sure the backend is running on port 5000.");
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Navbar />
      <Hero />

      <SearchBar ingredients={ingredients} setIngredients={setIngredients} />

      {/* FILTER SECTION */}
      <div
        style={{
          maxWidth: "1100px",
          margin: "20px auto",
          padding: "0 20px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "15px"
        }}
      >
        {/* Category */}
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={filterStyle}
        >
          <option value="">Category</option>
          <option value="Veg">Veg</option>
          <option value="Non-Veg">Non-Veg</option>
        </select>

        {/* Cooking Time */}
        <select
          value={selectedCookingTime}
          onChange={(e) => setSelectedCookingTime(e.target.value)}
          style={filterStyle}
        >
          <option value="">Cooking Time</option>
          <option value="1-30">1-30 mins</option>
          <option value="30-80">30-80 mins</option>
          <option value="80-150">80-150 mins</option>
          <option value="150-200">150-200 mins</option>
          <option value="200-250">200-250 mins</option>
          <option value="250-300">250-300 mins</option>
          <option value="300+">300+ mins</option>
        </select>

        {/* Cuisine */}
        <select
          value={selectedCuisine}
          onChange={(e) => setSelectedCuisine(e.target.value)}
          style={filterStyle}
        >
          <option value="">Cuisine</option>
          <option value="Other">Other</option>
          <option value="Indian">Indian</option>
          <option value="Chinese">Chinese</option>
          <option value="Italian">Italian</option>
          <option value="Continental">Continental</option>
          <option value="Mexican">Mexican</option>
          <option value="French">French</option>
          <option value="Thai">Thai</option>
          <option value="American">American</option>
          <option value="Korean">Korean</option>
          <option value="Japanese">Japanese</option>
          <option value="Spanish">Spanish</option>
          <option value="Greek">Greek</option>
          <option value="Turkish">Turkish</option>
          <option value="German">German</option>
          <option value="Brazilian">Brazilian</option>
          <option value="Filipino">Filipino</option>
          <option value="Indonesian">Indonesian</option>
          <option value="Ethiopian">Ethiopian</option>
          <option value="Moroccan">Moroccan</option>
          <option value="Vietnamese">Vietnamese</option>
        </select>

        {/* Allergy */}
        <input
          type="text"
          placeholder="Enter allergy"
          value={allergy}
          onChange={(e) => setAllergy(e.target.value)}
          style={filterStyle}
        />
      </div>

      <GenerateButton fetchRecipes={fetchRecipes} />

      {loading && (
        <div style={{ textAlign: "center", padding: "20px" }}>
          Loading recipes...
        </div>
      )}

      {error && (
        <div style={{ textAlign: "center", padding: "20px", color: "red" }}>
          {error}
        </div>
      )}

      <SuggestedRecipes recipes={recipes} />
      <WhyChefAI />
      <Footer />
    </div>
  );
}

// Simple common style
const filterStyle = {
  padding: "12px 14px",
  borderRadius: "10px",
  border: "1px solid #ccc",
  fontSize: "14px",
  outline: "none",
  width: "100%",
  backgroundColor: "#fff",
  color:"grey"
};

export default Home;