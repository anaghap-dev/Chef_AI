import RecipeCard from "./RecipeCard";

function SuggestedRecipes({ recipes }){

  return(

    <div style={{padding:"20px"}}>

      <h3>Suggested for you</h3>

      <div style={styles.row}>

        {recipes.length === 0 ? (
          <p>No recipes yet. Try searching ingredients.</p>
        ) : (

          recipes.map((recipe, index) => (

            <RecipeCard
              key={index}
              image={recipe.image || "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800"}
              title={recipe.recipe_name}
              time={recipe.time || "20 MINS"}
              tag={recipe.cuisine || "Recipe"}
              match={Math.round(recipe.score * 100) || "90"}
            />

          ))

        )}

      </div>

    </div>

  )
}

const styles={
row:{
 display:"flex",
 gap:"15px",
 overflowX:"auto",
 paddingTop:"10px",
 scrollbarWidth:"none"
}
}

export default SuggestedRecipes;