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
MODEL_VERSION = "v2"
MODEL_PATH = f"models/recipe_matcher_{MODEL_VERSION}.pkl"
VECTORIZER_PATH = f"models/vectorizer_{MODEL_VERSION}.pkl"
DATA_PATH = "data/recipes.csv"

# =========================
# GLOBALS
# =========================
# Dataframe and vectorizer are loaded at runtime, but may be None before initialization.
df: Optional[pd.DataFrame] = None
vectorizer: Optional[TfidfVectorizer] = None
model_loaded: bool = False
recipe_vectors = None

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

    "chilli": "chilli",
    "chili": "chilli",
    "chilies": "chilli",
    "green chili": "chilli",
    "green chillies": "chilli",
    "red chilli powder": "chilli powder",

    "coriander leaves": "coriander",
    "coriander seeds": "coriander",
    "coriander powder": "coriander",
    "coriander dhania leaves": "coriander",
    "coriander": "cilantro",

    "cumin seeds": "cumin",
    "cumin powder": "cumin",

    "paneer cubes": "paneer",
    "paneer": "cottage cheese",

    "basmati rice": "rice",
    "idli rice": "rice",

    "hung curd": "curd",
    "yogurt": "curd",
    "yoghurt": "curd",
    "curd": "yogurt",

    "green bell pepper": "capsicum",
    "red bell pepper": "capsicum",
    "bell pepper": "capsicum",
    "yellow bell pepper": "capsicum",
    "capsicum": "bell pepper",

    "spinach leaves": "spinach",
    "potato aloo": "potato",

    # CORN
    "sweet corn": "corn",
    "corn kernels": "corn",
    "baby corn": "corn",
    "corn meal": "cornmeal",
    "corn flour": "cornflour",

    "chicken breasts": "chicken",
    "chicken breast": "chicken",
    "breast": "chicken",

    # SPINACH
    "baby spinach": "spinach",
    "spinach leaves": "spinach",
    "palak": "spinach",}

STOPWORDS = {
    "fresh",
    "or",
    "kernels",
    "slices",
    "chopped",
    "powder",
    "cups",
    "cup",
    "tablespoon",
    "teaspoon",
    "taste",
    "required",
    "cooking",
    "cooked",
    "seeds",
    "powder",
    "leaves",
    # quantities
    "cup", "cups",
    "tbsp", "tablespoon", "tablespoons",
    "tsp", "teaspoon", "teaspoons",
    "oz", "ounce", "ounces",
    "ml", "l", "gram", "grams",
    "kg", "g",

    # size descriptors
    "small", "medium", "large",

    # cooking descriptors
    "chopped", "minced", "grated", "sliced", "diced",
    "crushed", "peeled", "cooked", "uncooked", "ripe",

    # filler words
    "fresh", "plain", "optional", "as", "needed", "taste",
    "pinch", 
    "dash",
    "chilli",
    "savory"
}

def safe_str(value: Any) -> str:
    """Convert any value safely to string."""
    if value is None:
        return ""
    # Check if it's a list or array first
    if isinstance(value, (list, tuple, np.ndarray)):
        return " ".join(map(str, value)).strip() 
    # Now it's safe to check pd.isna for scalar values
    if pd.isna(value):
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


    sorted_keys = sorted(ingredient_map.keys(), key=len, reverse=True)

    for key in sorted_keys:

        replacement = ingredient_map[key]

        pattern = r"\b" + re.escape(key) + r"\b"

        text = re.sub(pattern, replacement, text)

    text = re.sub(r"\s+", " ", text).strip()

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

def get_ingredient_tokens(text):
    """
    Better ingredient tokenizer.
    Removes cooking words and noise.
    """
    cleaned = clean_ingredients(text)
    
    tokens = []

    for token in cleaned.split():
        token = token.strip()
        if len(token) <= 2:
            continue
        if token in STOPWORDS:
            continue
        tokens.append(token)

    return set(tokens)

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
    df["ingredient_tokens"] = df["ingredients_clean"].apply(
    get_ingredient_tokens
)

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



