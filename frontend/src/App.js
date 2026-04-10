import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GroceryCart from "./pages/GroceryCart";
import RecipeDetails from "./pages/RecipeDetails";
import LoginSignup from "./LoginSignup";

function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/grocerycart" element={<GroceryCart />} />
        <Route path="/recipe-details" element={<RecipeDetails />} />
        <Route path="/login" element={<LoginSignup />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;