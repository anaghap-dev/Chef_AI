import traceback

from flask import Blueprint, request, jsonify
from modules.recipe_matcher_prod import recommend_recipes, df
from modules.health_preferences import (
    HealthPreferences, health_matcher, COMMON_ALLERGENS, DIETARY_PREFERENCES
)
import pandas as pd

text_routes = Blueprint("text_routes", __name__)


@text_routes.route("/search/text", methods=["POST"])
def search_by_text():
    """
    Search for recipes by ingredients with optional health filtering.

    Request JSON:
    {
        "ingredients": "chicken, garlic, onion",
        "cuisine": "Italian",           // optional
        "top_k": 5,                     // optional

        // Health & Dietary preferences (all optional)
        "dietary_type": "vegetarian",   // "vegetarian", "non_vegetarian", "vegan"
        "allergies": ["dairy", "eggs"], // List of allergen names
        "max_calories": 500,            // Max calories per serving
        "max_sodium": 1000,             // Max sodium (mg) per serving
        "min_protein": 20,              // Min protein (g) per serving
        "avoid_ingredients": ["nuts"]   // Ingredients to avoid
    }
    """
    try:
        data = request.get_json()
        ingredients = data.get("ingredients", "").strip()

        if not ingredients:
            return jsonify({"error": "Please provide ingredients"}), 400

        # Basic recipe search
        base_recipes = recommend_recipes(
            ingredients,
            cuisine=data.get("cuisine"),
            top_k=data.get("top_k", 5) * 2  # Get more to filter
        )

        # Health preferences filtering
        health_prefs = HealthPreferences()
        health_prefs.dietary_type = data.get("dietary_type")
        health_prefs.allergies = data.get("allergies", [])
        health_prefs.max_calories = data.get("max_calories")
        health_prefs.max_sodium = data.get("max_sodium")
        health_prefs.min_protein = data.get("min_protein")
        health_prefs.avoid_ingredients = data.get("avoid_ingredients", [])

        # Filter recipes based on health preferences
        filtered_recipes = []

        for recipe in base_recipes:
            # Find recipe in dataframe
            recipe_matches = health_matcher.df[
                health_matcher.df['recipe_name'] == recipe['recipe_name']
            ]

            if len(recipe_matches) == 0:
                continue

            recipe_idx = recipe_matches.index[0]

            # Check health compatibility
            if not health_matcher.check_dietary_compatibility(recipe_idx, health_prefs):
                continue
            if not health_matcher.check_nutritional_requirements(recipe_idx, health_prefs):
                continue

            # Add full recipe details
            full_recipe_matches = df[df['recipe_name'] == recipe['recipe_name']]
            if len(full_recipe_matches) == 0:
                continue
            full_recipe = full_recipe_matches.iloc[0]

            def safe_str(value):
                return '' if pd.isna(value) else str(value)

            existing_final_name = safe_str(recipe.get('final_recipe_name', ''))

            full_final_name = (
               safe_str(full_recipe.get('final_recipe_name', '')) or
               safe_str(full_recipe.get('Final recipe name', '')) or
               safe_str(full_recipe.get('Final Recipe Name', ''))
            )

            recipe['final_recipe_name'] = existing_final_name or full_final_name or safe_str(recipe.get('recipe_name', ''))
            recipe['Instructions'] = safe_str(full_recipe.get('Instructions', ''))
            # Try all possible column name variations
            detailed_ing = (
              safe_str(full_recipe.get('Detailed_Ingredients', '')) or
              safe_str(full_recipe.get('Detailed ingredients', '')) or
              safe_str(full_recipe.get('Detailed Ingredients', '')) or
              safe_str(full_recipe.get('Detailed_ingredients', ''))
        )

            # Fallback only if no detailed ingredients found
            if not detailed_ing:
              detailed_ing = safe_str(full_recipe.get('ingredients', ''))

            recipe['Detailed_Ingredients'] = detailed_ing
            recipe['Category'] = safe_str(full_recipe.get('Category', ''))
            recipe['Allergy'] = safe_str(full_recipe.get('Allergy', ''))

            # Add nutritional info
            nutrition = health_matcher.get_nutrition_info(recipe_idx)
            recipe['nutrition'] = nutrition

            # Flatten nutrition for frontend compatibility
            recipe['Calories kcal'] = nutrition.get('Calories (kcal)')
            recipe['Protein g'] = nutrition.get('Protein (g)')
            recipe['Carbohydrates g'] = nutrition.get('Carbohydrates (g)')
            recipe['Fats g'] = nutrition.get('Fats (g)')
            recipe['Free Sugar g'] = nutrition.get('Free Sugar (g)')
            recipe['Fibre g'] = nutrition.get('Fibre (g)')
            recipe['Sodium mg'] = nutrition.get('Sodium (mg)')
            recipe['Calcium mg'] = nutrition.get('Calcium (mg)')
            recipe['Iron mg'] = nutrition.get('Iron (mg)')

            filtered_recipes.append(recipe)

        # Trim to requested top_k
        final_recipes = filtered_recipes[:data.get("top_k", 5)]

        return jsonify({
            "input_ingredients": ingredients,
            "cuisine_filter": data.get("cuisine"),
            "health_filters": health_prefs.to_dict(),
            "recipe_count": len(final_recipes),
            "recipes": final_recipes,
            "message": f"Found {len(final_recipes)} recipes matching your preferences"
        })

    except Exception as e:
      print("ERROR in /search/text:")
      traceback.print_exc()
      return jsonify({"error": str(e)}), 500


