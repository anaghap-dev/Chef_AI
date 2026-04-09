import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

function RecipeDetails() {
  const location = useLocation();
  const navigate = useNavigate();

  const recipe = location.state?.recipe;
  const previousResults = location.state?.previousResults || [];

  if (!recipe) {
    return (
      <div style={styles.page}>
        <div style={styles.container}>
          <h2 style={styles.errorTitle}>No recipe selected</h2>
          <p style={styles.errorText}>
            Please go back and select a recipe from the suggestions page.
          </p>
          <button
            style={styles.backButton}
            onClick={() => navigate("/")}
          >
            Go Back Home
          </button>
        </div>
      </div>
    );
  }

  const handleBackClick = () => {
  navigate("/", {
    state: {
      preservedRecipes: previousResults
    }
  });
};

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* RECIPE IMAGE */}
        <img
          src={
            recipe.image ||
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
          }
          alt={recipe.recipe_name || "Recipe"}
          style={styles.image}
        />

        {/* MAIN HEADING */}
        <h1 style={styles.mainHeading}>
          {recipe.recipe_name || "Recipe Name"}
        </h1>

        {/* SUBHEADING */}
        <h3 style={styles.subHeading}>
          {recipe.final_recipe_name || recipe["Final recipe name"] || ""}
        </h3>

        {/* CUISINE */}
        <div style={styles.badgeRow}>
          <span style={styles.badge}>
            Cuisine: {recipe.Cuisine || recipe.cuisine || "Unknown"}
          </span>
        </div>

        {/* DETAILED INGREDIENTS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Detailed Ingredients</h2>
          <p style={styles.sectionText}>
            {recipe["Detailed_Ingredients"] ||
              recipe.detailed_ingredients ||
              recipe.detailedIngredients ||
              "No detailed ingredients available."}
          </p>
        </section>

        {/* INSTRUCTIONS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Instructions</h2>
          <p style={styles.sectionText}>
            {recipe.Instructions ||
              recipe.instructions ||
              "No instructions available."}
          </p>
        </section>

        {/* NUTRITION */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Nutrition Information</h2>

          <div style={styles.nutritionGrid}>
            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Calories</h4>
              <p style={styles.nutritionValue}>
                {recipe["Calories (kcal)"] ?? recipe.calories ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Carbohydrates</h4>
              <p style={styles.nutritionValue}>
                {recipe["Carbohydrates g"] ?? recipe.carbohydrates ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Protein</h4>
              <p style={styles.nutritionValue}>
                {recipe["Protein g"] ?? recipe.protein ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Fats</h4>
              <p style={styles.nutritionValue}>
                {recipe["Fats g"] ?? recipe.fats ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Free Sugar</h4>
              <p style={styles.nutritionValue}>
                {recipe["Free Sugar g"] ?? recipe.free_sugar ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Fibre</h4>
              <p style={styles.nutritionValue}>
                {recipe["Fibre g"] ?? recipe.fibre ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Sodium</h4>
              <p style={styles.nutritionValue}>
                {recipe["Sodium mg"] ?? recipe.sodium ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Calcium</h4>
              <p style={styles.nutritionValue}>
                {recipe["Calcium mg"] ?? recipe.calcium ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Iron</h4>
              <p style={styles.nutritionValue}>
                {recipe["Iron mg"] ?? recipe.iron ?? "N/A"}
              </p>
            </div>
          </div>
        </section>

        <button
          style={styles.backButton}
          onClick={handleBackClick}
        >
          ← Back to Home Page
        </button>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f8fafc",
    padding: "30px 20px"
  },
  container: {
    maxWidth: "1000px",
    margin: "0 auto",
    backgroundColor: "#ffffff",
    borderRadius: "20px",
    padding: "30px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.08)"
  },
  image: {
    width: "100%",
    height: "380px",
    objectFit: "cover",
    borderRadius: "18px",
    marginBottom: "24px"
  },
  mainHeading: {
    fontSize: "2.4rem",
    fontWeight: "800",
    marginBottom: "8px",
    color: "#111827"
  },
  subHeading: {
    fontSize: "1.1rem",
    fontWeight: "500",
    color: "#9ca3af",
    marginBottom: "20px"
  },
  badgeRow: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
    marginBottom: "28px"
  },
  badge: {
    backgroundColor: "#f3f4f6",
    color: "#374151",
    padding: "8px 14px",
    borderRadius: "999px",
    fontSize: "14px",
    fontWeight: "600"
  },
  section: {
    marginBottom: "30px"
  },
  sectionTitle: {
    fontSize: "1.5rem",
    fontWeight: "700",
    marginBottom: "12px",
    color: "#111827"
  },
  sectionText: {
    fontSize: "1rem",
    lineHeight: "1.8",
    color: "#374151",
    whiteSpace: "pre-line"
  },
  nutritionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginTop: "15px"
  },
  nutritionCard: {
    backgroundColor: "#f9fafb",
    border: "1px solid #e5e7eb",
    borderRadius: "16px",
    padding: "16px"
  },
  nutritionTitle: {
    fontSize: "0.95rem",
    color: "#6b7280",
    marginBottom: "8px",
    fontWeight: "600"
  },
  nutritionValue: {
    fontSize: "1.2rem",
    fontWeight: "700",
    color: "#111827"
  },
  backButton: {
    marginTop: "20px",
    padding: "12px 18px",
    border: "none",
    borderRadius: "12px",
    backgroundColor: "#111827",
    color: "#ffffff",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer"
  },
  errorTitle: {
    fontSize: "2rem",
    fontWeight: "700",
    marginBottom: "10px"
  },
  errorText: {
    fontSize: "1rem",
    color: "#6b7280",
    marginBottom: "20px"
  }
};

export default RecipeDetails;