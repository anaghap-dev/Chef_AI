import { useState } from "react"

import Navbar from "../components/Navbar"
import Hero from "../components/Hero"
import SearchBar from "../components/SearchBar"
import GenerateButton from "../components/GenerateButton"
import SuggestedRecipes from "../components/SuggestedRecipes"
import WhyChefAI from "../components/WhyChefAI"
import Footer from "../components/Footer"

function Home(){

  const [ingredients, setIngredients] = useState("")
  const [recipes, setRecipes] = useState([])

  const fetchRecipes = async () => {

    try {

      const response = await fetch("http://127.0.0.1:5000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ingredients: ingredients
        })
      })

      const data = await response.json()

      setRecipes(data)

    } catch (error) {
      console.error("Error fetching recipes:", error)
    }
  }

  return(

    <div>

      <Navbar/>

      <Hero/>

      <SearchBar
        ingredients={ingredients}
        setIngredients={setIngredients}
      />

      <GenerateButton
        fetchRecipes={fetchRecipes}
      />

      <SuggestedRecipes
        recipes={recipes}
      />

      <WhyChefAI/>

      <Footer/>

    </div>

  )
}

export default Home