import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.text_processing import preprocess_ingredients

# Load dataset once
df = pd.read_csv("data/recipes.csv")

# Clean ingredients column
df["ingredients"] = df["ingredients"].fillna("").apply(preprocess_ingredients)

# Train TF-IDF model once
vectorizer = TfidfVectorizer( ngram_range=(1,2),stop_words="english",  min_df=2)
ingredient_vectors = vectorizer.fit_transform(df["ingredients"])

print("Recipe model loaded")
print("Total recipes:", ingredient_vectors.shape[0])


def recommend_recipes(user_input):

    user_input = preprocess_ingredients(user_input)

    user_vector = vectorizer.transform([user_input])

    similarity = cosine_similarity(user_vector, ingredient_vectors)

    scores = similarity.flatten()

    top_indices = scores.argsort()[-5:][::-1]

    results = df.iloc[top_indices]

    return results.to_dict(orient="records")