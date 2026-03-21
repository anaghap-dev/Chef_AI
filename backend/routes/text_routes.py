from flask import Blueprint, request, jsonify
from modules.recipe_matcher_prod import recommend_recipes

text_routes = Blueprint("text_routes", __name__)


@text_routes.route("/search/text", methods=["POST"])
def search_by_text():
    """
    Search for recipes by ingredients.

    Request JSON:
    {
        "ingredients": "chicken, garlic, onion",
        "cuisine": "Italian",  // optional
        "top_k": 5  // optional
    }
    """
    data = request.get_json()
    ingredients = data.get("ingredients", "")
    cuisine = data.get("cuisine")
    top_k = data.get("top_k", 5)

    if not ingredients.strip():
        return jsonify({"error": "Please provide ingredients"}), 400

    recipes = recommend_recipes(ingredients, cuisine=cuisine, top_k=top_k)

    return jsonify({
        "input_ingredients": ingredients,
        "cuisine_filter": cuisine,
        "recipe_count": len(recipes),
        "recipes": recipes
    })