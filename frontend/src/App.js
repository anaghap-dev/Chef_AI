import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GroceryCart from "./pages/GroceryCart";

function App() {
  return (
    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/grocerycart" element={<GroceryCart />} />
      </Routes>

    </BrowserRouter>
  );
}

export default App;