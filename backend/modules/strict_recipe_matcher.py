# =========================================================
# STRICT RECIPE MATCHING + GEMINI AI GENERATION
# =========================================================

import os
import json
import pandas as pd
from google import genai

from dotenv import load_dotenv

from modules.recipe_matcher_prod import (
    df,
    get_ingredient_tokens,
    safe_str,
    clean_ingredients
)

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found")

# =========================================================
# CONFIGURE GEMINI
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =========================================================
# BASIC PANTRY ITEMS
# =========================================================

PANTRY_ITEMS = {
    "salt",
    "sugar",
    "oil",
    "water",
    "pepper",
    "spices",
    "butter",
    "ghee",
    "garlic",
    "ginger",
    "turmeric",
    "garam",
    "masala",
    "chili",
    "powder",
    "sweet",
    "black"
}
# =========================================================
# AI RECIPE GENERATOR
# =========================================================
def simple_fallback_recipe(user_tokens):

    ingredients = list(user_tokens)

    instructions = [
        "1. Wash and prepare all ingredients.",
        "2. Heat oil in a pan.",
        "3. Add ingredients gradually.",
        "4. Add salt and spices to taste.",
        "5. Cook until well combined.",
        "6. Serve hot."
    ]

    return {
        "rank": 1,
        "recipe_name": "Simple Homemade Dish",
        "final_recipe_name": "AI Safe Simple Recipe",
        "ingredients": ", ".join(ingredients),
        "Instructions": "\n".join(instructions),
        "Detailed_Ingredients": ", ".join(ingredients),
        "Cuisine": "Custom",
        "Category": (
         "Non-Veg"
        if any(
         x in user_tokens
         for x in ["chicken", "egg", "beef", "fish", "mutton"]
         )
        else "Veg"
        ),
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
        "match_type": "Fallback Safe Recipe"
    }


