import pandas as pd
from modules.recipe_matcher_prod import df, get_ingredient_tokens, safe_str

# Allowed pantry items
BASIC_INGREDIENTS = {
    "salt", "sugar", "oil", "water", "pepper",
    "spices", "butter", "ghee", "garlic", "ginger"
}


# =========================
# AI FALLBACK GENERATOR
# =========================
def generate_ai_recipe(user_tokens):
    """
    Generate a simple recipe using only given ingredients.
    """

    ingredients_list = list(user_tokens)

    title = "Custom Ingredient Recipe"
    final_title = "AI Generated " + " & ".join(ingredients_list[:3]).title() + " Dish"

    instructions = []
    instructions.append("1. Prepare all ingredients by washing and chopping as needed.")
    instructions.append("2. Heat oil in a pan.")
    instructions.append("3. Add base ingredients like garlic/ginger if available.")
    instructions.append(f"4. Add {', '.join(ingredients_list)} and cook well.")
    instructions.append("5. Add salt, spices, and seasoning to taste.")
    instructions.append("6. Cook until everything is well combined.")
    instructions.append("7. Serve hot and enjoy your custom dish!")

    return {
        "rank": 1,
        "recipe_name": title,
        "final_recipe_name": final_title,
        "ingredients": ", ".join(ingredients_list),
        "Instructions": "\n".join(instructions),
        "Detailed_Ingredients": ", ".join(ingredients_list),
        "Cuisine": "Custom",
        "Category": "Veg",
        "CookingTime": 20,
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
        "match_type": "AI Generated (Strict Mode)"
    }


# =========================
# STRICT MATCH FUNCTION
# =========================
def get_strict_recipes(user_input, top_k=3):
    """
    Return recipes that can be made ONLY with given ingredients
    + basic pantry items.
    If none found → generate AI recipe.
    """

    if df is None or len(df) == 0:
        return []

    # Clean + tokenize input
    user_tokens = get_ingredient_tokens(user_input)

    if not user_tokens:
        return []

    allowed_tokens = user_tokens.union(BASIC_INGREDIENTS)

    strict_results = []

    for _, row in df.iterrows():
        recipe_tokens = get_ingredient_tokens(row["ingredients_clean"])

        # STRICT CHECK
        if recipe_tokens.issubset(allowed_tokens):
            strict_results.append(row)

    # =========================
    # CASE 1: STRICT MATCH FOUND
    # =========================
    if len(strict_results) > 0:
        final_results = []

        for i, recipe in enumerate(strict_results[:top_k]):
            result = {
                "rank": i + 1,
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
                "similarity_score": 1.0,
                "ingredient_match": "100%",
                "match_type": "Strict Match"
            }

            final_results.append(result)

        return final_results

    # =========================
    # CASE 2: NO STRICT MATCH → AI FALLBACK
    # =========================
    ai_recipe = generate_ai_recipe(user_tokens)

    return [ai_recipe]