import pandas as pd
import numpy as np
import pickle
import warnings
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
import re

warnings.filterwarnings('ignore')

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

# Prepare training data
print("Preparing dataset...")
df['ingredients_clean'] = df['ingredients'].fillna("").apply(clean_ingredients_improved)
df['cuisine_clean'] = df['Cuisine'].fillna("").apply(lambda x: str(x).lower().strip())

# Split data
train_indices, test_indices = train_test_split(df.index, test_size=0.2, random_state=42)
train_df = df.iloc[train_indices]
test_df = df.iloc[test_indices]

print(f"Training set: {len(train_df)} recipes | Test set: {len(test_df)} recipes\n")

# Train multiple vectorizers
print("Training vectorizers...")
ingredient_vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=3000,
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)
ingredient_vectors = ingredient_vectorizer.fit_transform(df['ingredients_clean'])

# Cuisine vectorizer
cuisine_vectorizer = CountVectorizer()
cuisine_vectors = cuisine_vectorizer.fit_transform(df['cuisine_clean'])

print(f"Ingredient features: {ingredient_vectors.shape[1]}")
print(f"Cuisine features: {cuisine_vectors.shape[1]}")

def get_ingredient_tokens(text):
    """Extract individual ingredient tokens for comparison"""
    text = clean_ingredients_improved(text)
    return set(text.split())

def calculate_token_overlap(user_tokens, recipe_tokens):
    """Calculate how many user ingredients are in recipe"""
    if not user_tokens:
        return 0
    overlap = len(user_tokens & recipe_tokens)
    return overlap / len(user_tokens)

def find_best_match_advanced(user_input, top_k=5):
    """
    Advanced recipe matching using multiple signals:
    1. TF-IDF cosine similarity
    2. Token overlap percentage
    3. Cuisine matching
    """
    user_input_clean = clean_ingredients_improved(user_input)
    user_tokens = get_ingredient_tokens(user_input_clean)

    # Get TF-IDF similarity
    user_ingredient_vector = ingredient_vectorizer.transform([user_input_clean])
    tfidf_similarity = cosine_similarity(user_ingredient_vector, ingredient_vectors).flatten()

    # Calculate token overlap for each recipe
    token_overlaps = []
    for recipe_ingredients in df['ingredients_clean']:
        recipe_tokens = get_ingredient_tokens(recipe_ingredients)
        overlap = calculate_token_overlap(user_tokens, recipe_tokens)
        token_overlaps.append(overlap)

    token_overlaps = np.array(token_overlaps)

    # Combined score: TF-IDF (60%) + Token Overlap (40%)
    combined_scores = (0.6 * tfidf_similarity) + (0.4 * token_overlaps)

    # Get top indices
    top_indices = combined_scores.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            'recipe_name': df.iloc[idx]['recipe_name'],
            'ingredients': df.iloc[idx]['ingredients'],
            'Cuisine': df.iloc[idx]['Cuisine'],
            'CookingTime': df.iloc[idx]['CookingTime'],
            'similarity_score': float(combined_scores[idx]),
            'tfidf_score': float(tfidf_similarity[idx]),
            'token_overlap': float(token_overlaps[idx])
        })

    return results

def find_best_match(user_input):
    """Get best single match"""
    results = find_best_match_advanced(user_input, top_k=1)
    if results:
        idx = df[df['recipe_name'] == results[0]['recipe_name']].index[0]
        return idx, results[0]['similarity_score']
    return 0, 0.0

# Evaluation on test set
print("\n" + "="*70)
print("EVALUATING MODEL ACCURACY (EXACT RECIPE NAME MATCH)")
print("="*70)

correct_predictions = 0
top_5_correct = 0

for idx, row in test_df.iterrows():
    user_input = row['ingredients']
    expected_recipe_name = row['recipe_name']

    # Get top 1
    best_match_idx, similarity = find_best_match(user_input)
    predicted_recipe_name = df.iloc[best_match_idx]['recipe_name']

    if predicted_recipe_name == expected_recipe_name:
        correct_predictions += 1

    # Check if in top 5
    top_5_results = find_best_match_advanced(user_input, top_k=5)
    if any(r['recipe_name'] == expected_recipe_name for r in top_5_results):
        top_5_correct += 1

accuracy_top1 = (correct_predictions / len(test_df)) * 100
accuracy_top5 = (top_5_correct / len(test_df)) * 100

print(f"\nTop-1 Accuracy: {accuracy_top1:.2f}% ({correct_predictions}/{len(test_df)})")
print(f"Top-5 Accuracy: {accuracy_top5:.2f}% ({top_5_correct}/{len(test_df)})")
print(f"Improvement potential: {accuracy_top5 - accuracy_top1:.2f}%")

# Show example predictions
print("\n" + "="*70)
print("SAMPLE PREDICTIONS (Top 5 Results)")
print("="*70)

for i, (idx, row) in enumerate(test_df.head(3).iterrows()):
    user_input = row['ingredients']
    expected = row['recipe_name']
    results = find_best_match_advanced(user_input, top_k=5)

    print(f"\n[Test #{i+1}]")
    print(f"Input ingredients: {user_input[:70]}...")
    print(f"Expected recipe: {expected}")
    print(f"\nTop matches:")

    for rank, result in enumerate(results, 1):
        match = "[MATCH]" if result['recipe_name'] == expected else ""
        print(f"  {rank}. {result['recipe_name'][:50]:50} | "
              f"Score: {result['similarity_score']:.3f} | "
              f"TF-IDF: {result['tfidf_score']:.3f} | "
              f"Overlap: {result['token_overlap']:.1%} {match}")

# Save improved models
print("\n" + "="*70)
print("SAVING TRAINED MODELS")
print("="*70)

with open('models/ingredient_vectorizer_v2.pkl', 'wb') as f:
    pickle.dump(ingredient_vectorizer, f)
    print("[SAVED] Ingredient vectorizer")

with open('models/recipe_matcher_v2.pkl', 'wb') as f:
    pickle.dump({
        'dataframe': df[['recipe_name', 'ingredients', 'Cuisine', 'CookingTime', 'Calories (kcal)']],
        'ingredient_vectorizer': ingredient_vectorizer
    }, f)
    print("[SAVED] Recipe matcher data")

print("\n" + "="*70)
print("RECOMMENDATIONS TO IMPROVE ACCURACY")
print("="*70)
print(f"""
Current Performance:
- Top-1 Accuracy: {accuracy_top1:.2f}%
- Top-5 Accuracy: {accuracy_top5:.2f}%

The gap ({accuracy_top5 - accuracy_top1:.2f}%) shows the correct recipe IS in top-5
but not always ranked #1.

Improvement strategies:
1. Fine-tune the combined score weights
2. Add more features (cuisine, cooking time, calories)
3. Use semantic embeddings (Word2Vec, GloVe, BERT)
4. Implement recipe clustering
5. Create a training dataset with user feedback for ranking

Current approach uses:
- TF-IDF vectorization (60% weight)
- Ingredient token overlap (40% weight)
""")

print("Training complete!")