def generate_ai_recipe(user_tokens,cuisine=None,category=None):
    """
    Generate recipe STRICTLY using user ingredients.
    """
    print("GENERATE AI RECIPE CALLED")
    ingredients = list(user_tokens)

    prompt = f"""
You are an expert chef AI.

Generate ONE realistic recipe using ONLY these ingredients:

{", ".join(ingredients)}

Allowed pantry items:
{", ".join(PANTRY_ITEMS)}

If additional ingredients are required,
adapt the recipe instead of adding them.

Recipe must:
1. Be realistic and cookable
2. Return ONLY valid JSON
3. Never use markdown
4. Never invent ingredients
5. Use simple preparation if ingredients are limited
6. Include realistic estimated nutrition values for ALL nutrition fields
JSON FORMAT:

{{
    "recipe_name": "",
  "final_recipe_name": "",
  "ingredients": "",
  "Instructions": "",
  "Detailed_Ingredients": "",
  "Cuisine": "",
  "Category": "",
  "CookingTime": 0,

  "Calories (kcal)": 0,
  "Carbohydrates g": 0,
  "Protein g": 0,
  "Fats g": 0,
  "Free Sugar g": 0,
  "Fibre g": 0,
  "Sodium mg": 0,
  "Calcium mg": 0,
  "Iron mg": 0
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
         raise Exception("Empty response from Gemini")
        generated_text = response.text.strip()
        print("\nRAW GEMINI RESPONSE:")
        print(generated_text)
        # ---------------------------------------------
        # REMOVE MARKDOWN IF PRESENT
        # ---------------------------------------------

        if generated_text.startswith("```json"):
            generated_text = (
                generated_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        elif generated_text.startswith("```"):
            generated_text = (
                generated_text
                .replace("```", "")
                .strip()
            )

        # ---------------------------------------------
        # PARSE JSON
        # ---------------------------------------------

        data = json.loads(generated_text)

        # ---------------------------------------------
        # VALIDATE INGREDIENTS
        # ---------------------------------------------

        ingredients_field = data.get("ingredients", "")

        if isinstance(ingredients_field, list):
         ingredients_text = " ".join(ingredients_field)
        else:
         ingredients_text = str(ingredients_field)

        generated_ingredients = set(
            token.rstrip("s")
            for token in get_ingredient_tokens(ingredients_text)
        )

        allowed_tokens = set(
            token.rstrip("s")
            for token in user_tokens.union(PANTRY_ITEMS)
        )

        # Reject hallucinated ingredients
        invalid_items = generated_ingredients - allowed_tokens

        # Allow small harmless hallucinations
        SAFE_OPTIONAL_ITEMS = {
            "onion",
            "coriander",
            "lemon",
            "soy sauce",
            "vinegar",
            "green chili",
            "chilli"
        }

        real_invalid = invalid_items - SAFE_OPTIONAL_ITEMS

        if real_invalid:

             print("AI used invalid ingredients:", real_invalid)

            # Instead of failing completely,
            # regenerate a simpler recipe

             return simple_fallback_recipe(user_tokens)

        # ---------------------------------------------
        # SUCCESS RESPONSE
        # ---------------------------------------------

        return {

    "rank": 1,

    "recipe_name": safe_str(
        data.get("recipe_name", "")
    ),

    "final_recipe_name": safe_str(
        data.get("final_recipe_name", "")
    ),

    "ingredients": safe_str(
        data.get("ingredients", "")
    ),

    "Instructions": safe_str(
        data.get("Instructions", "")
    ),

    "Detailed_Ingredients": safe_str(
        data.get("Detailed_Ingredients", "")
    ),

    "Cuisine": safe_str(
        data.get("Cuisine", "")
    ),

    "Category": safe_str(
        data.get("Category", "")
    ),

    "CookingTime": int(
        data.get("CookingTime", 0)
    ),

    "Calories (kcal)": float(
        data.get("Calories (kcal)", 0)
    ),

    "Carbohydrates g": float(
        data.get("Carbohydrates g", 0)
    ),

    "Protein g": float(
        data.get("Protein g", 0)
    ),

    "Fats g": float(
        data.get("Fats g", 0)
    ),

    "Free Sugar g": float(
        data.get("Free Sugar g", 0)
    ),

    "Fibre g": float(
        data.get("Fibre g", 0)
    ),

    "Sodium mg": float(
        data.get("Sodium mg", 0)
    ),

    "Calcium mg": float(
        data.get("Calcium mg", 0)
    ),

    "Iron mg": float(
        data.get("Iron mg", 0)
    ),

    "similarity_score": 1.0,

    "ingredient_match": "100%",

    "match_type": "AI Generated Strict Recipe"
}

    except Exception as e:

        print("Gemini API Error:", e)

        return {
            "rank": 1,
            "recipe_name": "Simple Homemade Dish",
            "final_recipe_name": "Simple Homemade Dish ",
            "ingredients": ", ".join(ingredients),
            "Instructions":
            "1. Wash and prepare ingredients.\n"
            "2. Heat oil in a pan.\n"
            "3. Add ingredients gradually.\n"
            "4. Add salt and spices to taste.\n"
            "5. Cook until done and serve hot.",
            "Detailed_Ingredients": ", ".join(ingredients),
            "Cuisine": "Custom",
            "Category": (
             "Non-Veg"
                if any(
                    x in user_tokens
                    for x in [
                        "chicken",
                        "egg",
                        "fish",
                        "beef",
                        "mutton",
                        "prawn"
                    ]
                )
                else "Veg"
            ),
            "CookingTime": 20,
            "Calories (kcal)": 350,
            "Carbohydrates g": 40,
            "Protein g": 18,
            "Fats g": 12,
            "Free Sugar g": 5,
            "Fibre g": 6,
            "Sodium mg": 400,
            "Calcium mg": 120,
            "Iron mg": 3,
            "similarity_score": 1.0,
            "ingredient_match": "100%",
            "match_type": "AI Generated Fallback Recipe"
        }

# =========================================================
# STRICT RECIPE MATCHING
# =========================================================

def get_strict_recipes(user_input, top_k=3, allergies=None,cuisine=None,category=None):
    """
    Return recipes that can be made ONLY
    with provided ingredients + pantry items.

    If no strict recipe exists,
    generate AI recipe.
    """
    print("\n Strict recipe called")

    # DATAFRAME CHECK
    if df is None or len(df) == 0:
        return []
    
    # TOKENIZE USER INPUT
    user_tokens = get_ingredient_tokens(user_input)

    if not user_tokens:
        return []
    
    # ALLOWED TOKENS
    allowed_tokens = user_tokens

    strict_results = []

    # DYNAMIC THRESHOLDS based on number of user ingredients
    num_user_ingredients = len(user_tokens)
    
    if num_user_ingredients == 1:
        # Single ingredient: be lenient
        MIN_MATCH_PERCENTAGE = 60
        MIN_USER_INGREDIENT_MATCH = 1  # Just needs to use the 1 ingredient
    elif num_user_ingredients == 2:
        # Two ingredients: moderate
        MIN_MATCH_PERCENTAGE = 70
        MIN_USER_INGREDIENT_MATCH = 2
    else:
        # 3+ ingredients: strict
        MIN_MATCH_PERCENTAGE = 80
        MIN_USER_INGREDIENT_MATCH = 2
    
    for _, row in df.iterrows():

        recipe_tokens = get_ingredient_tokens(
            row["ingredients_clean"]
        )

        # Skip empty recipes
        if not recipe_tokens:
            continue

        # Calculate match percentage (all ingredients)
        matched_tokens = recipe_tokens.intersection(allowed_tokens)
        match_percentage = (len(matched_tokens) / len(recipe_tokens)) * 100 if recipe_tokens else 0

        # CRITICAL: Must also match at least some user-provided ingredients
        user_ingredient_overlap = recipe_tokens.intersection(user_tokens)
        
        # Accept recipes that meet BOTH thresholds:
        # 1. 50%+ of recipe ingredients are available
        # 2. At least 1+ user-provided ingredient is used
        if(match_percentage >= MIN_MATCH_PERCENTAGE and len(user_ingredient_overlap) >= 1):
            row["match_percentage"] = match_percentage
            row["user_ingredient_count"] = len(user_ingredient_overlap)
            strict_results.append(row)
    
    # Sort by user ingredient match first, then by overall match percentage
    strict_results.sort(
        key=lambda x: (x.get("user_ingredient_count", 0), x.get("match_percentage", 0)), 
        reverse=True
    )
    
    print(f"Strict matches found: {len(strict_results)}")

    # FILTER STRICT RESULTS BY ALLERGIES (if provided)
    expanded_allergy_tokens = set()
    if allergies:
        allergy_list = []
        if isinstance(allergies, str):
            allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
        elif isinstance(allergies, list):
            allergy_list = [str(a).lower() for a in allergies if a]

        ALLERGY_SYNONYMS = {
            "milk": ["milk", "cream", "condensed milk", "milk powder"],
            "cheese": ["cheese", "cheddar", "mozzarella", "processed cheese"],
            "butter": ["butter", "ghee", "margarine"]
        }

        for a in allergy_list:
            try:
                expanded_allergy_tokens.update(get_ingredient_tokens(clean_ingredients(a)))
            except Exception:
                expanded_allergy_tokens.update(get_ingredient_tokens(a))

            if a in ALLERGY_SYNONYMS:
                for syn in ALLERGY_SYNONYMS[a]:
                    try:
                        expanded_allergy_tokens.update(get_ingredient_tokens(clean_ingredients(syn)))
                    except Exception:
                        expanded_allergy_tokens.update(get_ingredient_tokens(syn))

    if expanded_allergy_tokens:
        filtered_strict = []
        for row in strict_results:
            tokens = get_ingredient_tokens(row["ingredients_clean"])
            if not (tokens & expanded_allergy_tokens):
                filtered_strict.append(row)
        strict_results = filtered_strict

    # =====================================================
    # CASE 1 : STRICT MATCH FOUND
    # =====================================================

    if len(strict_results) > 0:
        print("STRICT MATCH FOUND")
        print("Returning strict recipe(s)")

        final_results = []

        for i, recipe in enumerate(strict_results[:top_k]):

            result = {

                "rank": i + 1,

                "recipe_name": safe_str(
                    recipe.get("recipe_name", "")
                ),

                "final_recipe_name": safe_str(
                    recipe.get("final_recipe_name", "")
                ),

                "ingredients": safe_str(
                    recipe.get("ingredients", "")
                ),

                "Instructions": safe_str(
                    recipe.get("Instructions", "")
                ),

                "Detailed_Ingredients": safe_str(
                    recipe.get("Detailed_Ingredients", "")
                ),

                "Cuisine": safe_str(
                    recipe.get("Cuisine", "")
                ),

                "Category": safe_str(
                    recipe.get("Category", "")
                ),

                "CookingTime": (
                    int(recipe["CookingTime"])
                    if pd.notna(recipe["CookingTime"])
                    else None
                ),

                "Calories (kcal)": (
                    float(recipe["Calories (kcal)"])
                    if pd.notna(recipe["Calories (kcal)"])
                    else None
                ),

                "Carbohydrates g": (
                    float(recipe["Carbohydrates g"])
                    if pd.notna(recipe["Carbohydrates g"])
                    else None
                ),

                "Protein g": (
                    float(recipe["Protein g"])
                    if pd.notna(recipe["Protein g"])
                    else None
                ),

                "Fats g": (
                    float(recipe["Fats g"])
                    if pd.notna(recipe["Fats g"])
                    else None
                ),

                "Free Sugar g": (
                    float(recipe["Free Sugar g"])
                    if pd.notna(recipe["Free Sugar g"])
                    else None
                ),

                "Fibre g": (
                    float(recipe["Fibre g"])
                    if pd.notna(recipe["Fibre g"])
                    else None
                ),

                "Sodium mg": (
                    float(recipe["Sodium mg"])
                    if pd.notna(recipe["Sodium mg"])
                    else None
                ),

                "Calcium mg": (
                    float(recipe["Calcium mg"])
                    if pd.notna(recipe["Calcium mg"])
                    else None
                ),

                "Iron mg": (
                    float(recipe["Iron mg"])
                    if pd.notna(recipe["Iron mg"])
                    else None
                ),

                "similarity_score": 1.0,

                "ingredient_match": f"{recipe.get('match_percentage', 100):.0f}%",

                "match_type": "Strict Match"
            }

            final_results.append(result)

        return final_results

    # =====================================================
    # CASE 2 : NO MATCH -> AI GENERATION
    # =====================================================
    print("NO STRICT MATCH FOUND")
    print("Trying Gemini AI generation...")
    # If no strict matches, generate AI recipe but exclude allergens
    safe_user_tokens = (
        {t for t in user_tokens if t not in expanded_allergy_tokens}
        if expanded_allergy_tokens else user_tokens
    )

    if not safe_user_tokens:
        return []

    ai_recipe = generate_ai_recipe(safe_user_tokens,cuisine=cuisine,category=category)

    return [ai_recipe]