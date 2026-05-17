import RecipeCard from "./RecipeCard";

function SuggestedRecipes({ recipes = [], 
  strictRecipes = null,
  ingredients,
  selectedCategory,
  selectedCuisine,
  selectedCookingTime,
  allergy,
  message}) {
  return (
    <div style={styles.container}>
      <h3>Suggested for you</h3>

      <div style={styles.scrollWrapper}>
        <div style={styles.row}>
          {recipes.map((recipe, index) => (
            <RecipeCard
              key={recipe.recipe_name || index}
              recipe={recipe}
              index={index}
              recipes={recipes}
              strictRecipes={strictRecipes}
              ingredients={ingredients}
              selectedCategory={selectedCategory}
              selectedCuisine={selectedCuisine}
              selectedCookingTime={selectedCookingTime}
              allergy={allergy}
              message={message}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "20px",
    width: "100%",
    maxWidth: "100vw",
    overflow: "hidden"
  },

  scrollWrapper: {
    width: "100%",
    overflowX: "auto",
    overflowY: "hidden",
    whiteSpace: "nowrap",
    scrollbarWidth: "none"
  },

  row: {
    display: "inline-flex", // IMPORTANT
    gap: "15px",
    paddingTop: "10px"
  }
};

export default SuggestedRecipes;