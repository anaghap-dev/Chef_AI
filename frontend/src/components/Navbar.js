import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";

function Navbar() {

  const navbarStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "15px 40px",
    background: "#ffffff",
    borderBottom: "1px solid #eee"
  };

  const logoSection = {
    display: "flex",
    alignItems: "center",
    gap: "12px"
  };

  const navLinks = {
    display: "flex",
    gap: "20px"
  };

  const buttonStyle = {
    textDecoration: "none",
    backgroundColor: "#f47b5d",
    color: "white",
    padding: "8px 16px",
    borderRadius: "6px",
    fontWeight: "500"
  };

  return (

    <div style={navbarStyle}>

      {/* Logo */}
      <div style={logoSection}>

        <img
          src={logo}
          alt="ChefAI"
          style={{width:"100px"}}
        />

        <h1 style={{fontSize:"26px"}}>
          Chef<span style={{color:"#f47b5d"}}>AI</span>
        </h1>

      </div>

      {/* Navigation Buttons */}
      <div style={navLinks}>

        <Link to="/grocerycart" style={buttonStyle}>
          Grocery Cart
        </Link>

        <Link to="#" style={buttonStyle}>
          Profile
        </Link>

        <Link to="#" style={buttonStyle}>
          Login
        </Link>

      </div>

    </div>

  );
}

export default Navbar;