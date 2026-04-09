import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GroceryCart from "./pages/GroceryCart";
import RecipeDetails from "./pages/RecipeDetails";

function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/grocerycart" element={<GroceryCart />} />
        <Route path="/recipe-details" element={<RecipeDetails />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;