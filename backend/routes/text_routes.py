from fastapi import APIRouter
from pydantic import BaseModel

from models.recipe_matcher import recommend_recipes

router = APIRouter()

class IngredientInput(BaseModel):
    ingredients: str


@router.post("/search/text")
def search_by_text(data: IngredientInput):

    recipes = recommend_recipes(data.ingredients)

    return {
        "input_ingredients": data.ingredients,
        "recipes": recipes
    }