import React, { useState } from "react";
import { useNavigate ,Link} from "react-router-dom";
import { supabase} from "./pages/supabaseClient";
import "./style.css";

function LoginSignup() {

  const [page, setPage] = useState("login");
  const navigate = useNavigate();   
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    const { error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password,
    });

    if (error) {
      alert(error.message);
      return;
    }
   
    alert("✅ Login successful! Welcome back to ChefAI 👨‍🍳");
    setTimeout(() => {
      navigate("/profile");
    }, 1000);
  };

  const handleSignup = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
  
    const { error } = await supabase.auth.signUp({
      email: email,
      password: password,
      options:{
        data:{
          username: username,
          firstName: firstName,
          lastName: lastName
        }
      }
    });

    if (error) {
      alert(error.message);
      return;
    }

    alert("✅ Account created! Please login");
    setPage("login");
  };

  return (
    <div className="login-container">

      <div style={{
        position: "absolute",
        top: "20px",
        right: "20px",
        zIndex: 9999
      }}>
        <button
          type="button"
          onClick={() => navigate("/")}
          style={{
            padding: "8px 14px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#f07238",
            color: "#fff",
            fontWeight: "600",
            cursor: "pointer"
          }}
        >
          Home
        </button>
      </div>

      <div className="bg-pattern"></div>

      {page === "login" && (
        <div className="page active">
          <div className="content-wrapper">

            <div className="header-section">
              <div className="logo-circle"></div>
              <h1>ChefAI</h1>
            </div>

            <form className="login-form" onSubmit={handleLogin}>

              <div className="input-group">
                <label>Username</label>
                <input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Email</label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="forgot-section">
                <Link to="/forgot-password">Forgot Password?</Link>
              </div>

              <button className="login-button">Login</button>

            </form>

            <div className="signup-section">
              <p>
                Don't have an account?
                <button
                  style={{border:"none",background:"none",color:"#f07238",fontWeight:"700"}}
                  onClick={() => setPage("signup")}
                >
                  Sign Up
                </button>
              </p>
            </div>

          </div>
        </div>
      )}

      {page === "signup" && (
        <div className="page active">
          <div className="content-wrapper">

            <div className="header-section">
              <div className="logo-circle"></div>
              <h1>ChefAI</h1>
            </div>

            <form className="login-form" onSubmit={handleSignup}>

              <div className="input-group">
                <label>First Name</label>
                <input
                  type="text"
                  placeholder="Enter your first name"
                  onChange={(e) => setFirstName(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Last Name</label>
                <input
                  type="text"
                  placeholder="Enter your last name"
                  onChange={(e) => setLastName(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Email</label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Username</label>
                <input
                  type="text"
                  placeholder="Enter your username"
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="Enter your password"
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  placeholder="Confirm your password"
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>

              <button className="login-button">
                Create Account
              </button>

            </form>

            <div className="signup-section">
              <p>
                Already have an account?
                <button
                  style={{border:"none",background:"none",color:"#f07238",fontWeight:"700"}}
                  onClick={() => setPage("login")}
                >
                  Sign In
                </button>
              </p>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default LoginSignup;
