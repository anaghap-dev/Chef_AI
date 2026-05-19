export const normalizeRecipe = (recipe, fullRecipe = null) => {
  return {
    name:
      recipe?.recipe_name ||
      recipe?.final_recipe_name ||
      fullRecipe?.recipe_name,

    ingredients:
      recipe?.ingredients || fullRecipe?.ingredients || "",

    detailedIngredients:
      recipe?.Detailed_Ingredients ||
      fullRecipe?.Detailed_Ingredients ||
      fullRecipe?.detailed_ingredients ||
      "",

    instructions:
      recipe?.Instructions || fullRecipe?.Instructions || "",

    cuisine:
      recipe?.Cuisine || fullRecipe?.Cuisine || "",

    category:
      recipe?.Category || fullRecipe?.Category || "",

    cookingTime:
      recipe?.CookingTime ?? fullRecipe?.CookingTime ?? null,

    calories:
      recipe?.["Calories (kcal)"] ??
      fullRecipe?.["Calories (kcal)"] ??
      null,

    carbs:
      recipe?.["Carbohydrates (g)"] ??
      fullRecipe?.["Carbohydrates (g)"] ??
      recipe?.["Carbohydrates g"] ??
      fullRecipe?.["Carbohydrates g"] ??
      null,

    protein:
      recipe?.["Protein (g)"] ??
      fullRecipe?.["Protein (g)"] ??
      recipe?.["Protein g"] ??
      fullRecipe?.["Protein g"] ??
      null,

    fats:
      recipe?.["Fats (g)"] ??
      fullRecipe?.["Fats (g)"] ??
      recipe?.["Fats g"] ??
      fullRecipe?.["Fats g"] ??
      null,

    sugar:
      recipe?.["Free Sugar (g)"] ??
      fullRecipe?.["Free Sugar (g)"] ??
      recipe?.["Free Sugar g"] ??
      fullRecipe?.["Free Sugar g"] ??
      null,

    fibre:
      recipe?.["Fibre (g)"] ??
      fullRecipe?.["Fibre (g)"] ??
      recipe?.["Fibre g"] ??
      fullRecipe?.["Fibre g"] ??
      null,

    sodium:
      recipe?.["Sodium (mg)"] ??
      fullRecipe?.["Sodium (mg)"] ??
      recipe?.["Sodium mg"] ??
      fullRecipe?.["Sodium mg"] ??
      null,

      image:
  recipe?.image ||
  fullRecipe?.image ||
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
  
    calcium:
      recipe?.["Calcium (mg)"] ??
      fullRecipe?.["Calcium (mg)"] ??
      recipe?.["Calcium mg"] ??
      fullRecipe?.["Calcium mg"] ??
      null,

    iron:
      recipe?.["Iron (mg)"] ??
      fullRecipe?.["Iron (mg)"] ??
      recipe?.["Iron mg"] ??
      fullRecipe?.["Iron mg"] ??
      null,
  };
};