import React from "react";
import "./Favorites.css";

const recipes = [
  {
    title: "Miso Glazed Salmon",
    time: "25 mins",
    servings: "2 Servings",
    image: "https://images.unsplash.com/photo-1467003909585-2f8a72700288"
  },
  {
    title: "Quinoa Chickpea Bowl",
    time: "15 mins",
    servings: "1 Serving",
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
  },
  {
    title: "Pesto Pasta",
    time: "20 mins",
    servings: "4 Servings",
    image: "https://images.unsplash.com/photo-1525755662778-989d0524087e"
  },
  {
    title: "Avocado Toast",
    time: "10 mins",
    servings: "1 Serving",
    image: "https://images.unsplash.com/photo-1504674900247-0877df9cc836"
  }
];

function Favorites() {
  return (
    <div className="favorites-container">
      <h1>Your Favorite Recipes</h1>
      <p className="subtitle">A collection of your saved recipes.</p>

      <div className="recipe-grid">
        {recipes.map((recipe, index) => (
          <div key={index} className="recipe-card">
            <img src={recipe.image} alt={recipe.title} />
            <div className="recipe-content">
              <h3>{recipe.title}</h3>
              <p>{recipe.time} • {recipe.servings}</p>
              <button>View Recipe</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Favorites;