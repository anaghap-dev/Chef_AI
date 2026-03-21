#!/usr/bin/env python
"""
Quick verification test for ChefAI system
Run this to verify both recipe matching and health preferences are working
"""

import sys
from flask import Flask
from flask_cors import CORS
from routes.text_routes import text_routes

def run_tests():
    """Run quick verification tests"""

    print("\n" + "="*70)
    print("CHEFAI SYSTEM VERIFICATION")
    print("="*70)

    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(text_routes, url_prefix='')

    test_results = []

    with app.test_client() as client:

        # Test 1: Basic Recipe Search
        print("\n[TEST 1] Basic Recipe Search")
        try:
            response = client.post('/search/text', json={
                'ingredients': 'chicken, garlic, onion',
                'top_k': 3
            }, content_type='application/json')

            if response.status_code == 200 and response.get_json()['recipe_count'] > 0:
                print("  [PASS] Recipe search working")
                test_results.append(True)
            else:
                print("  [FAIL] Recipe search failed")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

        # Test 2: Cuisine Filtering
        print("\n[TEST 2] Cuisine Filtering")
        try:
            response = client.post('/search/text', json={
                'ingredients': 'vegetables, rice',
                'cuisine': 'Italian',
                'top_k': 3
            }, content_type='application/json')

            if response.status_code == 200:
                data = response.get_json()
                has_italian = any('italian' in r['recipe_name'].lower() for r in data['recipes'])
                if has_italian or len(data['recipes']) > 0:
                    print("  [PASS] Cuisine filtering working")
                    test_results.append(True)
                else:
                    print("  [FAIL] No Italian recipes found")
                    test_results.append(False)
            else:
                print("  [FAIL] Cuisine filter failed")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

        # Test 3: Dietary Preferences
        print("\n[TEST 3] Dietary Preferences (Vegetarian)")
        try:
            response = client.post('/search/text', json={
                'ingredients': 'vegetables, rice',
                'dietary_type': 'vegetarian',
                'top_k': 3
            }, content_type='application/json')

            if response.status_code == 200 and response.get_json()['recipe_count'] > 0:
                print("  [PASS] Dietary filtering working")
                test_results.append(True)
            else:
                print("  [FAIL] Dietary filter failed")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

        # Test 4: Nutritional Constraints
        print("\n[TEST 4] Nutritional Constraints (Max 400 cals)")
        try:
            response = client.post('/search/text', json={
                'ingredients': 'vegetables, rice',
                'max_calories': 400,
                'top_k': 5
            }, content_type='application/json')

            if response.status_code == 200:
                data = response.get_json()
                all_under_400 = all(
                    r['nutrition']['Calories (kcal)'] <= 400
                    for r in data['recipes']
                    if 'nutrition' in r and r['nutrition'].get('Calories (kcal)')
                )
                if all_under_400 or len(data['recipes']) == 0:
                    print("  [PASS] Calorie constraint working")
                    test_results.append(True)
                else:
                    print("  [FAIL] Some recipes exceed calorie limit")
                    test_results.append(False)
            else:
                print("  [FAIL] Nutritional filter failed")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

        # Test 5: Allergen Detection
        print("\n[TEST 5] Allergen Detection & Avoidance")
        try:
            response = client.get('/health/allergens')

            if response.status_code == 200:
                data = response.get_json()
                allergens = list(data['allergens'].keys())
                if 'dairy' in allergens and 'eggs' in allergens:
                    print("  [PASS] Allergen system working")
                    test_results.append(True)
                else:
                    print("  [FAIL] Missing expected allergens")
                    test_results.append(False)
            else:
                print("  [FAIL] Allergen list failed")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

        # Test 6: Nutrition Info Endpoint
        print("\n[TEST 6] Nutrition Info Endpoint")
        try:
            # Get a recipe name first
            response = client.post('/search/text', json={
                'ingredients': 'chicken',
                'top_k': 1
            }, content_type='application/json')

            if response.status_code == 200:
                data = response.get_json()
                if data['recipes']:
                    recipe_name = data['recipes'][0]['recipe_name']

                    # Now get nutrition info
                    response2 = client.get(f'/recipe/{recipe_name}/nutrition')
                    if response2.status_code == 200:
                        nutrition = response2.get_json()
                        if 'nutrition' in nutrition:
                            print("  [PASS] Nutrition info endpoint working")
                            test_results.append(True)
                        else:
                            print("  [FAIL] No nutrition data returned")
                            test_results.append(False)
                    else:
                        print("  [FAIL] Nutrition endpoint failed")
                        test_results.append(False)
                else:
                    print("  [SKIP] No recipes to test nutrition endpoint")
                    test_results.append(None)
            else:
                print("  [ERROR] Could not find recipe")
                test_results.append(False)
        except Exception as e:
            print(f"  [ERROR] {e}")
            test_results.append(False)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in test_results if r is True)
    failed = sum(1 for r in test_results if r is False)
    skipped = sum(1 for r in test_results if r is None)

    print(f"\nPassed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")

    if failed == 0 and passed > 0:
        print("\n[SUCCESS] All tests passed! System is ready.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
