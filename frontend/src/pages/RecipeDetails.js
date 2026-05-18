import { useEffect, useState } from "react";
import { supabase } from "./supabaseClient";
import { useLocation, useNavigate } from "react-router-dom";
import { normalizeRecipe } from "../utils/normalizeRecipe";
import SubstitutesModal from "../components/SubstitutesModal";

function RecipeDetails() {
  const location = useLocation();
  const navigate = useNavigate();
  const recipe = location.state?.recipe;
  const recipeType = recipe?.type || recipe?.match_type;
  const isStrict = recipeType === "strict";
  const recipeName = recipe?.recipe_name;
  const [fullRecipe, setFullRecipe] = useState(null);
  const [isSaved, setIsSaved] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
 

  const normalizedRecipe = normalizeRecipe(recipe, fullRecipe || {});
   console.log("RECIPE:", recipe);
console.log("FULL RECIPE:", fullRecipe);
console.log("NORMALIZED:", normalizedRecipe);

  useEffect(() => {
  const fetchRecipe = async () => {
    // ONLY strict recipes exist in Supabase
    if (!isStrict || !recipeName) {
      setFullRecipe(recipe);
      return;
    }

    const { data, error } = await supabase
      .from("recipes")
      .select("*")
      .eq("recipe_name", recipeName)
      .maybeSingle();

    if (error) {
      console.log("Supabase error:", error.message);
      setFullRecipe(recipe);
      return;
    }

    setFullRecipe(data || recipe);
  };

  fetchRecipe();
}, [isStrict, recipeName, recipe]);

  useEffect(() => {
    const checkSaved = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user || !fullRecipe) return;

      const { data, error } = await supabase
        .from("saved_recipes")
        .select("*")
        .eq("user_id", user.id)
        .eq("recipe_name", recipeName);

      if (error) return console.log(error.message);

      setIsSaved(data?.length > 0);
    };

    checkSaved();
  }, [recipe, isStrict, recipeName, fullRecipe]);

  const handleAddMissing = (e) => {
  if (!e.target.checked) return;

  const userIngredients = (
    location.state?.ingredients || ""
  )
    .split(",")
    .map((i) => i.trim().toLowerCase());

  const recipeIngredients =
    normalizedRecipe.ingredientsList?.length
      ? normalizedRecipe.ingredientsList
      : normalizedRecipe.detailedIngredients
          ?.split(",")
          .map((i) => i.trim()) || [];

  const missing = recipeIngredients.filter(
    (item) =>
      !userIngredients.includes(
        item.toLowerCase().trim()
      )
  );

  if (missing.length === 0) {
    setPopupMessage("You already have all ingredients!");
    setShowPopup(true);
    return;
  }

  const newItems = missing.map((item) => ({
    name: item,
    qty: ""
  }));

  const existing =
    JSON.parse(localStorage.getItem("groceryItems")) || [];

  localStorage.setItem(
  "groceryItems",
  JSON.stringify(
    [...existing, ...newItems].filter(
      (item, index, self) =>
        index ===
        self.findIndex(
          (t) =>
            t.name.toLowerCase().trim() ===
            item.name.toLowerCase().trim()
        )
    )
  )
);
  

  setPopupMessage(
    "Missing ingredients added to grocery cart!"
  );

  setShowPopup(true);
};
  const handleSaveFavorite = () => {
    setIsFavorite((prev) => !prev);
  };



  const handleBackClick = () => {
    const backState = { fromDetails: true };

    if (location.state) {
      if (Object.prototype.hasOwnProperty.call(location.state, "recipes")) {
        backState.recipes = location.state.recipes;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "strictRecipes")) {
        backState.strictRecipes = location.state.strictRecipes;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "ingredients")) {
        backState.ingredients = location.state.ingredients;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "selectedCuisine")) {
        backState.selectedCuisine = location.state.selectedCuisine;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "selectedCategory")) {
        backState.selectedCategory = location.state.selectedCategory;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "selectedCookingTime")) {
        backState.selectedCookingTime = location.state.selectedCookingTime;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "allergy")) {
        backState.allergy = location.state.allergy;
      }
      if (Object.prototype.hasOwnProperty.call(location.state, "message")) {
        backState.message = location.state.message;
      }
    }

    navigate("/", { state: backState });
  };

  const handleSaveRecipe = async () => {
    console.log("CLICKED SAVE BUTTON");

    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      setPopupMessage("Please login to save recipes");
      setShowPopup(true);
      return;
    }

    try {
      if (isSaved) {
        const { error } = await supabase
          .from("saved_recipes")
          .delete()
          .eq("user_id", user.id)
          .eq("recipe_name", recipeName);

        if (error) throw error;

        setIsSaved(false);
        setPopupMessage("Removed from saved");
        setShowPopup(true);
        return;
      }

      const { error } = await supabase
        .from("saved_recipes")
        .insert([
          {
            user_id: user.id,
            recipe_name: normalizedRecipe.name
          }
        ]);

      if (error) throw error;

      setIsSaved(true);
      setPopupMessage("Recipe saved ❤️");
      setShowPopup(true);
    } catch (err) {
      console.log("FULL ERROR:", err);
      setPopupMessage(err.message);
      setShowPopup(true);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* RECIPE IMAGE */}
        <img
          src={
            normalizeRecipe?.image ||
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
          }
          alt={normalizedRecipe.name || "Recipe"}
          style={styles.image}
        />

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <h1 style={styles.mainHeading}>
            {normalizedRecipe.name || recipe?.recipe_name || "Recipe Name"}
          </h1>
          <button
            style={{
              ...styles.saveButton,
              backgroundColor: isSaved ? "#ef4444" : "#fa1515",
              color: isSaved ? "#fff" : "#111"
            }}
            onClick={handleSaveRecipe}
          >
            {isSaved ? "❤️ Saved" : "Save Recipe"}
          </button>
          <span onClick={handleSaveFavorite} style={{ fontSize: "26px", cursor: "pointer" }}>
            {isFavorite ? "❤️" : "🤍"}
          </span>
        </div>

        {/* SUBHEADING */}
        <h3 style={styles.subHeading}>
          {normalizedRecipe.name || ""}
        </h3>

        {/* CUISINE */}
        <div style={styles.badgeRow}>
          <span style={styles.badge}>
            Cuisine: {normalizedRecipe.cuisine || "Unknown"}
          </span>
        </div>

        {/* DETAILED INGREDIENTS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Detailed Ingredients</h2>
          <p style={styles.sectionText}>
            { normalizedRecipe.detailedIngredients ||
              "No detailed ingredients available."}
          </p>
 <SubstitutesModal
  ingredients={
    (fullRecipe?.ingredients ||
      fullRecipe?.ingredient_list ||
      fullRecipe?.ingredientsList ||
      "")
      .toString()
      .split(",")
      .map(i => i.trim())
      .filter(Boolean)
    }
/>
        </section>

        <label style={{ display: "flex", gap: "10px", alignItems: "center", marginTop: "10px",marginBottom: "20px" }}>
  <input type="checkbox" onChange={handleAddMissing} />
  Add missing ingredients to grocery cart
</label>

        {/* INSTRUCTIONS */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Instructions</h2>
          <p style={styles.sectionText}>
            {normalizedRecipe.instructions ||
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
                { normalizedRecipe.calories ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Carbohydrates</h4>
              <p style={styles.nutritionValue}>
                { normalizedRecipe.carbs ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Protein</h4>
              <p style={styles.nutritionValue}>
                { normalizedRecipe.protein ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Fats</h4>
              <p style={styles.nutritionValue}>
                {normalizedRecipe.fats ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Free Sugar</h4>
              <p style={styles.nutritionValue}>
                { normalizedRecipe.sugar ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Fibre</h4>
              <p style={styles.nutritionValue}>
                {normalizedRecipe.fibre ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Sodium</h4>
              <p style={styles.nutritionValue}>
                {normalizedRecipe.sodium ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Calcium</h4>
              <p style={styles.nutritionValue}>
                { normalizedRecipe.calcium ?? "N/A"}
              </p>
            </div>

            <div style={styles.nutritionCard}>
              <h4 style={styles.nutritionTitle}>Iron</h4>
              <p style={styles.nutritionValue}>
                {normalizedRecipe.iron ?? "N/A"}
              </p>
            </div>
          </div>
        </section>

        <button
  style={{
    marginTop: "15px",
    marginRight: "10px",
    padding: "12px 18px",
    border: "none",
    borderRadius: "12px",
    backgroundColor: "#f97316",
    color: "#fff",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer"
  }}
  onClick={() => navigate("/grocerycart",{
    state: {fromRecipe:true,recipe}
  })}
>
  🛒 View Grocery Cart
</button>
        <button
          style={styles.backButton}
          onClick={handleBackClick}
        >
          ← Back to Home Page
        </button>
        {showPopup && (
          <div style={styles.overlay}>
            <div style={styles.popup}>
              <p style={styles.popupText}>
                {popupMessage}
              </p>

              <button
                style={styles.popupButton}
                onClick={() => setShowPopup(false)}
              >
                OK
              </button>
            </div>
          </div>
        )}
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
  },
  overlay: {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 999
},

popup: {
  backgroundColor: "#fff",
  padding: "25px 30px",
  borderRadius: "15px",
  textAlign: "center",
  boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
  maxWidth: "300px"
},

popupText: {
  fontSize: "16px",
  marginBottom: "20px",
  color: "#111"
},

popupButton: {
  padding: "10px 18px",
  borderRadius: "10px",
  border: "none",
  backgroundColor: "#111827",
  color: "#fff",
  cursor: "pointer",
  fontWeight: "600"
}
};

export default RecipeDetails;