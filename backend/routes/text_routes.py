from flask import Blueprint, request, jsonify
from modules.text_processing import preprocess_ingredients
from modules.recipe_matcher import find_recipes

text_bp = Blueprint("text", __name__)

@text_bp.route("/text-input", methods=["POST"])
def text_input():

    data = request.json

    ingredients = preprocess_ingredients(data["ingredients"])

    recipes = find_recipes(ingredients)

    return jsonify(recipes)