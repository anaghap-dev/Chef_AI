import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { normalizeRecipe } from "../utils/normalizeRecipe";

function RecipeCard({recipe,
  onView,
  recipes,
  strictRecipes,
  ingredients,
  selectedCategory,
  selectedCuisine,
  selectedCookingTime,
  allergy,
  message }) {
    const [windowWidth, setWindowWidth] = useState(
      typeof window !== "undefined" ? window.innerWidth : 1024
    );
    const navigate = useNavigate();
    const normalizedRecipe = normalizeRecipe(recipe);

    useEffect(() => {
      const handleResize = () => setWindowWidth(window.innerWidth);
      window.addEventListener("resize", handleResize);
      return () => window.removeEventListener("resize", handleResize);
    }, []);
    
  const cardStyle = {
    ...styles.card,
    minWidth: windowWidth < 640 ? "85vw" : styles.card.minWidth,
    maxWidth: windowWidth < 640 ? "85vw" : styles.card.maxWidth
  };

  return (
      <div style={cardStyle}>
      <div style={styles.imageContainer}>
        <img src={normalizedRecipe.image} alt="recipe" style={styles.image} />
      </div>

      <div style={styles.content}>
        <div style={styles.row}>
          <div>
            <h4 style={styles.title}>
              {recipe.recipe_name || normalizedRecipe.name}
            </h4>

            <p style={styles.info}>
              {recipe.time || normalizedRecipe.time || "N/A"} •{" "} {recipe.cuisine || normalizedRecipe.cuisine}
            </p>
          </div>

          <button
            style={styles.button}
            onClick={() => {
              if (onView) {
                onView(recipe);
              } else {
                navigate("/recipe-details", {
                  state: {
                    recipe: {
                   ...recipe,
                    type:
                    recipe.type ||
                    (recipe.is_strict ? "strict" : "ai") ||
                    "fallback"
                    },
                     recipes,
                  strictRecipes,
                         ingredients,
                     selectedCategory,
                         selectedCuisine,
                 selectedCookingTime,
                         allergy,
                     message
                  }
                });
              }
            }}
          >
            View Recipe
          </button>
        </div>
      </div>
    </div>
  );
}
const styles = {
  card: {
    minWidth: "220px",
    maxWidth: "320px",
    width: "100%",
    background: "#fff",
    borderRadius: "15px",
    overflow: "hidden",
    flexShrink: 0,
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
  },

  imageContainer: {
    position: "relative"
  },

  image: {
    width: "100%",
    height: "150px",
    objectFit: "cover"
  },

  content: {
    padding: "12px"
  },

  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "10px",
    flexWrap: "wrap"
  },

  title: {
    margin: "0",
    fontSize: "15px"
  },

  info: {
    fontSize: "13px",
    color: "#777",
    marginTop: "6px"
  },

  button: {
    padding: "8px 14px",
    borderRadius: "20px",
    border: "none",
    background: "#f2f2f2",
    cursor: "pointer",
    whiteSpace: "nowrap",
    flexShrink: 0
  }
};

export default RecipeCard;