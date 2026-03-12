import RecipeCard from "./RecipeCard";

function SuggestedRecipes({ recipes }){

  return(

    <div style={{padding:"20px"}}>

      <h3>Suggested for you</h3>

      <div style={styles.row}>

        {recipes.map((recipe, index) => (

          <RecipeCard
            key={index}
            image={recipe.image}
            title={recipe.recipe_name}
            time={recipe.time}
            tag={recipe.cuisine}
            match={Math.round(recipe.score * 100)}
          />

        ))}

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