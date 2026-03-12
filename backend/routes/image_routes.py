from flask import Blueprint, request, jsonify
from modules.image_recognition import detect_ingredients
import os

image_bp = Blueprint("image", __name__)

@image_bp.route("/image-input", methods=["POST"])
def image_input():

    file = request.files["image"]

    path = os.path.join("uploads", file.filename)

    file.save(path)

    ingredients = detect_ingredients(path)

    return jsonify({"ingredients": ingredients})