@text_routes.route("/search/cuisines", methods=["GET"])
def get_cuisines():
    """Get list of available cuisines in the dataset"""
    try:
        from modules.recipe_matcher_prod import df, initialize_model
        if df is None:
            initialize_model()
        cuisines = sorted(df['Cuisine'].dropna().unique().tolist())
        return jsonify({
            "cuisines": cuisines,
            "count": len(cuisines)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@text_routes.route("/health/allergens", methods=["GET"])
def get_allergen_list():
    """Get list of recognized allergens"""
    return jsonify({
        "allergens": {
            allergen: keywords
            for allergen, keywords in COMMON_ALLERGENS.items()
        }
    })


@text_routes.route("/health/dietary-types", methods=["GET"])
def get_dietary_types():
    """Get available dietary preference types"""
    return jsonify({
        "dietary_types": list(DIETARY_PREFERENCES.keys())
    })


@text_routes.route("/recipe/<recipe_name>/nutrition", methods=["GET"])
def get_recipe_nutrition(recipe_name):
    """Get detailed nutrition and allergen info for a specific recipe"""
    try:
        recipe_matches = health_matcher.df[
            health_matcher.df['recipe_name'] == recipe_name
        ]

        if len(recipe_matches) == 0:
            return jsonify({"error": "Recipe not found"}), 404

        recipe_idx = recipe_matches.index[0]
        nutrition = health_matcher.get_nutrition_info(recipe_idx)

        return jsonify({
            "recipe_name": recipe_name,
            "nutrition": nutrition
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@text_routes.route("/recipe/<recipe_name>/portions/<float:serving_factor>", methods=["GET"])
def adjust_recipe_portions(recipe_name, serving_factor):
    """
    Adjust recipe portion size and return adjusted nutrition.
    serving_factor: 0.5 (half), 1.0 (original), 2.0 (double), etc.
    """
    try:
        recipe_matches = health_matcher.df[
            health_matcher.df['recipe_name'] == recipe_name
        ]

        if len(recipe_matches) == 0:
            return jsonify({"error": "Recipe not found"}), 404

        recipe_idx = recipe_matches.index[0]
        nutrition = health_matcher.get_nutrition_info(recipe_idx)
        adjusted_nutrition = health_matcher.adjust_portion_size(nutrition, serving_factor)

        return jsonify({
            "recipe_name": recipe_name,
            "serving_factor": serving_factor,
            "original_nutrition": nutrition,
            "adjusted_nutrition": adjusted_nutrition
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
