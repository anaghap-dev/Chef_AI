import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import warnings
from typing import Any, Optional

warnings.filterwarnings("ignore")

# =========================
# CONFIG
# =========================
MODEL_PATH = "models/recipe_matcher_prod.pkl"
VECTORIZER_PATH = "models/vectorizer_prod.pkl"
DATA_PATH = "data/recipes.csv"

# =========================
# GLOBALS
# =========================
# Dataframe and vectorizer are loaded at runtime, but may be None before initialization.
df: Optional[pd.DataFrame] = None
vectorizer: Optional[TfidfVectorizer] = None
model_loaded: bool = False


# =========================
# HELPERS
# =========================

# =========================
# INGREDIENT NORMALIZATION MAP
# =========================
ingredient_map = {
    "cloves garlic": "garlic",
    "garlic paste": "garlic",
    "ginger garlic paste": "ginger garlic",

    "spring onion": "onion",
    "spring onion greens": "onion",
    "pearl onion": "onion",
    "onion paste": "onion",

    "green chillies": "chilli",
    "dry red chilli": "chilli",
    "red chilli powder": "chilli",

    "coriander leaves": "coriander",
    "coriander seeds": "coriander",
    "coriander powder": "coriander",
    "coriander dhania leaves": "coriander",

    "cumin seeds": "cumin",
    "cumin powder": "cumin",

    "paneer cubes": "paneer",
    "chicken breasts": "chicken",

    "basmati rice": "rice",
    "idli rice": "rice",

    "hung curd": "curd",
    "yogurt": "curd",

    "green bell pepper": "capsicum",
    "red bell pepper": "capsicum",

    "spinach leaves": "spinach",
    "potato aloo": "potato"
}

