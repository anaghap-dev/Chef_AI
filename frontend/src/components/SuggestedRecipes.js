import RecipeCard from "./RecipeCard";

function SuggestedRecipes(){

  return(

    <div style={{padding:"20px"}}>

      <h3>Suggested for you</h3>

      <div style={styles.row}>

        <RecipeCard
        image="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800"
        title="Mediterranean Bowl"
        time="15 MINS"
        tag="Healthy"
        match="95"
        />

        <RecipeCard
        image="https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=800"
        title="Pantry Pasta Pesto"
        time="20 MINS"
        tag="Vegetarian"
        match="82"
        />

        <RecipeCard
        image="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800"
        title="Veg Rice Bowl"
        time="18 MINS"
        tag="Quick"
        match="88"
        />

        <RecipeCard
        image="https://images.unsplash.com/photo-1525351484163-7529414344d8?w=800"
        title="Avocado Toast"
        time="10 MINS"
        tag="Breakfast"
        match="91"
        />

        <RecipeCard
        image="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"
        title="Grilled Veg Salad"
        time="25 MINS"
        tag="Low Fat"
        match="86"
        />

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