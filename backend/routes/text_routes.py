from flask import Blueprint, request, jsonify
import pandas as pd
import traceback

from modules.recipe_matcher_prod import recommend_recipes, df, safe_str
from modules.strict_recipe_matcher import get_strict_recipes

text_routes = Blueprint("text_routes", __name__)


# =========================
# HELPERS
# =========================
def get_row_value(row, possible_names, default=""):
    """
    Return first available value from a pandas row for multiple possible column names.
    """
    for col in possible_names:
        if col in row.index:
            value = row[col]
            if pd.notna(value):
                return value
    return default


def to_python_int(value):
    if value is None or pd.isna(value):
        return None
    try:
        return int(value)
    except:
        return None


def to_python_float(value):
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except:
        return None


def build_full_recipe_details(recipe_name):
    """
    Find full recipe details in dataframe by matching recipe_name or final_recipe_name.
    """
    global df

    if df is None or len(df) == 0:
        return None

    recipe_name = safe_str(recipe_name).strip().lower()
    if not recipe_name:
        return None

    # Possible columns
    recipe_name_cols = ["recipe_name", "Recipe Name", "recipe"]
    final_recipe_cols = ["final_recipe_name", "Final recipe name", "Final Recipe Name"]
    ingredients_cols = ["ingredients", "Ingredients"]
    instructions_cols = ["instructions", "Instructions", "RecipeInstructions", "Method", "Directions"]
    detailed_ingredients_cols = [
        "Detailed_Ingredients", "Detailed Ingredients", "Detailed _Ingredients",
        "Detailed ingredients", "Detailed_ingredients"
    ]
    cuisine_cols = ["Cuisine", "cuisine"]
    category_cols = ["Category", "category"]
    cooking_cols = ["CookingTime", "Cooking Time", "cooking_time"]
    calories_cols = ["Calories (kcal)", "Calories", "calories"]
    carbohydrates_cols = ["Carbohydrates g", "Carbohydrates (g)", "Carbohydrates"]
    protein_cols = ["Protein g", "Protein (g)", "Protein"]
    fats_cols = ["Fats g", "Fats (g)", "Fats"]
    free_sugar_cols = ["Free Sugar g", "Free Sugar (g)", "Free Sugar"]
    fibre_cols = ["Fibre g", "Fibre (g)", "Fibre"]
    sodium_cols = ["Sodium mg", "Sodium (mg)", "Sodium"]
    calcium_cols = ["Calcium mg", "Calcium (mg)", "Calcium"]
    iron_cols = ["Iron mg", "Iron (mg)", "Iron"]

    # Try exact match on recipe_name
    matched_row = None
    for _, row in df.iterrows():
        row_recipe_name = safe_str(get_row_value(row, recipe_name_cols)).lower()
        row_final_name = safe_str(get_row_value(row, final_recipe_cols)).lower()

        if recipe_name == row_recipe_name or recipe_name == row_final_name:
            matched_row = row
            break

    # Fallback partial contains
    if matched_row is None:
        for _, row in df.iterrows():
            row_recipe_name = safe_str(get_row_value(row, recipe_name_cols)).lower()
            row_final_name = safe_str(get_row_value(row, final_recipe_cols)).lower()

            if recipe_name in row_recipe_name or recipe_name in row_final_name:
                matched_row = row
                break

    if matched_row is None:
        return None

    details = {
        "recipe_name": safe_str(get_row_value(matched_row, recipe_name_cols)),
        "final_recipe_name": safe_str(get_row_value(matched_row, final_recipe_cols)),
        "ingredients": safe_str(get_row_value(matched_row, ingredients_cols)),
        "Instructions": safe_str(get_row_value(matched_row, instructions_cols)),
        "Detailed_Ingredients": safe_str(get_row_value(matched_row, detailed_ingredients_cols)),
        "Cuisine": safe_str(get_row_value(matched_row, cuisine_cols)),
        "Category": safe_str(get_row_value(matched_row, category_cols)),
        "CookingTime": to_python_int(get_row_value(matched_row, cooking_cols, None)),
        "Calories (kcal)": to_python_float(get_row_value(matched_row, calories_cols, None)),
        "Carbohydrates g": to_python_float(get_row_value(matched_row, carbohydrates_cols, None)),
        "Protein g": to_python_float(get_row_value(matched_row, protein_cols, None)),
        "Fats g": to_python_float(get_row_value(matched_row, fats_cols, None)),
        "Free Sugar g": to_python_float(get_row_value(matched_row, free_sugar_cols, None)),
        "Fibre g": to_python_float(get_row_value(matched_row, fibre_cols, None)),
        "Sodium mg": to_python_float(get_row_value(matched_row, sodium_cols, None)),
        "Calcium mg": to_python_float(get_row_value(matched_row, calcium_cols, None)),
        "Iron mg": to_python_float(get_row_value(matched_row, iron_cols, None)),
    }

    return details


