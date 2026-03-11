import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Function to clean ingredient text
def clean_ingredients(text):
    text = str(text).lower()
    text = text.replace(",", " ")
    text = text.replace("  ", " ")
    return text


# Load dataset
df = pd.read_csv("data/recipes.csv")

# Clean ingredient column
df["ingredients"] = df["ingredients"].fillna("").apply(clean_ingredients)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()

# Train the model
ingredient_vectors = vectorizer.fit_transform(df["ingredients"])

print("Model training completed")
print("Number of recipes:", ingredient_vectors.shape[0])


# Function to recommend recipes
def recommend_recipes(user_input):

    # Clean user input
    user_input = clean_ingredients(user_input)

    # Convert user ingredients to vector
    user_vector = vectorizer.transform([user_input])

    # Compute similarity
    similarity = cosine_similarity(user_vector, ingredient_vectors)

    # Get top 5 matching recipes
    top_indices = similarity.argsort()[0][-5:][::-1]

    # Get full recipe data
    results = df.iloc[top_indices]

    return results.to_dict(orient="records")


# Test the model
user_ingredients = input("\nEnter ingredients: ")

results = recommend_recipes(user_ingredients)

print("\nRecommended Recipes:\n")

for recipe in results:
    print("\nRecipe:", recipe["recipe_name"])
    print("Cuisine:", recipe.get("Cuisine", "N/A"))
    print("Ingredients:", recipe["ingredients"])