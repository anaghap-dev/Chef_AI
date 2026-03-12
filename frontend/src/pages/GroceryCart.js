import React, { useState } from "react";
import "./GroceryCart.css";
import logo from "../assets/logo.png";

function GroceryCart() {

const [items, setItems] = useState([
{ name: "Fresh Spinach", qty: "200g" },
{ name: "Heirloom Carrots", qty: "4 units" },
{ name: "Chicken Thighs", qty: "500g" },
{ name: "Extra Virgin Olive Oil", qty: "1 bottle" },
{ name: "Greek Yogurt", qty: "500g" }
]);

const [newItem, setNewItem] = useState("");
const [newQty, setNewQty] = useState("");

const tips = [
"Buying seasonal vegetables saves money",
"Frozen vegetables last longer",
"Buying in bulk reduces cost",
"Plan meals before shopping",
"Store herbs in water to keep them fresh"
];

const randomTip = tips[Math.floor(Math.random() * tips.length)];

const addItem = () => {

if (newItem.trim() !== "") {

setItems([
...items,
{ name: newItem, qty: newQty }
]);

setNewItem("");
setNewQty("");

}

};

const deleteItem = (index) => {
setItems(items.filter((_, i) => i !== index));
};

return (

<div className="grocery-container">

{/* HEADER */}

<div className="header">

<div className="logo-section">
<img src={logo} alt="ChefAI"/>

<h2 className="logo-text">
Chef<span>AI</span>
</h2>

</div>

<div className="menu">☰</div>

</div>

<h1 className="title">My Grocery List</h1>

{/* ADD ITEM */}

<div className="add-box">

<input
type="text"
placeholder="Ingredient"
value={newItem}
onChange={(e)=>setNewItem(e.target.value)}
/>

<input
type="text"
placeholder="Quantity"
value={newQty}
onChange={(e)=>setNewQty(e.target.value)}
/>

<button onClick={addItem}>+</button>

</div>

{/* ITEMS */}

<div className="items">

{items.map((item,index)=>(

<div className="item-card" key={index}>

<div>
<h3>{item.name}</h3>
<p>{item.qty}</p>
</div>

<button
className="delete"
onClick={()=>deleteItem(index)}
>
🗑
</button>

</div>

))}

</div>

{/* SUMMARY */}

<div className="summary">

<h3>List Summary</h3>

<p>Total Items: {items.length}</p>

<div className="tip">
💡 {randomTip}
</div>

</div>

</div>

);

}

export default GroceryCart;