NONVEG_KEYWORDS = {
    "chicken",
    "mutton",
    "meat",
    "fish",
    "egg",
    "prawn",
    "beef",
    "pork",
    "seafood"
}
def is_nonveg(category_value):
    """Check if category means non-veg."""
    c = safe_str(category_value).lower()
    return any(
        word in c
        for word in NONVEG_KEYWORDS
    )

VEG_KEYWORDS = {
    "veg",
    "vegetarian",
    "vegan"
}

def is_veg(category_value):
    """Check if category means veg."""
    c = safe_str(category_value).lower()

    words = set(c.replace("-", " ").split())

    return (
        len(words & VEG_KEYWORDS) > 0
        and not is_nonveg(c)
    )

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

def remove_duplicate_recipes(results):
    """
    Remove duplicate or near-duplicate recipes.
    """

    seen = set()
    unique_results = []

    for recipe in results:

        name = safe_str(
            recipe.get("final_recipe_name")
        ).lower()

        if not name:
            name = safe_str(
                recipe.get("recipe_name")
            ).lower()

        # Normalize
        name = re.sub(r"[^a-z\s]", "", name)
        name = re.sub(r"\s+", " ", name).strip()

        important_words = [
            w for w in name.split()
            if w not in {
               "healthy",
                "easy",
                "simple",
                "creamy",
                "homemade",
                "zesty"
            }
        ]

        simplified = " ".join(important_words[:3])

        if simplified not in seen:
            seen.add(simplified)
            unique_results.append(recipe)

    return unique_results

def diversify_results(results, similarity_threshold=0.75):
    """
    Remove semantically similar recipes.
    Keeps recipe variety in final recommendations.
    """

    diversified = []

    for recipe in results:

        current_name = safe_str(
            recipe.get("final_recipe_name")
        ).lower()

        if not current_name:
            current_name = safe_str(
                recipe.get("recipe_name")
            ).lower()

        current_words = set(
            clean_text(current_name).split()
        )

        is_similar = False

        for existing in diversified:

            existing_name = safe_str(
                existing.get("final_recipe_name")
            ).lower()

            if not existing_name:
                existing_name = safe_str(
                    existing.get("recipe_name")
                ).lower()

            existing_words = set(
                clean_text(existing_name).split()
            )

            # Jaccard similarity
            intersection = len(
                current_words & existing_words
            )

            union = len(
                current_words | existing_words
            )

            similarity = (
                intersection / union
                if union > 0 else 0
            )

            if similarity >= similarity_threshold:
                is_similar = True
                break

        if not is_similar:
            diversified.append(recipe)

    return diversified

