import React, { useState } from "react";
import "./style.css";

function LoginSignup() {

  const [page, setPage] = useState("login");

  const handleLogin = (e) => {
    e.preventDefault();
    alert("✅ Login successful! Welcome back to ChefAI 👨‍🍳");
  };

  const handleSignup = (e) => {
    e.preventDefault();
    alert("✅ Account created successfully!");
  };

  return (
    <div className="login-container">

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
                <input type="text" placeholder="Enter your username"/>
              </div>

              <div className="input-group">
                <label>Password</label>
                <input type="password" placeholder="Enter your password"/>
              </div>

              <div className="forgot-section">
                <a href="/">Forgot Password?</a>
              </div>

              <button className="login-button">Login</button>

            </form>

            <div className="divider">
              <span>or continue with</span>
            </div>

            <button className="google-button">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuARxCLdFA-0yyQWU6JkllNhK0wod6FAD30nAcKYx6XEubcXqDvXY4Pn3A9HsXNDNouIpWH_maQC-74vAbMGeh1R_j2suJxZ0cJtLI1POcfXqfVE-clYIOBog6mSNQXGrN5ORvTEpospmSO9SWVyhnr2_MBWbQRrWhZ1PwCI3fmgFiD9IiU3i0k3a9sC48wmS8SCP7fEwiC73Ep1yjKkACg2dsQZy0RV44vIhW2kkQ_nofq5J_HwmR3QV5vwlv1Glf15u18WJ4LUAh6I"
                alt="google"
                className="google-logo"
              />
              <span>Sign in with Google</span>
            </button>

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
                <input type="text" placeholder="Enter your first name"/>
              </div>

              <div className="input-group">
                <label>Last Name</label>
                <input type="text" placeholder="Enter your last name"/>
              </div>

              <div className="input-group">
                <label>Email</label>
                <input type="email" placeholder="Enter your email"/>
              </div>

              <div className="input-group">
                <label>Username</label>
                <input type="text" placeholder="Enter your username"/>
              </div>

              <div className="input-group">
                <label>Password</label>
                <input type="password" placeholder="Enter your password"/>
              </div>

              <div className="input-group">
                <label>Confirm Password</label>
                <input type="password" placeholder="Confirm your password"/>
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