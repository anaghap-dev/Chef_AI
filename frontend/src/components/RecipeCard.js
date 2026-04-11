import { useNavigate } from "react-router-dom";

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
    const navigate = useNavigate();

    
  return (
    <div style={styles.card}>
      <div style={styles.imageContainer}>
        <img src={recipe.image} alt="recipe" style={styles.image} />
      </div>

      <div style={styles.content}>
        <div style={styles.row}>
          <div>
            <h4 style={styles.title}>
              {recipe.recipe_name}
            </h4>

            <p style={styles.info}>
              {recipe.time} • {recipe.cuisine}
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
                    recipe,
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
    minWidth: "260px",
    background: "#fff",
    borderRadius: "15px",
    overflow: "hidden",
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
  },

  imageContainer: {
    position: "relative"
  },

  image: {
    width: "100%",
    height: "130px",
    objectFit: "cover"
  },

  content: {
    padding: "12px"
  },

  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "10px"
  },

  title: {
    margin: "0",
    fontSize: "16px"
  },

  info: {
    fontSize: "13px",
    color: "#777",
    marginTop: "4px"
  },

  button: {
    padding: "8px 14px",
    borderRadius: "20px",
    border: "none",
    background: "#f2f2f2",
    cursor: "pointer",
    whiteSpace: "nowrap"
  }
};

export default RecipeCard;