# =========================
# MODEL INIT
# =========================
def initialize_model():
    """
    Load saved dataframe + vectorizer if available,
    otherwise train and save them.
    """

    global df, vectorizer, model_loaded, recipe_vectors

    try:
        # try loading
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):

            print("[MODEL] Loading existing trained model...")

            with open(MODEL_PATH, "rb") as f:
                df = pickle.load(f)

            with open(VECTORIZER_PATH, "rb") as f:
                vectorizer = pickle.load(f)

            normalize_dataframe()

            assert vectorizer is not None
            assert df is not None
            # Precompute vectors for faster search
            recipe_vectors = vectorizer.transform(
                df["ingredients_clean"]
            )

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

    assert vectorizer is not None
    # Precompute vectors once
    recipe_vectors = vectorizer.transform(
        df["ingredients_clean"]
    )

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
    - TF-IDF cosine similarity = 60%
    - token overlap = 40%
    Optional bonuses for cuisine/category.
    """

    global df, vectorizer, recipe_vectors

    if df is None or vectorizer is None:
        raise RuntimeError("Recipe matcher is not initialized")

    # =========================================
    # USE PRECOMPUTED VECTORS (FASTER)
    # =========================================
    tfidf_scores = cosine_similarity(user_vector, recipe_vectors).flatten()

    # =========================================
    # TOKEN OVERLAP SCORE
    # =========================================
    token_scores = np.zeros(len(df))

    for i, recipe_tokens in enumerate(df["ingredient_tokens"]):

        # Exact overlap
        common = user_tokens & recipe_tokens

        if len(user_tokens) > 0:

            # Basic overlap
            # =====================================
            # COVERAGE SCORE
            # How much of user's ingredients matched
            # =====================================
            coverage_score = (
                len(common) / len(user_tokens)
            )

            # =====================================
            # PURITY SCORE
            # Penalize recipes with too many extra ingredients
            # =====================================
            purity_score = (
                len(common) / len(recipe_tokens)
                if len(recipe_tokens) > 0 else 0
            )

            # =====================================
            # FINAL TOKEN OVERLAP
            # =====================================
            overlap_score = (
             0.7 * coverage_score
             + 0.3 * purity_score
            )

            # =====================================
            # EXTRA BOOST FOR HIGH MATCHES
            # =====================================
            if overlap_score >= 0.85:
                overlap_score += 0.08

            elif overlap_score >= 0.65:
               overlap_score += 0.04

            # =====================================
            # PENALTY FOR TOO MANY EXTRA INGREDIENTS
            # =====================================
            extra_ingredients = len(recipe_tokens - user_tokens)

            if extra_ingredients > 10:
                overlap_score -= 0.05

            overlap_score = min(overlap_score, 1.0)
            token_scores[i] = max(overlap_score, 0)

    # =========================================
    # CUISINE BONUS
    # =========================================
    cuisine_bonus = np.zeros(len(df))

    if cuisine_filter:
        cuisine_filter = safe_str(cuisine_filter).lower()

        for i, c in enumerate(df["Cuisine"]):

            if cuisine_filter in safe_str(c).lower():
                cuisine_bonus[i] = 0.10

    # =========================================
    # CATEGORY BONUS
    # =========================================
    category_bonus = np.zeros(len(df))

    if category_filter:

        category_filter = safe_str(category_filter).lower()

        for i, c in enumerate(df["Category"]):

            category_text = safe_str(c).lower()

            if category_filter in ["veg", "vegetarian", "v"]:
                 if is_veg(category_text):
                    category_bonus[i] = 0.10

            elif category_filter in ["non veg", "non-veg", "nonveg", "nv"]:
                 if is_nonveg(category_text):
                   category_bonus[i] = 0.10

            elif category_filter in category_text:
                  category_bonus[i] = 0.10

    # =========================================
    # FINAL SCORE
    # =========================================
    composite_scores = (
        (0.6 * tfidf_scores)
        + (0.4 * token_scores)
        + cuisine_bonus
        + category_bonus
    )

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
            filtered = [r for r in filtered if is_veg(r.get("Category", ""))]
        elif category_lower in ["non veg", "non-veg", "nonveg", "nv"]:
            filtered = [r for r in filtered if is_nonveg(r.get("Category", ""))]
        else:
            filtered = [
                r for r in filtered
                if category_lower in safe_str(r.get("Category", "")).lower()
            ]

    # =========================================
    # ALLERGY FILTER
    # =========================================
    if allergies:
        if isinstance(allergies, str):
            allergy_list = [
                clean_ingredients(a.strip().lower())
                for a in allergies.split(",")
                if a.strip()
            ]
        elif isinstance(allergies, list):
            allergy_list = [
                clean_ingredients(safe_str(a).lower())
                for a in allergies
                if safe_str(a)
            ]
        else:
            allergy_list = []
    else:
        allergy_list = []


    # Strict filter: remove recipes containing any allergy term
    temp = []

    for r in filtered:

     # BEST SOURCE: use already precomputed tokens if available
        recipe_tokens = set()

        if "ingredient_tokens" in r:
            recipe_tokens = set(r["ingredient_tokens"])

        else:
            combined_text = " ".join([
                safe_str(r.get("ingredients", "")),
                safe_str(r.get("Detailed_Ingredients", "")),
            ])
            recipe_tokens = get_ingredient_tokens(combined_text)

        blocked = False
        for allergy in allergy_list:
            allergy_tokens = get_ingredient_tokens(allergy)
            if recipe_tokens & allergy_tokens:
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
    global df, vectorizer, model_loaded

    if not model_loaded:
        initialize_model()
    if df is None or vectorizer is None:
        raise RuntimeError("Recipe matcher initialization failed")

    def pre_filter_df(df, expanded_allergies):
        if not expanded_allergies:
         return df

        mask = []

        for _, row in df.iterrows():
            tokens = row["ingredient_tokens"]

            blocked = False
            for allergy in expanded_allergies:
                allergy_tokens = get_ingredient_tokens(allergy)
                if tokens & allergy_tokens:
                    blocked = True
                    break

            mask.append(not blocked)

        return df[pd.Series(mask)]

    # EXPAND ALLERGIES (needed before pre-filtering dataframe)
    allergy_list = []

    if allergies:
        if isinstance(allergies, str):
            allergy_list = [
                a.strip().lower()
                for a in allergies.split(",")
                if a.strip()
            ]
        elif isinstance(allergies, list):
            allergy_list = [
                str(a).lower()
                for a in allergies
                if a
            ]

    ALLERGY_SYNONYMS = {
     "milk": ["milk", "cream", "condensed milk", "milk powder"],
     "cheese": ["cheese", "cheddar", "mozzarella", "processed cheese"],
     "butter": ["butter", "ghee", "margarine"],
     "chilli": ["chilli", "chili", "red chilli", "green chilli", "green chili"],
     "chili": ["chilli", "chili"],
    }

    expanded_allergies = set()
    for a in allergy_list:
        expanded_allergies.add(a)
        if a in ALLERGY_SYNONYMS:
            expanded_allergies.update(ALLERGY_SYNONYMS[a])

    # Tokenize expanded allergies for robust set-based checks
    expanded_allergy_tokens = set()
    for a in expanded_allergies:
        expanded_allergy_tokens.update(get_ingredient_tokens(clean_ingredients(a)))

    # Clean user input and remove allergy terms from the search query
    user_input_clean = clean_ingredients(user_input)
    user_tokens = get_ingredient_tokens(user_input_clean)
    safe_user_tokens = user_tokens - expanded_allergy_tokens
    safe_input_clean = " ".join(
        [token for token in user_input_clean.split() if token in safe_user_tokens]
    )

    # If the user's safe ingredient set is empty, no allergy-safe match is possible
    if not safe_user_tokens:
        return []

    df_filtered = pre_filter_df(df, expanded_allergies)

    assert vectorizer is not None
    # Vectorize user input using the allergy-safe ingredients only
    user_vector = vectorizer.transform([safe_input_clean])

    # Score only against the filtered dataframe: temporarily swap globals
    _orig_df = df
    _orig_recipe_vectors = globals().get("recipe_vectors", None)
    try:
        df = df_filtered
        globals()["recipe_vectors"] = vectorizer.transform(df["ingredients_clean"])

        composite_scores, tfidf_scores, token_scores = calculate_scores(
            user_vector=user_vector,
            user_tokens=safe_user_tokens,
            cuisine_filter=cuisine,
            category_filter=category
        )

        # Get larger pool first so filters can still work
        candidate_k = min(max(top_k * 5, 20), len(df))
        top_indices = composite_scores.argsort()[-candidate_k:][::-1]
    finally:
        df = _orig_df
        globals()["recipe_vectors"] = _orig_recipe_vectors

    # Build candidate results
    results = []
    for idx in top_indices:
        recipe = df_filtered.iloc[idx]

        score = float(composite_scores[idx])
        token_match = float(token_scores[idx])
        # Skip weak matches
        if token_match < 0.35 and score < 0.25:
            continue

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
                "Excellent Match" if token_match >= 0.85 else
                "Good Match" if token_match >= 0.55 else
                "Partial Match"
            )
        }

        # =========================================
        # STRICT INGREDIENT VALIDATION
        # =========================================
        recipe_tokens = recipe["ingredient_tokens"]
        matched_tokens = safe_user_tokens & recipe_tokens
        invalid_tokens = recipe_tokens - safe_user_tokens

        # allow tiny cooking basics
        allowed_extras = {
            "salt",
            "oil",
            "water",
            "spices",
            "masala",
            "chilli",
            "chili",
            "chilli powder",
            "green chili",
            "green chilli",
            "red chili",
             "cumin"
        }

        invalid_tokens = invalid_tokens - allowed_extras

        # Skip recipes with too many unrelated ingredients
        if len(invalid_tokens) > 4:
            continue

        coverage_score = (
            len(matched_tokens) / len(safe_user_tokens)
            if len(safe_user_tokens) > 0 else 0
        )

        results.append(result)

    # Apply optional filters
    results = apply_optional_filters(
        results,
        category=category,
        allergies=allergies,
        max_cooking_time=cooking_time
    )
    # Remove duplicates
    results = remove_duplicate_recipes(results)

    # If filters removed everything, fallback to top_k original results
    if len(results) == 0:
        fallback = []
        for idx in top_indices[:top_k]:
            recipe = df.iloc[idx]
            score = float(composite_scores[idx])
            recipe_tokens = recipe["ingredient_tokens"]

            matched_tokens = safe_user_tokens & recipe_tokens
            if expanded_allergy_tokens and (recipe_tokens & expanded_allergy_tokens):
                continue

            coverage_score = (
             len(matched_tokens) / len(safe_user_tokens)
             if len(safe_user_tokens) > 0 else 0
            )

            purity_score = (
             len(matched_tokens) / len(recipe_tokens)
             if len(recipe_tokens) > 0 else 0
            )

            # Final displayed match score
            token_match = (0.7 * coverage_score) + (0.3 * purity_score)
            token_match = min(token_match, 1.0)

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
                    "Excellent Match" if token_match >= 0.85 else
                    "Good Match" if token_match >= 0.55 else
                    "Partial Match"
                )
            })

        results = fallback

        # =========================================
        # FINAL CLEANUP
        # =========================================

        # Remove duplicates again after fallback
        results = remove_duplicate_recipes(results)

        # Diversify only if we have excess recipes
        if len(results) > top_k:
          results = diversify_results(results)

        # =========================================
        # ENSURE AT LEAST TOP-K RESULTS
        # =========================================
        if len(results) < top_k:
            existing_names = set(
                safe_str(r.get("final_recipe_name", "")).lower()
                for r in results
            )

            for idx in top_indices:
                recipe = df.iloc[idx]
                recipe_tokens = recipe["ingredient_tokens"]

                if expanded_allergy_tokens and len(recipe_tokens & expanded_allergy_tokens) > 0:
                    continue

                name = safe_str(recipe.get("final_recipe_name", "")).lower()
                if name in existing_names:
                    continue

                extra_recipe = {
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
                    "similarity_score": float(composite_scores[idx]),
                    "ingredient_match": "50%",
                    "match_type": "Fallback Match"
                }

                results.append(extra_recipe)
                existing_names.add(name)

                if len(results) >= top_k:
                    break

        # Final trim
        results = results[:top_k]

    # Re-rank
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    # Make JSON safe
    results = [make_json_safe(r) for r in results]

    # =========================================
    # ALWAYS ADD AI SAFE RECIPE (but exclude allergens)
    # =========================================
    ai_tokens = list(safe_user_tokens)
    if ai_tokens:
        results.append({
            "rank": len(results) + 1,
            "recipe_name": "Simple Homemade Dish",
            "final_recipe_name": "AI Safe Simple Recipe",
            "ingredients": ", ".join(ai_tokens),
            "Instructions":
                "1. Prepare ingredients.\n"
                "2. Heat oil in a pan.\n"
                "3. Add ingredients gradually.\n"
                "4. Add salt and basic spices.\n"
                "5. Cook well and serve hot.",
            "Detailed_Ingredients": ", ".join(ai_tokens),
            "Cuisine": cuisine if cuisine else "Custom",
            "Category": category if category else "Custom",
            "CookingTime": cooking_time if cooking_time else 20,
            "Calories (kcal)": None,
            "Carbohydrates g": None,
            "Protein g": None,
            "Fats g": None,
            "Free Sugar g": None,
            "Fibre g": None,
            "Sodium mg": None,
            "Calcium mg": None,
            "Iron mg": None,
            "similarity_score": 1.0,
            "ingredient_match": "100%",
            "match_type": "AI Safe Recipe"
        })

    return results



# =========================
# INIT ON IMPORT
# =========================
print("[INIT] Initializing recipe matcher...")
initialize_model()
print("[INIT] Recipe matcher ready!")