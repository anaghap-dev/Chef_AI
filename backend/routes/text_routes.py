from flask import Blueprint, request, jsonify
from modules.recipe_matcher import recommend_recipes

text_routes = Blueprint("text_routes", __name__)


@text_routes.route("/search/text", methods=["POST"])
def search_by_text():

    data = request.get_json()

    ingredients = data.get("ingredients", "")

    recipes = recommend_recipes(ingredients)

    return jsonify({
        "input_ingredients": ingredients,
        "recipes": recipes
    })