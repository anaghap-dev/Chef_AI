import React, { useState, useRef ,useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../pages/supabaseClient';
import RecipeCard from './RecipeCard';
import './ProfilePage.css';
import { 
  ArrowLeft, Settings,  
  Camera, Bell, Moon, LogOut, ChevronRight
} from 'lucide-react';

const Profile = () => {

  const [showSettings, setShowSettings] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [savedRecipes, setSavedRecipes] = useState([]);

  const fileInputRef = useRef(null);
  const formattedRecipes = savedRecipes.map((r) => ({
  recipe_name: r.recipe_name,
  image: r.recipe_image,
  time: "",
  cuisine: ""
}));

  useEffect(() => {
  const loadUser = async () => {
    const { data, error } = await supabase.auth.getUser();

     if (error) {
      console.error("Error fetching user:", error.message);
      navigate("/login");
      return;
    }

    if (!data.user) {
      navigate("/login");
      return;
    }

    const supaUser = data.user;

    setUser({
      name: supaUser.user_metadata?.username || "User",
      email: supaUser.email,
      memberSince: new Date(supaUser.created_at).toLocaleDateString(),
      avatar:
        supaUser.user_metadata?.avatar ||
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400"
    });
  };

  loadUser();
  
}, [navigate]);


    useEffect(() => {
  const fetchSavedRecipes = async () => {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) return;

    const { data, error } = await supabase
      .from("saved_recipes")
      .select("*")
      .eq("user_id", user.id)
      .order("id", { ascending: false });

    if (error) {
      console.log("Fetch error:", error.message);
    } else {
      setSavedRecipes(data);
    }
  };

  fetchSavedRecipes();
}, []);
  

  const handleShare = async () => {
    const shareData = {
      title: 'Chef AI Profile',
      text: `Check out ${user.name}'s profile!`,
      url: window.location.href, 
    };
    try {
      if (navigator.share) await navigator.share(shareData);
      else {
        await navigator.clipboard.writeText(window.location.href);
        alert('Profile link copied!');
      }
    } catch (err) { console.error(err); }
  };

      const handleBack = () => {
  if (showSettings) {
    setShowSettings(false);
  } else {
    navigate("/");
  }
};


  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setUser({ ...user, avatar: reader.result });
      reader.readAsDataURL(file);
    }
  };

 const handleDeleteRecipe = async (recipeName) => {
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) return;

  const { error } = await supabase
    .from("saved_recipes")
    .delete()
    .eq("user_id", user.id)
    .eq("recipe_name", recipeName);

  if (!error) {
    setSavedRecipes(prev =>
      prev.filter(r => r.recipe_name !== recipeName)
    );
  }
};

  if (!user) {
  return (
    <div className="app-viewport">
      <p style={{ textAlign: "center", marginTop: "50px" }}>
        Loading profile...
      </p>
    </div>
  );
}

  return (
    <div className={`app-viewport ${darkMode ? 'dark' : 'light'}`}>
      <div className="main-phone-wrapper">
        
        <header className="app-navbar">
          <button className="nav-action-btn" onClick={handleBack}>
            <ArrowLeft size={24} strokeWidth={2.5} />
          </button>
          <h1 className="nav-page-title">
               {showSettings ? "Settings" : "My Profile"}
                </h1>
          <button 
            className={`nav-action-btn ${showSettings ? 'active-state' : ''}`} 
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings size={24} strokeWidth={2.5} />
          </button>
        </header>

        <div className="scrollable-content">
          {!showSettings ? (
  <div className="view-fade">

    {/* PROFILE CARD */}
    <section className="profile-hero-card">

      <div className="profile-avatar-group">
        <div className="avatar-ring">
          <img src={user?.avatar} alt="User" />
        </div>

        <button
          className="camera-fab"
          onClick={() => fileInputRef.current.click()}
        >
          <Camera size={18} fill="white" color="white" />
        </button>

        <input
          type="file"
          ref={fileInputRef}
          hidden
          onChange={handleImageChange}
          accept="image/*"
        />
      </div>

      <div className="user-text-center">
        <h2 className="user-display-name">{user?.name}</h2>
        <p className="user-display-email">{user?.email}</p>
      </div>

    </section>

    {/* SHARE BUTTON */}
    <div className="action-button-grid">
      <button className="main-orange-btn" onClick={handleShare}>
        Share Profile
      </button>
    </div>

    {/* SAVED RECIPES */}
    <section className="content-section">
      <div className="section-flex-header">
        <h3>Saved Recipes</h3>
      </div>

      {savedRecipes.length === 0 ? (
        <p style={{ textAlign: "center", opacity: 0.6 }}>
          No saved recipes
        </p>
      ) : (
        <div className="saved-recipes-list">
  {formattedRecipes.map((recipe) => (
    <div key={recipe.recipe_name} style={{ position: "relative" }}>

      {/* Recipe Card (same as home page) */}
      <RecipeCard
        recipe={recipe}
         onView={(r) =>
    navigate("/recipe-details", {
      state: { recipe: r }
    })
  }
      />

      {/* DELETE BUTTON OVERLAY */}
      <button
        onClick={() => handleDeleteRecipe(recipe.recipe_name)}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: "red",
          color: "white",
          border: "none",
          padding: "6px 10px",
          borderRadius: "8px",
          cursor: "pointer"
        }}
      >
        Delete
      </button>

    </div>
  ))}
        </div>
      )}
    </section>

  </div>
) : (
            <div className="settings-list-container view-fade">
              <div className="settings-group-card">
                <div className="setting-tile">
                  <div className="tile-left">
                    <div className="tile-icon orange-bg"><Bell size={20} /></div>
                    <span className="tile-label">Push Notifications</span>
                  </div>
                  <div className={`pro-toggle ${notifications ? 'on' : ''}`} onClick={() => setNotifications(!notifications)}>
                    <div className="toggle-knob" />
                  </div>
                </div>

                <div className="setting-tile">
                  <div className="tile-left">
                    <div className="tile-icon blue-bg"><Moon size={20} /></div>
                    <span className="tile-label">Dark Mode</span>
                  </div>
                  <div className={`pro-toggle ${darkMode ? 'on' : ''}`} onClick={() => setDarkMode(!darkMode)}>
                    <div className="toggle-knob" />
                  </div>
                </div>

                <div className="setting-tile danger-tile" onClick={() => {
                       localStorage.removeItem("user");
                      navigate("/login");
                      }}>
                  <div className="tile-left">
                    <div className="tile-icon red-bg"><LogOut size={20} /></div>
                    <span className="tile-label">Logout Account</span>
                  </div>
                  <ChevronRight size={20} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;