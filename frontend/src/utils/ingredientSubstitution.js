// 🔁 Substitution dictionary
const substitutionMap = {
  milk: ["soy milk", "almond milk", "coconut milk"],
  butter: ["margarine", "olive oil"],
  egg: ["flaxseed", "banana"],
  sugar: ["honey", "jaggery"],
  rice: ["quinoa", "cauliflower rice"],
  wheat: ["rice flour", "oats flour"],
  cream: ["yogurt", "coconut cream"],
  cheese: ["tofu", "nutritional yeast"],
  chicken: ["tofu", "paneer"],
  beef: ["mushroom", "soy chunks"],
  onion: ["shallots", "leek"],
  garlic: ["garlic powder"],
  tomato: ["tomato paste", "canned tomatoes"]
};

// 🧹 Normalize text
const clean = (text) => {
  return text?.toLowerCase().trim();
};

// 🧩 Convert string → array
const splitIngredients = (ingredients) => {
  if (!ingredients) return [];

  return ingredients
    .split(",")
    .map((item) => clean(item))
    .filter(Boolean);
};

// 🔍 Find substitution using partial match
const findSubstitution = (ingredient) => {
  for (let key in substitutionMap) {
    if (ingredient.includes(key)) {
      return {
        ingredient,
        substitutes: substitutionMap[key]
      };
    }
  }
  return null;
};

// 🚀 MAIN FUNCTION
export const getSubstitutions = (recipeIngredients, userIngredients) => {
  const recipeList = splitIngredients(recipeIngredients);
  const userList = splitIngredients(userIngredients);

  const missing = [];
  const substitutions = [];

  recipeList.forEach((ingredient) => {
    const hasIngredient = userList.some((userIng) =>
      ingredient.includes(userIng)
    );

    if (!hasIngredient) {
      missing.push(ingredient);

      const sub = findSubstitution(ingredient);
      if (sub) substitutions.push(sub);
    }
  });

  return {
    missingIngredients: missing,
    substitutions: substitutions
  };
};