def merge_recipe_with_details(base_recipe):
    """
    Merge recommendation result with full recipe details from dataframe.
    """
    full_details = build_full_recipe_details(
        base_recipe.get("recipe_name") or base_recipe.get("final_recipe_name")
    )

    merged = {
        "rank": to_python_int(base_recipe.get("rank")),
        "recipe_name": safe_str(base_recipe.get("recipe_name", "")),
        "final_recipe_name": safe_str(base_recipe.get("final_recipe_name", "")),
        "ingredients": safe_str(base_recipe.get("ingredients", "")),
        "Instructions": safe_str(base_recipe.get("Instructions", "")),
        "Detailed_Ingredients": safe_str(base_recipe.get("Detailed_Ingredients", "")),
        "Cuisine": safe_str(base_recipe.get("Cuisine", "")),
        "Category": safe_str(base_recipe.get("Category", "")),
        "CookingTime": to_python_int(base_recipe.get("CookingTime")),
        "Calories (kcal)": to_python_float(base_recipe.get("Calories (kcal)")),
        "Carbohydrates g": to_python_float(base_recipe.get("Carbohydrates g")),
        "Protein g": to_python_float(base_recipe.get("Protein g")),
        "Fats g": to_python_float(base_recipe.get("Fats g")),
        "Free Sugar g": to_python_float(base_recipe.get("Free Sugar g")),
        "Fibre g": to_python_float(base_recipe.get("Fibre g")),
        "Sodium mg": to_python_float(base_recipe.get("Sodium mg")),
        "Calcium mg": to_python_float(base_recipe.get("Calcium mg")),
        "Iron mg": to_python_float(base_recipe.get("Iron mg")),
        "similarity_score": to_python_float(base_recipe.get("similarity_score")),
        "ingredient_match": safe_str(base_recipe.get("ingredient_match", "")),
        "match_type": safe_str(base_recipe.get("match_type", "")),
    }

    # If full details found, prefer them when base value is missing
    if full_details:
        if not merged["recipe_name"]:
            merged["recipe_name"] = full_details["recipe_name"]

        if not merged["final_recipe_name"]:
            merged["final_recipe_name"] = full_details["final_recipe_name"]

        if not merged["ingredients"]:
            merged["ingredients"] = full_details["ingredients"]

        merged["Instructions"] = full_details["Instructions"] or merged["Instructions"]
        merged["Detailed_Ingredients"] = full_details["Detailed_Ingredients"] or merged["Detailed_Ingredients"]

        if not merged["Cuisine"]:
            merged["Cuisine"] = full_details["Cuisine"]

        if not merged["Category"]:
            merged["Category"] = full_details["Category"]

        if merged["CookingTime"] is None:
            merged["CookingTime"] = full_details["CookingTime"]

        if merged["Calories (kcal)"] is None:
            merged["Calories (kcal)"] = full_details["Calories (kcal)"]

        if merged["Carbohydrates g"] is None:
            merged["Carbohydrates g"] = full_details["Carbohydrates g"]

        if merged["Protein g"] is None:
            merged["Protein g"] = full_details["Protein g"]

        if merged["Fats g"] is None:
            merged["Fats g"] = full_details["Fats g"]

        if merged["Free Sugar g"] is None:
            merged["Free Sugar g"] = full_details["Free Sugar g"]

        if merged["Fibre g"] is None:
            merged["Fibre g"] = full_details["Fibre g"]

        if merged["Sodium mg"] is None:
            merged["Sodium mg"] = full_details["Sodium mg"]

        if merged["Calcium mg"] is None:
            merged["Calcium mg"] = full_details["Calcium mg"]

        if merged["Iron mg"] is None:
            merged["Iron mg"] = full_details["Iron mg"]

    return merged


