import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import re

# Load dataset
df = pd.read_csv("data/recipes.csv")

def clean_ingredients_improved(text):
    """Improved ingredient cleaning that preserves important terms"""
    text = str(text).lower()
    # Keep important cooking terms
    text = re.sub(r'(?i)(tsp|teaspoon|tbsp|tablespoon|cup|pinch|dash)', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_cuisine(text):
    """Clean cuisine field"""
    return str(text).lower().strip()

def clean_instructions(text):
    """Clean instructions - extract key action words"""
    text = str(text).lower()
    # Keep only letters and spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Prepare training data
print("Preparing dataset...")
df['ingredients_clean'] = df['ingredients'].fillna("").apply(clean_ingredients_improved)
df['cuisine_clean'] = df['Cuisine'].fillna("").apply(clean_cuisine)
df['instructions_clean'] = df['Instructions'].fillna("").apply(clean_instructions)

# Combine features with weights
df['combined_features'] = (
    df['ingredients_clean'] + " " +
    df['cuisine_clean'] * 2 + " " +  # Weight cuisine more heavily
    df['instructions_clean']
)

# Split data maintaining recipe diversity
train_indices, test_indices = train_test_split(
    df.index,
    test_size=0.2,
    random_state=42
)

train_df = df.iloc[train_indices]
test_df = df.iloc[test_indices]

print(f"Training set: {len(train_df)} recipes")
print(f"Test set: {len(test_df)} recipes")

# Train vectorizer on full data for consistency
print("\nTraining TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=5000,
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)

# Fit on combined features
combined_vectors = vectorizer.fit_transform(df['combined_features'])

# Also create ingredient-only vectors
ingredient_vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=3000,
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)
ingredient_vectors = ingredient_vectorizer.fit_transform(df['ingredients_clean'])

print("Vectorizer trained")
print(f"Feature dimension: {combined_vectors.shape[1]}")

def find_best_match(user_input, top_k=1):
    """Find the best matching recipe for user input"""
    user_input_clean = clean_ingredients_improved(user_input)
    user_vector = ingredient_vectorizer.transform([user_input_clean])

    similarity = cosine_similarity(user_vector, ingredient_vectors)
    scores = similarity.flatten()

    best_idx = scores.argmax()
    return best_idx, scores[best_idx]

def recommend_recipes(user_input, top_k=5):
    """Recommend top K recipes"""
    user_input_clean = clean_ingredients_improved(user_input)
    user_vector = ingredient_vectorizer.transform([user_input_clean])

    similarity = cosine_similarity(user_vector, ingredient_vectors)
    scores = similarity.flatten()

    top_indices = scores.argsort()[-top_k:][::-1]
    results = df.iloc[top_indices][['recipe_name', 'ingredients', 'Cuisine', 'CookingTime', 'Calories (kcal)']].copy()
    results['similarity_score'] = scores[top_indices]

    return results.to_dict(orient="records")

# Evaluation on test set
print("\n" + "="*60)
print("EVALUATING MODEL ACCURACY")
print("="*60)

correct_predictions = 0
total_tests = len(test_df)

for idx, row in test_df.iterrows():
    user_input = row['ingredients']
    expected_recipe_name = row['recipe_name']

    best_match_idx, similarity = find_best_match(user_input)
    predicted_recipe_name = df.iloc[best_match_idx]['recipe_name']

    if predicted_recipe_name == expected_recipe_name:
        correct_predictions += 1

accuracy = (correct_predictions / total_tests) * 100

print(f"\nTest Set Results:")
print(f"Correct predictions: {correct_predictions}/{total_tests}")
print(f"Accuracy: {accuracy:.2f}%")
print(f"Missing matches: {total_tests - correct_predictions}")

# Show examples of mismatches
print("\n" + "="*60)
print("SAMPLE PREDICTIONS")
print("="*60)

for i, (idx, row) in enumerate(test_df.head(5).iterrows()):
    user_input = row['ingredients']
    best_match_idx, similarity = find_best_match(user_input)
    predicted = df.iloc[best_match_idx]['recipe_name']
    expected = row['recipe_name']
    match_status = "[OK]" if predicted == expected else "[MISS]"

    print(f"\n#{i+1} {match_status}")
    print(f"  Input: {user_input[:60]}...")
    print(f"  Expected: {expected}")
    print(f"  Predicted: {predicted}")
    print(f"  Similarity: {similarity:.3f}")

# Save models
print("\n" + "="*60)
print("SAVING MODELS")
print("="*60)

with open('models/ingredient_vectorizer.pkl', 'wb') as f:
    pickle.dump(ingredient_vectorizer, f)
    print("✓ Ingredient vectorizer saved")

with open('models/recipe_metadata.pkl', 'wb') as f:
    pickle.dump(df[['recipe_name', 'ingredients', 'Cuisine', 'CookingTime', 'Calories (kcal)']], f)
    print("✓ Recipe metadata saved")

print("\nTraining complete!")
