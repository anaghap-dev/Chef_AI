from flask import Blueprint, request, jsonify
from modules.image_recognition import detect_ingredients
import os

image_bp = Blueprint("image", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@image_bp.route("/image-input", methods=["POST"])
def image_input():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    filename = file.filename
    if not filename:
        return jsonify({"error": "Empty filename"}), 400

    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        ingredients = detect_ingredients(path)
        return jsonify({"ingredients": ingredients})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(path):
            os.remove(path)
