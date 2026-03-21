import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import warnings

warnings.filterwarnings('ignore')

# Configuration
MODEL_PATH = 'models/recipe_matcher_prod.pkl'
VECTORIZER_PATH = 'models/vectorizer_prod.pkl'

# Global variables
df = None
vectorizer = None
model_loaded = False

def clean_ingredients(text):
    """Clean and normalize ingredient text"""
    text = str(text).lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def initialize_model():
    """Load or train the recipe matching model"""
    global df, vectorizer, model_loaded

    try:
        # Try loading existing model
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            print("[MODEL] Loading existing trained model...")
            with open(MODEL_PATH, 'rb') as f:
                df = pickle.load(f)
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
            model_loaded = True
            print(f"[MODEL] Loaded {len(df)} recipes from saved model")
            return
    except Exception as e:
        print(f"[WARNING] Could not load saved model: {e}")

    # Train new model
    print("[MODEL] Training new model...")
    df = pd.read_csv("data/recipes.csv")

    # Clean ingredients
    df['ingredients_clean'] = df['ingredients'].fillna("").apply(clean_ingredients)

    # Train TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3000,
        min_df=2,
        max_df=0.8,
        sublinear_tf=True
    )
    vectorizer.fit(df['ingredients_clean'])

    # Save model
    os.makedirs('models', exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(df, f)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)

    model_loaded = True
    print(f"[MODEL] Model trained and saved with {len(df)} recipes")

def get_ingredient_tokens(text):
    """Extract ingredient tokens for comparison"""
    text = clean_ingredients(text)
    return set(text.split())

def calculate_scores(user_vector, user_tokens, cuisine_filter=None):
    """
    Calculate composite similarity scores for all recipes.
    Uses:
    - TF-IDF cosine similarity (60%)
    - Token overlap percentage (40%)
    """
    # TF-IDF similarity
    all_vectors = vectorizer.transform(df['ingredients_clean'])
    tfidf_scores = cosine_similarity(user_vector, all_vectors).flatten()

    # Token overlap
    token_scores = []
    for ing in df['ingredients_clean']:
        recipe_tokens = get_ingredient_tokens(ing)
        if user_tokens:
            overlap = len(user_tokens & recipe_tokens) / len(user_tokens)
        else:
            overlap = 0
        token_scores.append(overlap)
    token_scores = np.array(token_scores)

    # Cuisine filter bonus (for disambiguation)
    cuisine_bonus = np.zeros(len(df))
    if cuisine_filter:
        cuisine_filter_lower = str(cuisine_filter).lower().strip()
        for i, recipe_cuisine in enumerate(df['Cuisine']):
            if isinstance(recipe_cuisine, str):
                if cuisine_filter_lower.lower() in recipe_cuisine.lower():
                    cuisine_bonus[i] = 0.2  # 20% bonus

    # Composite score
    composite = (0.6 * tfidf_scores) + (0.4 * token_scores) + cuisine_bonus

    return composite, tfidf_scores, token_scores

def recommend_recipes(user_input, cuisine=None, top_k=5):
    """
    Recommend recipes based on user ingredients.

    Args:
        user_input (str): Comma-separated or space-separated ingredients
        cuisine (str, optional): Filter by cuisine type (e.g., "Italian", "Indian")
        top_k (int): Number of top recommendations to return

    Returns:
        list: List of dictionaries with recipe recommendations
    """
    if not model_loaded:
        initialize_model()

    # Clean user input
    user_input_clean = clean_ingredients(user_input)
    user_tokens = get_ingredient_tokens(user_input_clean)

    # Vectorize user input
    user_vector = vectorizer.transform([user_input_clean])

    # Calculate scores
    composite_scores, tfidf_scores, token_scores = calculate_scores(
        user_vector,
        user_tokens,
        cuisine_filter=cuisine
    )

    # Get top-k indices
    top_indices = composite_scores.argsort()[-top_k:][::-1]

    # Build results
    results = []
    for rank, idx in enumerate(top_indices, 1):
        recipe = df.iloc[idx]
        results.append({
            'rank': int(rank),
            'recipe_name': str(recipe['recipe_name']),
            'ingredients': str(recipe['ingredients']),
            'Cuisine': str(recipe['Cuisine']),
            'CookingTime': int(recipe['CookingTime']),
            'Calories (kcal)': float(recipe['Calories (kcal)']) if pd.notna(recipe['Calories (kcal)']) else None,
            'similarity_score': float(composite_scores[idx]),
            'ingredient_match': f"{float(token_scores[idx]):.1%}",
            'match_type': 'Exact Match' if composite_scores[idx] > 0.95 else 'Good Match' if composite_scores[idx] > 0.75 else 'Partial Match'
        })

    return results

# Initialize model when module is loaded
print("[INIT] Initializing recipe matcher...")
initialize_model()
print("[INIT] Recipe matcher ready!")