# =========================
# ROUTE: SEARCH BY TEXT
# =========================
@text_routes.route("/search/text", methods=["POST"])
def search_by_text():
    """
    POST /search/text
    Body:
    {
      "ingredients": "chicken, onion, tomato",
      "cuisine": "Indian",          # optional
      "category": "non veg",        # optional
      "allergies": "peanut,milk",   # optional OR list
      "cooking_time": 30,           # optional max time
      "top_k": 5                    # optional
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON body provided",
                "recipes": []
            }), 400

        ingredients = safe_str(data.get("ingredients", "")).strip()
        cuisine = data.get("cuisine")
        category = data.get("category")
        allergies = data.get("allergies") or data.get("allergy")
        cooking_time = data.get("cooking_time") or data.get("cooking_time_range")
        top_k = data.get("top_k", 5)

        # Validate input
        if not ingredients:
            return jsonify({
                "success": False,
                "message": "Please provide ingredients",
                "recipes": []
            }), 400

        try:
            top_k = int(top_k)
            if top_k <= 0:
                top_k = 5
        except:
            top_k = 5

        # Get base recommendations
        base_recipes = recommend_recipes(
            user_input=ingredients,
            cuisine=cuisine,
            category=category,
            allergies=allergies,
            cooking_time=cooking_time,
            top_k=top_k
        )

        # Merge with full details
        final_recipes = []
        for recipe in base_recipes:
            merged = merge_recipe_with_details(recipe)
            final_recipes.append(merged)

        # Compute strict-match recipes separately
        strict_recipes = get_strict_recipes(ingredients, top_k=1)
        

        return jsonify({
            "success": True,
            "input_ingredients": ingredients,
            "filters": {
                "cuisine": cuisine if cuisine else None,
                "category": category if category else None,
                "allergies": allergies if allergies else None,
                "cooking_time": to_python_int(cooking_time) if cooking_time is not None else None,
                "top_k": top_k
            },
            "count": len(final_recipes),
            "recipes": final_recipes,
            "strict_recipes": strict_recipes,
            "message": f"Found {len(final_recipes)} recipes matching your preferences"
        }), 200

    except Exception as e:
        print("ERROR in /search/text:")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
            "recipes": []
        }), 500
    

# =========================
# ROUTE: GET RECIPE DETAILS
# =========================
@text_routes.route("/recipe/details", methods=["POST"])
def get_recipe_details():
    """
    POST /recipe/details
    Body:
    {
      "recipe_name": "Chicken Curry"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON body provided"
            }), 400

        recipe_name = safe_str(data.get("recipe_name", "")).strip()

        if not recipe_name:
            return jsonify({
                "success": False,
                "message": "Please provide recipe_name"
            }), 400

        details = build_full_recipe_details(recipe_name)

        if not details:
            return jsonify({
                "success": False,
                "message": "Recipe not found"
            }), 404

        return jsonify({
            "success": True,
            "recipe": details
        }), 200

    except Exception as e:
        print("ERROR in /recipe/details:")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}"
        }), 500