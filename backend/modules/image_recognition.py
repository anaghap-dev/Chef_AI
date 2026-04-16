import os
import re
from google import genai
from PIL import Image


def detect_ingredients(image_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            prompt = (
                "Identify all food ingredients or grocery items visible in this image. "
                "Return ONLY a comma-separated list of ingredient names in lowercase English. "
                "Do not add any extra words, punctuation, or explanation. "
                "Example: tomato, onion, garlic, chicken breast, bell pepper"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image, prompt],
            )
    except Exception as e:
        message = str(e)
        if "PERMISSION_DENIED" in message or "leaked" in message.lower():
            raise RuntimeError(
                "Image recognition failed: invalid or leaked Gemini API key. "
                "Update backend/.env with a valid GEMINI_API_KEY."
            ) from e
        raise RuntimeError(f"Image recognition failed: {e}") from e

    raw = getattr(response, "text", "") or ""
    raw = raw.strip()
    if not raw:
        return []

    raw = re.sub(r"[\n;]+", ",", raw)
    items = [item.strip().lower() for item in raw.split(",") if item.strip()]

    if any(phrase in raw.lower() for phrase in ["unable", "can't", "cannot", "no ingredients", "cannot identify"]):
        return []

    return items