def safe_str(value: Any) -> str:
    """Convert any value safely to string."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def clean_text(text: Any) -> str:
    """Clean and normalize text for matching."""
    text = safe_str(text).lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)   # keep only letters + spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_ingredients(text):
    text = clean_text(text)

    # Sort keys by length (longest first)
    sorted_keys = sorted(ingredient_map.keys(), key=len, reverse=True)

    for key in sorted_keys:
        if key in text:
            text = text.replace(key, ingredient_map[key])

    return text


def get_column_name(possible_names: list[str]) -> Optional[str]:
    """
    Return first matching column name from df.
    Helps support different CSV header variations.
    """
    global df
    if df is None:
        return None
    for col in possible_names:
        if col in df.columns:
            return col
    return None


def get_value_from_row(row: pd.Series, possible_names: list[str], default: Any = "") -> Any:
    """Get first available value from row using multiple possible column names."""
    for col in possible_names:
        if col in row.index:
            return row[col]
    return default


def get_ingredient_tokens(text):
    """Tokenize cleaned ingredient text."""
    cleaned = clean_ingredients(text)
    return set(cleaned.split()) if cleaned else set()


def normalize_dataframe() -> None:
    """Normalize dataset columns to the standardized internal names."""
    global df

    if df is None:
        return

    recipe_name_col = get_column_name(["recipe_name", "Recipe Name", "recipe"])
    ingredients_col = get_column_name(["ingredients", "Ingredients"])
    cuisine_col = get_column_name(["Cuisine", "cuisine"])
    category_col = get_column_name(["Category", "category"])
    cooking_col = get_column_name(["CookingTime", "Cooking Time", "cooking_time"])
    calories_col = get_column_name(["Calories (kcal)", "Calories", "calories"])
    final_recipe_col = get_column_name(["final_recipe_name", "Final recipe name", "Final Recipe Name"])

    if recipe_name_col is None:
        df["recipe_name"] = ""
    elif recipe_name_col != "recipe_name":
        df["recipe_name"] = df[recipe_name_col]

    if ingredients_col is None:
        df["ingredients"] = ""
    elif ingredients_col != "ingredients":
        df["ingredients"] = df[ingredients_col]

    if cuisine_col is None:
        df["Cuisine"] = ""
    elif cuisine_col != "Cuisine":
        df["Cuisine"] = df[cuisine_col]

    if category_col is None:
        df["Category"] = ""
    elif category_col != "Category":
        df["Category"] = df[category_col]

    if cooking_col is None:
        df["CookingTime"] = np.nan
    elif cooking_col != "CookingTime":
        df["CookingTime"] = df[cooking_col]

    if calories_col is None:
        df["Calories (kcal)"] = np.nan
    elif calories_col != "Calories (kcal)":
        df["Calories (kcal)"] = df[calories_col]

    if final_recipe_col is None:
        df["final_recipe_name"] = ""
    elif final_recipe_col != "final_recipe_name":
        df["final_recipe_name"] = df[final_recipe_col]

    instructions_col = get_column_name(["instructions", "Instructions", "RecipeInstructions", "Method", "Directions"])
    detailed_ingredients_col = get_column_name([
        "Detailed_Ingredients", "Detailed Ingredients", "Detailed _Ingredients",
        "Detailed ingredients", "Detailed_ingredients"
    ])
    carbohydrates_col = get_column_name(["Carbohydrates g", "Carbohydrates (g)", "Carbohydrates"])
    protein_col = get_column_name(["Protein g", "Protein (g)", "Protein"])
    fats_col = get_column_name(["Fats g", "Fats (g)", "Fats"])
    free_sugar_col = get_column_name(["Free Sugar g", "Free Sugar (g)", "Free Sugar"])
    fibre_col = get_column_name(["Fibre g", "Fibre (g)", "Fibre"])
    sodium_col = get_column_name(["Sodium mg", "Sodium (mg)", "Sodium"])
    calcium_col = get_column_name(["Calcium mg", "Calcium (mg)", "Calcium"])
    iron_col = get_column_name(["Iron mg", "Iron (mg)", "Iron"])

    if instructions_col is None:
        df["Instructions"] = ""
    elif instructions_col != "Instructions":
        df["Instructions"] = df[instructions_col]

    if detailed_ingredients_col is None:
        df["Detailed_Ingredients"] = ""
    elif detailed_ingredients_col != "Detailed_Ingredients":
        df["Detailed_Ingredients"] = df[detailed_ingredients_col]

    if carbohydrates_col is None:
        df["Carbohydrates g"] = np.nan
    elif carbohydrates_col != "Carbohydrates g":
        df["Carbohydrates g"] = df[carbohydrates_col]

    if protein_col is None:
        df["Protein g"] = np.nan
    elif protein_col != "Protein g":
        df["Protein g"] = df[protein_col]

    if fats_col is None:
        df["Fats g"] = np.nan
    elif fats_col != "Fats g":
        df["Fats g"] = df[fats_col]

    if free_sugar_col is None:
        df["Free Sugar g"] = np.nan
    elif free_sugar_col != "Free Sugar g":
        df["Free Sugar g"] = df[free_sugar_col]

    if fibre_col is None:
        df["Fibre g"] = np.nan
    elif fibre_col != "Fibre g":
        df["Fibre g"] = df[fibre_col]

    if sodium_col is None:
        df["Sodium mg"] = np.nan
    elif sodium_col != "Sodium mg":
        df["Sodium mg"] = df[sodium_col]

    if calcium_col is None:
        df["Calcium mg"] = np.nan
    elif calcium_col != "Calcium mg":
        df["Calcium mg"] = df[calcium_col]

    if iron_col is None:
        df["Iron mg"] = np.nan
    elif iron_col != "Iron mg":
        df["Iron mg"] = df[iron_col]

    # Clean ingredients
    df["ingredients_clean"] = df["ingredients"].fillna("").apply(clean_ingredients)

    # Fill missing text fields
    df["recipe_name"] = df["recipe_name"].fillna("").astype(str)
    df["final_recipe_name"] = df["final_recipe_name"].fillna("").astype(str)
    df["Cuisine"] = df["Cuisine"].fillna("").astype(str)
    df["Category"] = df["Category"].fillna("").astype(str)
    df["Instructions"] = df["Instructions"].fillna("").astype(str)
    df["Detailed_Ingredients"] = df["Detailed_Ingredients"].fillna("").astype(str)

    # Numeric conversions
    df["CookingTime"] = pd.to_numeric(df["CookingTime"], errors="coerce")
    df["Calories (kcal)"] = pd.to_numeric(df["Calories (kcal)"], errors="coerce")
    df["Carbohydrates g"] = pd.to_numeric(df["Carbohydrates g"], errors="coerce")
    df["Protein g"] = pd.to_numeric(df["Protein g"], errors="coerce")
    df["Fats g"] = pd.to_numeric(df["Fats g"], errors="coerce")
    df["Free Sugar g"] = pd.to_numeric(df["Free Sugar g"], errors="coerce")
    df["Fibre g"] = pd.to_numeric(df["Fibre g"], errors="coerce")
    df["Sodium mg"] = pd.to_numeric(df["Sodium mg"], errors="coerce")
    df["Calcium mg"] = pd.to_numeric(df["Calcium mg"], errors="coerce")
    df["Iron mg"] = pd.to_numeric(df["Iron mg"], errors="coerce")



def is_nonveg(category_value):
    """Check if category means non-veg."""
    c = safe_str(category_value).lower()
    return c in ["non veg", "non-veg", "nonveg", "nv", "chicken", "meat", "egg", "fish"]


def is_veg(category_value):
    """Check if category means veg."""
    c = safe_str(category_value).lower()
    return c in ["veg", "vegetarian", "v"]


def make_json_safe(recipe_dict):
    """Convert all values to Flask JSON-safe Python native types."""
    def safe_number(key):
        value = recipe_dict.get(key)
        if value is None or pd.isna(value):
            return None
        return float(value)

    return {
        "rank": int(recipe_dict["rank"]) if recipe_dict.get("rank") is not None else None,
        "recipe_name": str(recipe_dict.get("recipe_name", "")),
        "final_recipe_name": str(recipe_dict.get("final_recipe_name", "")),
        "ingredients": str(recipe_dict.get("ingredients", "")),
        "Instructions": str(recipe_dict.get("Instructions", "")),
        "Detailed_Ingredients": str(recipe_dict.get("Detailed_Ingredients", "")),
        "Cuisine": str(recipe_dict.get("Cuisine", "")),
        "Category": str(recipe_dict.get("Category", "")),
        "CookingTime": int(recipe_dict["CookingTime"]) if recipe_dict.get("CookingTime") is not None else None,
        "Calories (kcal)": safe_number("Calories (kcal)"),
        "Carbohydrates g": safe_number("Carbohydrates g"),
        "Protein g": safe_number("Protein g"),
        "Fats g": safe_number("Fats g"),
        "Free Sugar g": safe_number("Free Sugar g"),
        "Fibre g": safe_number("Fibre g"),
        "Sodium mg": safe_number("Sodium mg"),
        "Calcium mg": safe_number("Calcium mg"),
        "Iron mg": safe_number("Iron mg"),
        "similarity_score": float(recipe_dict["similarity_score"]) if recipe_dict.get("similarity_score") is not None else None,
        "ingredient_match": str(recipe_dict.get("ingredient_match", "")),
        "match_type": str(recipe_dict.get("match_type", "")),
    }


# =========================
# MODEL INIT
# =========================
def initialize_model():
    """
    Load saved dataframe + vectorizer if available,
    otherwise train and save them.
    """
    global df, vectorizer, model_loaded

    try:
        #try loading
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            print("[MODEL] Loading existing trained model...")
            with open(MODEL_PATH, "rb") as f:
                df = pickle.load(f)
            with open(VECTORIZER_PATH, "rb") as f:
                vectorizer = pickle.load(f)
            normalize_dataframe()
            model_loaded = True
            assert df is not None
            print(f"[MODEL] Loaded {len(df)} recipes from saved model")
            return
    except Exception as e:
        print(f"[WARNING] Could not load saved model: {e}")

    print("[MODEL] Training new TF-IDF recipe matcher...")

    # Load CSV
    df = pd.read_csv(DATA_PATH)

    normalize_dataframe()

    # Train TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )

    assert df is not None
    vectorizer.fit(df["ingredients_clean"])

    # Save model
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(df, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    model_loaded = True
    print(f"[MODEL] Model trained and saved with {len(df)} recipes")


# =========================
# SCORING
# =========================
def calculate_scores(user_vector, user_tokens, cuisine_filter=None, category_filter=None):
    """
    Composite score:
    - TF-IDF cosine similarity = 70%
    - token overlap = 30%
    Optional small bonuses for cuisine/category matches.
    """
    global df, vectorizer
    if df is None or vectorizer is None:
        raise RuntimeError("Recipe matcher is not initialized")

    # Transform all recipe ingredient vectors
    all_vectors = vectorizer.transform(df["ingredients_clean"])
    tfidf_scores = cosine_similarity(user_vector, all_vectors).flatten()

    # Token overlap
    token_scores = []
    for ing in df["ingredients_clean"]:
        recipe_tokens = get_ingredient_tokens(ing)
        if len(user_tokens) > 0:
            overlap = len(user_tokens & recipe_tokens) / len(user_tokens)
        else:
            overlap = 0.0
        token_scores.append(overlap)

    token_scores = np.array(token_scores)

    # Bonuses
    cuisine_bonus = np.zeros(len(df))
    if cuisine_filter:
        cuisine_filter = safe_str(cuisine_filter).lower()
        for i, c in enumerate(df["Cuisine"]):
            if cuisine_filter and cuisine_filter in safe_str(c).lower():
                cuisine_bonus[i] = 0.10

    category_bonus = np.zeros(len(df))
    if category_filter:
        category_filter = safe_str(category_filter).lower()
        for i, c in enumerate(df["Category"]):
            cat = safe_str(c).lower()
            if category_filter in cat:
                category_bonus[i] = 0.10

    # Final score
    composite_scores = (0.7 * tfidf_scores) + (0.3 * token_scores) + cuisine_bonus + category_bonus

    return composite_scores, tfidf_scores, token_scores


# =========================
# FILTERS
# =========================
def apply_optional_filters(results, category=None, allergies=None, max_cooking_time=None):
    """
    Apply optional filters after similarity ranking.
    Filters are optional. If not given, system still works normally.
    """
    filtered = results

    # Category filter
    if category:
        category_lower = safe_str(category).lower()

        if category_lower in ["veg", "vegetarian", "v"]:
            filtered = [
                r for r in filtered
                if is_veg(r.get("Category", ""))
            ]

        elif category_lower in ["non veg", "non-veg", "nonveg", "nv"]:
            filtered = [
                r for r in filtered
                if is_nonveg(r.get("Category", ""))
            ]

        else:
            filtered = [
                r for r in filtered
                if category_lower in safe_str(r.get("Category", "")).lower()
            ]

    # Allergy filter (exclude recipes containing allergy words in ingredients)
    if allergies:
        if isinstance(allergies, str):
            allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
        elif isinstance(allergies, list):
            allergy_list = [safe_str(a).lower() for a in allergies if safe_str(a)]
        else:
            allergy_list = []

        if allergy_list:
            temp = []
            for r in filtered:
                ing = safe_str(r.get("ingredients", "")).lower()
                blocked = False
                for allergy in allergy_list:
                    if allergy in ing:
                        blocked = True
                        break
                if not blocked:
                    temp.append(r)
            filtered = temp

    # Cooking time filter
    if max_cooking_time is not None:
        try:
            max_cooking_time = int(max_cooking_time)
            filtered = [
                r for r in filtered
                if r.get("CookingTime") is not None and int(r.get("CookingTime")) <= max_cooking_time
            ]
        except:
            pass

    # Re-rank after filtering
    for i, r in enumerate(filtered, start=1):
        r["rank"] = i

    return filtered


# =========================
# MAIN API FUNCTION
# =========================
def recommend_recipes(user_input, cuisine=None, category=None, allergies=None, cooking_time=None, top_k=5):
    """
    Recommend recipes using TF-IDF + cosine similarity + token overlap.
    Optional filters:
      - cuisine
      - category
      - allergies
      - cooking_time (max)
    Works even if filters are not provided.
    """
    global df, vectorizer, model_loaded

    if not model_loaded:
        initialize_model()
    if df is None or vectorizer is None:
        raise RuntimeError("Recipe matcher initialization failed")

    # Clean user input
    user_input_clean = clean_ingredients(user_input)
    user_tokens = get_ingredient_tokens(user_input_clean)

    # If empty input, return empty list
    if not user_input_clean:
        return []

    # Vectorize user input
    user_vector = vectorizer.transform([user_input_clean])

    # Score all recipes
    composite_scores, tfidf_scores, token_scores = calculate_scores(
        user_vector=user_vector,
        user_tokens=user_tokens,
        cuisine_filter=cuisine,
        category_filter=category
    )

    # Get larger pool first so filters can still work
    candidate_k = min(max(top_k * 5, 20), len(df))
    top_indices = composite_scores.argsort()[-candidate_k:][::-1]

    # Build candidate results
    results = []
    for idx in top_indices:
        recipe = df.iloc[idx]

        score = float(composite_scores[idx])
        token_match = float(token_scores[idx])

        result = {
            "rank": 0,  # temporary, will set later
            "recipe_name": safe_str(recipe.get("recipe_name", "")),
            "final_recipe_name": safe_str(
                recipe.get("final_recipe_name", "")
            ),
            "ingredients": safe_str(recipe.get("ingredients", "")),
            "Instructions": safe_str(recipe.get("Instructions", "")),
            "Detailed_Ingredients": safe_str(recipe.get("Detailed_Ingredients", "")),
            "Cuisine": safe_str(recipe.get("Cuisine", "")),
            "Category": safe_str(recipe.get("Category", "")),
            "CookingTime": int(recipe["CookingTime"]) if pd.notna(recipe["CookingTime"]) else None,
            "Calories (kcal)": float(recipe["Calories (kcal)"]) if pd.notna(recipe["Calories (kcal)"]) else None,
            "Carbohydrates g": float(recipe["Carbohydrates g"]) if pd.notna(recipe["Carbohydrates g"]) else None,
            "Protein g": float(recipe["Protein g"]) if pd.notna(recipe["Protein g"]) else None,
            "Fats g": float(recipe["Fats g"]) if pd.notna(recipe["Fats g"]) else None,
            "Free Sugar g": float(recipe["Free Sugar g"]) if pd.notna(recipe["Free Sugar g"]) else None,
            "Fibre g": float(recipe["Fibre g"]) if pd.notna(recipe["Fibre g"]) else None,
            "Sodium mg": float(recipe["Sodium mg"]) if pd.notna(recipe["Sodium mg"]) else None,
            "Calcium mg": float(recipe["Calcium mg"]) if pd.notna(recipe["Calcium mg"]) else None,
            "Iron mg": float(recipe["Iron mg"]) if pd.notna(recipe["Iron mg"]) else None,
            "similarity_score": score,
            "ingredient_match": f"{token_match:.1%}",
            "match_type": (
                "Excellent Match" if score >= 0.85 else
                "Good Match" if score >= 0.60 else
                "Partial Match"
            )
        }

        results.append(result)

    # Apply optional filters
    results = apply_optional_filters(
        results,
        category=category,
        allergies=allergies,
        max_cooking_time=cooking_time
    )

    # If filters removed everything, fallback to top_k original results
    if len(results) == 0:
        fallback = []
        for idx in top_indices[:top_k]:
            recipe = df.iloc[idx]
            score = float(composite_scores[idx])
            token_match = float(token_scores[idx])

            fallback.append({
                "rank": 0,
                "recipe_name": safe_str(recipe.get("recipe_name", "")),
                "final_recipe_name": safe_str(recipe.get("final_recipe_name", "")),
                "ingredients": safe_str(recipe.get("ingredients", "")),
                "Instructions": safe_str(recipe.get("Instructions", "")),
                "Detailed_Ingredients": safe_str(recipe.get("Detailed_Ingredients", "")),
                "Cuisine": safe_str(recipe.get("Cuisine", "")),
                "Category": safe_str(recipe.get("Category", "")),
                "CookingTime": int(recipe["CookingTime"]) if pd.notna(recipe["CookingTime"]) else None,
                "Calories (kcal)": float(recipe["Calories (kcal)"]) if pd.notna(recipe["Calories (kcal)"]) else None,
                "Carbohydrates g": float(recipe["Carbohydrates g"]) if pd.notna(recipe["Carbohydrates g"]) else None,
                "Protein g": float(recipe["Protein g"]) if pd.notna(recipe["Protein g"]) else None,
                "Fats g": float(recipe["Fats g"]) if pd.notna(recipe["Fats g"]) else None,
                "Free Sugar g": float(recipe["Free Sugar g"]) if pd.notna(recipe["Free Sugar g"]) else None,
                "Fibre g": float(recipe["Fibre g"]) if pd.notna(recipe["Fibre g"]) else None,
                "Sodium mg": float(recipe["Sodium mg"]) if pd.notna(recipe["Sodium mg"]) else None,
                "Calcium mg": float(recipe["Calcium mg"]) if pd.notna(recipe["Calcium mg"]) else None,
                "Iron mg": float(recipe["Iron mg"]) if pd.notna(recipe["Iron mg"]) else None,
                "similarity_score": score,
                "ingredient_match": f"{token_match:.1%}",
                "match_type": (
                    "Excellent Match" if score >= 0.85 else
                    "Good Match" if score >= 0.60 else
                    "Partial Match"
                )
            })

        results = fallback

    # Final top-k
    results = results[:top_k]

    # Re-rank
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    # Make JSON-safe
    results = [make_json_safe(r) for r in results]

    return results


# =========================
# INIT ON IMPORT
# =========================
print("[INIT] Initializing recipe matcher...")
initialize_model()
print("[INIT] Recipe matcher ready!")