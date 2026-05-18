import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";
import { useNavigate } from "react-router-dom";
import { supabase } from "../pages/supabaseClient";
import { useEffect, useState } from "react";

function Navbar() {
  const [user,setUser] = useState(null);
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== "undefined" ? window.innerWidth : 1024
  );
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

    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);

    return () => {
      listener.subscription.unsubscribe();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const navbarStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    padding: windowWidth < 640 ? "12px 16px" : "15px 40px",
    background: "var(--bg-light)",
    color: "var(--text-light)",
    borderBottom: "1px solid rgba(255,255,255,0.08)"
  };

  const logoSection = {
    display: "flex",
    alignItems: "center",
    gap: "12px"
  };

  const navLinks = {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "flex-end",
    gap: windowWidth < 640 ? "10px" : "20px",
    width: windowWidth < 640 ? "100%" : "auto",
    marginTop: windowWidth < 640 ? "12px" : "0"
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

        <img src={logo} alt="ChefAI" style={{ width: "60px" }} />

        <h1 className="navbar-title">
          Chef<span className="navbar-title-accent">AI</span>
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