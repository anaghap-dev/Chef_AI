import json
import os
import re
import google.generativeai as genai

# ==========================
# GOOGLE GENAI CLIENT
# ==========================
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.4,        # lower = more deterministic JSON
        "top_p": 0.9,
        "max_output_tokens": 2048,
    }
)

# ==========================
# HELPERS
# ==========================
def _build_prompt(ingredients, cuisine, category, allergies, cooking_time, top_k):
    if isinstance(allergies, list):
        allergy_str = ", ".join(allergies) if allergies else "none"
    elif isinstance(allergies, str) and allergies.strip():
        allergy_str = allergies.strip()
    else:
        allergy_str = "none"

    cuisine_str  = str(cuisine).strip()  if cuisine  else "any"
    category_str = str(category).strip() if category else "any"
    time_str     = str(int(cooking_time)) if cooking_time else "any"

    return f"""
You are a professional chef AI assistant for ChefAI.

INGREDIENTS:
{ingredients}

Pantry staples always available:
salt, sugar, oil, water, pepper, spices, butter, ghee, garlic, ginger.

User constraints:
Cuisine: {cuisine_str}
Category: {category_str}
Allergies: {allergy_str}
Max cooking time: {time_str} minutes

Generate EXACTLY {top_k} recipes.

STRICT RULES:
- Use ONLY given ingredients + pantry staples
- Respect ALL filters strictly
- No allergens
- Do not exceed cooking time
- Must match cuisine/category

OUTPUT FORMAT:
Return ONLY valid JSON array. No explanation. No markdown.

Schema:
[
  {{
    "rank": 1,
    "recipe_name": "",
    "final_recipe_name": "",
    "ingredients": "",
    "Instructions": "",
    "Detailed_Ingredients": "",
    "Cuisine": "",
    "Category": "",
    "CookingTime": 0,
    "Calories (kcal)": 0.0,
    "Carbohydrates g": 0.0,
    "Protein g": 0.0,
    "Fats g": 0.0,
    "Free Sugar g": 0.0,
    "Fibre g": 0.0,
    "Sodium mg": 0.0,
    "Calcium mg": 0.0,
    "Iron mg": 0.0,
    "similarity_score": 1.0,
    "ingredient_match": "100%",
    "match_type": "AI Generated"
  }}
]
"""


def _safe_float(v):
    try:
        return float(v)
    except:
        return None


def _safe_int(v):
    try:
        return int(v)
    except:
        return None


def _extract_json(text):
    """
    Gemini sometimes adds junk → extract JSON safely.
    """
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # Try extracting JSON block
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise json.JSONDecodeError("No valid JSON found", text, 0)


def _parse_response(raw_text, top_k):
    data = _extract_json(raw_text)

    if not isinstance(data, list):
        data = [data]

    results = []
    for i, r in enumerate(data[:top_k]):
        results.append({
            "rank": _safe_int(r.get("rank", i + 1)),
            "recipe_name": str(r.get("recipe_name", "")).strip(),
            "final_recipe_name": str(r.get("final_recipe_name", "")).strip(),
            "ingredients": str(r.get("ingredients", "")).strip(),
            "Instructions": str(r.get("Instructions", "")).strip(),
            "Detailed_Ingredients": str(r.get("Detailed_Ingredients", "")).strip(),
            "Cuisine": str(r.get("Cuisine", "")).strip(),
            "Category": str(r.get("Category", "")).strip(),
            "CookingTime": _safe_int(r.get("CookingTime")),
            "Calories (kcal)": _safe_float(r.get("Calories (kcal)")),
            "Carbohydrates g": _safe_float(r.get("Carbohydrates g")),
            "Protein g": _safe_float(r.get("Protein g")),
            "Fats g": _safe_float(r.get("Fats g")),
            "Free Sugar g": _safe_float(r.get("Free Sugar g")),
            "Fibre g": _safe_float(r.get("Fibre g")),
            "Sodium mg": _safe_float(r.get("Sodium mg")),
            "Calcium mg": _safe_float(r.get("Calcium mg")),
            "Iron mg": _safe_float(r.get("Iron mg")),
            "similarity_score": 1.0,
            "ingredient_match": "100%",
            "match_type": "AI Generated",
        })

    return results


# ==========================
# PUBLIC API
# ==========================
def get_strict_recipes(
    user_input,
    top_k=3,
    cuisine=None,
    category=None,
    allergies=None,
    cooking_time=None,
):
    if not user_input or not str(user_input).strip():
        return []

    prompt = _build_prompt(
        user_input.strip(),
        cuisine,
        category,
        allergies,
        cooking_time,
        top_k
    )

    try:
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text"):
            print("[ChefAI] Empty Gemini response")
            return []

        raw_text = response.text.strip()

        recipes = _parse_response(raw_text, top_k)

        return recipes

    except json.JSONDecodeError as e:
        print(f"[ChefAI] JSON parse error: {e}")
        return []

    except Exception as e:
        print(f"[ChefAI] Gemini error: {e}")
        return []