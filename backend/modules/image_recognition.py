import os
from google import genai
from google.genai import types
from PIL import Image
import io

def detect_ingredients(image_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Detect mime type from extension
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    prompt = (
        "Look at this image. Identify all the food ingredients or grocery items visible. "
        "Return ONLY a comma-separated list of ingredient names in lowercase English, nothing else. "
        "Example: tomato, onion, garlic, chicken breast, bell pepper"
    )

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
    )

    raw = response.text.strip()
    items = [item.strip().lower() for item in raw.split(",") if item.strip()]
    return items
