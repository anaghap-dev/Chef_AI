import pandas as pd
from flask import Blueprint, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import os
from dotenv import load_dotenv

load_dotenv()

subs_routes = Blueprint("subs_routes", __name__)

# LOAD INGREDIENT DATASET
ingredients_df = pd.read_csv("data/ingredients.csv")

nutrition_cols = [
    "calories",
    "carbs",
    "protein",
    "fats",
    "fibre",
    "sugar"
]

# fill nulls
ingredients_df[nutrition_cols] = ingredients_df[
    nutrition_cols
].fillna(0)

# scale features
scaler = StandardScaler()

scaled_features = scaler.fit_transform(
    ingredients_df[nutrition_cols]
)

@subs_routes.route("/get-substitutes", methods=["POST"])
def get_substitutes():

    data = request.get_json()

    ingredient = data.get("ingredient", "")

    if not ingredient:
        return jsonify({
            "error": "Ingredient is required"
        }), 400

    try:

        # FIND INGREDIENT
        ingredient_row = ingredients_df[
            ingredients_df["ingredient"]
            .str.lower()
            .str.strip()
            == ingredient.lower().strip()
        ]

        if ingredient_row.empty:
            return jsonify({
                "ingredient": ingredient,
                "substitutes": []
            })

        # TARGET VECTOR
        target_vector = scaler.transform(
            ingredient_row[nutrition_cols]
        )

        # COSINE SIMILARITY
        similarities = cosine_similarity(
            target_vector,
            scaled_features
        )[0]

        ingredients_df["similarity"] = similarities

        # REMOVE SAME INGREDIENT
        results = ingredients_df[
            ingredients_df["ingredient"]
            .str.lower()
            != ingredient.lower()
        ]

        # TOP 5 MATCHES
        top_matches = results.sort_values( # type: ignore
            by="similarity",
            ascending=False
        ).head(5)

        substitutes = top_matches[
            "ingredient"
        ].tolist()

        return jsonify({
            "ingredient": ingredient,
            "substitutes": substitutes
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500