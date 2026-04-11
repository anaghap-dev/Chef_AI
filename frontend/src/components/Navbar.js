import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";
import { useNavigate } from "react-router-dom";
import { supabase } from "../pages/supabaseClient";
import { useEffect, useState } from "react";

function Navbar() {
  const [user,setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // get current user
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
    });
    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user || null);
      }
    );

    return () => listener.subscription.unsubscribe();
  }, []);

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

        <img   src={logo}    alt="ChefAI"      style={{width:"60px"}}/>

        <h1 style={{fontSize:"26px"}}>
          Chef<span style={{color:"#f47b5d"}}>AI</span>
        </h1>

      </div>

      {/* Navigation Buttons */}
      <div style={navLinks}>

        <Link to="/grocerycart" style={buttonStyle}>
          Grocery Cart
        </Link>

        {user && (
        <Link to="/profile" style={buttonStyle}>
          Profile
        </Link>
        )}

        {user ? (
          <button
            onClick={async () => {
              await supabase.auth.signOut();
              setUser(null);
              navigate("/"); // better than reload
            }}
            style={buttonStyle}
          >
            Logout
          </button>
        )  : (
         <Link to="/login" style={buttonStyle}>
         Login
          </Link>
        )}
        
      </div>

    </div>

  );
}

export default Navbar;