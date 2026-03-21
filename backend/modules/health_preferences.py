"""
Health & Dietary Preferences System
Handles dietary restrictions, allergies, nutritional needs, and portion sizing
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import pickle
import os

# Dietary preferences and allergen mappings
DIETARY_PREFERENCES = {
    'vegetarian': 'Veg',
    'non_vegetarian': 'Non-veg',
    'vegan': 'Veg',  # Approximate - would need more data for exact vegan recipes
}

# Common allergens that might be in recipes
COMMON_ALLERGENS = {
    'eggs': ['egg', 'eggs'],
    'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'paneer', 'ghee'],
    'peanuts': ['peanut', 'groundnut'],
    'tree_nuts': ['almonds', 'cashew', 'walnut', 'pistachio', 'coconut'],
    'soy': ['soy', 'tofu', 'soybean'],
    'wheat': ['wheat', 'flour', 'bread', 'pasta'],
    'fish': ['fish', 'salmon', 'tuna', 'cod'],
    'shellfish': ['shrimp', 'prawn', 'crab', 'oyster', 'lobster'],
    'sesame': ['sesame', 'tahini'],
}

class HealthPreferences:
    """User health and dietary preferences"""

    def __init__(self):
        self.dietary_type = None  # 'vegetarian', 'non_vegetarian', 'vegan'
        self.allergies = []  # List of allergen names
        self.max_calories = None  # Maximum calories per serving
        self.max_sodium = None  # Maximum sodium (mg) per serving
        self.min_protein = None  # Minimum protein (g) per serving
        self.avoid_ingredients = []  # User's preferred ingredients to avoid

    def to_dict(self):
        return {
            'dietary_type': self.dietary_type,
            'allergies': self.allergies,
            'max_calories': self.max_calories,
            'max_sodium': self.max_sodium,
            'min_protein': self.min_protein,
            'avoid_ingredients': self.avoid_ingredients
        }

class HealthAwareRecipeMatcher:
    """Recipe matcher with health and dietary filtering"""

    def __init__(self, df):
        self.df = df
        self.df['ingredients_lower'] = df['ingredients'].fillna("").str.lower()
        self.df['Category_clean'] = df['Category'].fillna("").str.lower()

    def detect_allergens(self, recipe_idx: int) -> List[str]:
        """Detect which allergens are in a recipe"""
        ingredients = self.df.iloc[recipe_idx]['ingredients_lower']
        detected = []

        for allergen_name, keywords in COMMON_ALLERGENS.items():
            for keyword in keywords:
                if keyword.lower() in ingredients:
                    detected.append(allergen_name)
                    break

        return list(set(detected))  # Remove duplicates

    def check_dietary_compatibility(self, recipe_idx: int, preferences: HealthPreferences) -> bool:
        """Check if recipe matches dietary preferences"""

        # Dietary type check
        if preferences.dietary_type:
            expected_category = DIETARY_PREFERENCES.get(preferences.dietary_type, 'Veg')
            recipe_category = self.df.iloc[recipe_idx]['Category_clean']

            if preferences.dietary_type == 'vegetarian' and 'veg' not in recipe_category:
                return False
            if preferences.dietary_type == 'non_vegetarian' and 'veg' in recipe_category:
                # Non-veg can include veg recipes, so this is okay
                pass

        # Allergy check
        if preferences.allergies:
            recipe_allergens = self.detect_allergens(recipe_idx)
            for allergen in preferences.allergies:
                if allergen in recipe_allergens:
                    return False

        # Ingredient avoidance
        if preferences.avoid_ingredients:
            ingredients = self.df.iloc[recipe_idx]['ingredients_lower']
            for avoid_ing in preferences.avoid_ingredients:
                if avoid_ing.lower() in ingredients:
                    return False

        return True

    def check_nutritional_requirements(self, recipe_idx: int, preferences: HealthPreferences) -> bool:
        """Check if recipe meets nutritional constraints"""

        if preferences.max_calories:
            calories = self.df.iloc[recipe_idx]['Calories (kcal)']
            if pd.notna(calories) and calories > preferences.max_calories:
                return False

        if preferences.max_sodium:
            sodium = self.df.iloc[recipe_idx]['Sodium (mg)']
            if pd.notna(sodium) and sodium > preferences.max_sodium:
                return False

        if preferences.min_protein:
            protein = self.df.iloc[recipe_idx]['Protein (g)']
            if pd.notna(protein) and protein < preferences.min_protein:
                return False

        return True

    def filter_recipes(self, recipe_indices: List[int],
                      preferences: HealthPreferences) -> List[int]:
        """Filter recipes based on health preferences"""

        filtered = []
        for idx in recipe_indices:
            if (self.check_dietary_compatibility(idx, preferences) and
                self.check_nutritional_requirements(idx, preferences)):
                filtered.append(idx)

        return filtered

    def get_nutrition_info(self, recipe_idx: int) -> Dict:
        """Get nutritional information for a recipe"""
        recipe = self.df.iloc[recipe_idx]

        nutrition_cols = ['Calories (kcal)', 'Protein (g)', 'Carbohydrates (g)',
                         'Fats (g)', 'Fibre (g)', 'Sodium (mg)', 'Calcium (mg)', 'Iron (mg)']

        nutrition = {}
        for col in nutrition_cols:
            value = recipe[col]
            nutrition[col] = float(value) if pd.notna(value) else None

        nutrition['allergens'] = self.detect_allergens(recipe_idx)

        return nutrition

    def adjust_portion_size(self, nutrition_info: Dict, factor: float) -> Dict:
        """
        Adjust nutrition values based on portion size
        factor: 1.0 = original, 0.5 = half, 2.0 = double
        """
        adjusted = {}

        scaling_fields = ['Calories (kcal)', 'Protein (g)', 'Carbohydrates (g)',
                         'Fats (g)', 'Fibre (g)', 'Sodium (mg)', 'Calcium (mg)', 'Iron (mg)']

        for key, value in nutrition_info.items():
            if key in scaling_fields and value is not None:
                adjusted[key] = value * factor
            else:
                adjusted[key] = value

        return adjusted

def load_health_matcher():
    """Load the health-aware recipe matcher using the same data as recipe matcher"""
    # Load from the same source as recipe_matcher_prod to ensure consistency
    import pickle
    import os

    try:
        # Try to load from saved model first (has full recipe data)
        model_path = 'models/recipe_matcher_prod.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                df = pickle.load(f)
            print("[HEALTH] Loaded recipes from saved model")
        else:
            # Fallback to CSV
            df = pd.read_csv("data/recipes.csv")
            print("[HEALTH] Loaded recipes from CSV")
    except Exception as e:
        print(f"[HEALTH] Error loading models: {e}, using CSV as fallback")
        df = pd.read_csv("data/recipes.csv")

    return HealthAwareRecipeMatcher(df)

# Initialize on module load
health_matcher = load_health_matcher()
print("[HEALTH] Health & Dietary Preferences system initialized")
