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
    Generate a smart recipe based on ingredient types.
    """

    tokens = set(user_tokens)
    ingredients_list = list(tokens)

    # -------------------------
    # CATEGORY DETECTION
    # -------------------------
    has_chicken = "chicken" in tokens
    has_egg = "egg" in tokens or "eggs" in tokens
    has_beef = "beef" in tokens
    has_rice = "rice" in tokens
    has_bread = "bread" in tokens
    has_veg = any(x in tokens for x in ["onion", "tomato", "carrot", "beans", "capsicum"])

    # -------------------------
    # CHICKEN RECIPES
    # -------------------------
    if has_chicken:
        title = "Chicken Fry"
        final_title = "AI Generated Spicy Chicken Fry"

        instructions = [
            "1. Clean and cut chicken into pieces.",
            "2. Marinate with salt, pepper, spices, and a little oil.",
            "3. Heat oil in a pan.",
            "4. Add garlic and ginger if available.",
            "5. Add chicken and cook on medium flame.",
            "6. Stir occasionally until chicken is fully cooked.",
            "7. Roast slightly for crispy texture.",
            "8. Serve hot."
        ]

    # -------------------------
    # EGG RECIPES
    # -------------------------
    elif has_egg and has_bread:
        title = "Egg Sandwich"
        final_title = "AI Egg Bread Sandwich"

        instructions = [
            "1. Boil or fry the eggs.",
            "2. Mash eggs with salt and pepper.",
            "3. Toast bread slices.",
            "4. Spread egg mixture between bread.",
            "5. Optionally add vegetables or sauce.",
            "6. Serve warm."
        ]

    elif has_egg:
        title = "Masala Omelette"
        final_title = "AI Spiced Egg Omelette"

        instructions = [
            "1. Beat eggs in a bowl.",
            "2. Add chopped onion, chili, and salt.",
            "3. Heat oil in a pan.",
            "4. Pour egg mixture.",
            "5. Cook both sides until golden.",
            "6. Serve hot."
        ]

    # -------------------------
    # BEEF RECIPES
    # -------------------------
    elif has_beef:
        title = "Beef Steak"
        final_title = "AI Pan-Seared Beef Steak"

        instructions = [
            "1. Season beef with salt and pepper.",
            "2. Heat a pan with oil or butter.",
            "3. Place beef and cook on high heat.",
            "4. Flip and cook to desired doneness.",
            "5. Rest for a few minutes.",
            "6. Slice and serve."
        ]

    # -------------------------
    # RICE RECIPES
    # -------------------------
    elif has_rice:
        title = "Fried Rice"
        final_title = "AI Quick Fried Rice"

        instructions = [
            "1. Cook rice and let it cool.",
            "2. Heat oil in a pan.",
            "3. Add garlic and vegetables if available.",
            "4. Add rice and stir well.",
            "5. Add salt, pepper, and sauces.",
            "6. Mix and cook for 5 minutes.",
            "7. Serve hot."
        ]

    # -------------------------
    # VEGETABLE DISH
    # -------------------------
    elif has_veg:
        title = "Veg Stir Fry"
        final_title = "AI Mixed Vegetable Stir Fry"

        instructions = [
            "1. Chop all vegetables.",
            "2. Heat oil in a pan.",
            "3. Add garlic and sauté.",
            "4. Add vegetables and stir fry.",
            "5. Add salt and spices.",
            "6. Cook until slightly crunchy.",
            "7. Serve hot."
        ]

    # -------------------------
    # DEFAULT FALLBACK
    # -------------------------
    else:
        title = "Custom Ingredient Dish"
        final_title = "AI Generated Mixed Ingredient Recipe"

        instructions = [
            "1. Prepare all ingredients.",
            "2. Heat oil in a pan.",
            "3. Add base spices if available.",
            f"4. Add {', '.join(ingredients_list)}.",
            "5. Cook until well combined.",
            "6. Season to taste.",
            "7. Serve hot."
        ]

    # -------------------------
    # FINAL OBJECT
    # -------------------------
    return {
        "rank": 1,
        "recipe_name": title,
        "final_recipe_name": final_title,
        "ingredients": ", ".join(ingredients_list),
        "Instructions": "\n".join(instructions),
        "Detailed_Ingredients": ", ".join(ingredients_list),
        "Cuisine": "Custom AI",
        "Category": "Non-Veg" if any(x in tokens for x in ["chicken", "egg", "beef"]) else "Veg",
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
        "match_type": "AI Generated (Smart Strict Mode)"
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