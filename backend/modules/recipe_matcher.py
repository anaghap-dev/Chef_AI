import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_recipes(user_ingredients):

    with open("data/recipes.json") as f:
        recipes = json.load(f)

    recipe_texts = [" ".join(r["ingredients"]) for r in recipes]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(recipe_texts + [" ".join(user_ingredients)])

    similarity = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    scores = similarity.flatten()

    ranked = sorted(zip(recipes, scores), key=lambda x: x[1], reverse=True)

    return [r[0] for r in ranked[:5]]