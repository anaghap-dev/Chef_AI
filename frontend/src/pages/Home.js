import Navbar from "../components/Navbar"
import Hero from "../components/Hero"
import SearchBar from "../components/SearchBar"
import GenerateButton from "../components/GenerateButton"
import SuggestedRecipes from "../components/SuggestedRecipes"
import WhyChefAI from "../components/WhyChefAI";
import Footer from "../components/Footer";

function Home(){

  return(

    <div>

      <Navbar/>

      <Hero/>

      <SearchBar/>

      <GenerateButton/>

      <SuggestedRecipes/>

      <WhyChefAI/>

      <Footer/>

    </div>

  )
}

export default Home