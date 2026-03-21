import { useState } from "react";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import GenerateButton from "../components/GenerateButton";
import SuggestedRecipes from "../components/SuggestedRecipes";
import WhyChefAI from "../components/WhyChefAI";
import Footer from "../components/Footer";

const recipes = [
  {
    recipe_name: "Mediterranean Bowl",
    cuisine: "Healthy",
    time: "15 MINS",
    score: 0.95,
    image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
  },
  {
    recipe_name: "Pantry Pasta Pesto",
    cuisine: "Italian",
    time: "20 MINS",
    score: 0.92,
    image: "https://images.unsplash.com/photo-1525755662778-989d0524087e"
  },
  {
    recipe_name: "Veg Rice Bowl",
    cuisine: "Asian",
    time: "18 MINS",
    score: 0.89,
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
  },
  {
   
  recipe_name: "Avocado Toast",
  cuisine: "Breakfast",
  time: "10 MINS",
  score: 0.91,
  image: "https://images.unsplash.com/photo-1588137378633-dea1336ce1e2?w=800"
   },
  {
    recipe_name: "Grilled Veg Salad",
    cuisine: "Healthy",
    time: "12 MINS",
    score: 0.88,
    image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd"
  }
];

function Home(){
  const [ingredients, setIngredients] = useState("");

  return(

    <div>

      <Navbar/>

      <Hero/>

      <SearchBar ingredients={ingredients} setIngredients={setIngredients}/>

      <GenerateButton/>

      <SuggestedRecipes recipes={recipes}/>

      <WhyChefAI/>

      <Footer/>

    </div>

  )
}

export default Home;