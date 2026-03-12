from flask import Blueprint, request, jsonify
from modules.speech_to_text import voice_to_text

voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/voice-input", methods=["POST"])
def voice_input():

    file = request.files["audio"]

    text = voice_to_text(file)

    return jsonify({"text": text})