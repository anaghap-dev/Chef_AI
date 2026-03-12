import React, { useState, useRef } from 'react';
import './ProfilePage.css';
import { 
  ArrowLeft, Settings, Share2, Calendar, 
  Check, Camera, Bell, Moon, LogOut, ChevronRight, Save
} from 'lucide-react';

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  
  const [user, setUser] = useState({
    name: 'Alex Chefson',
    email: 'alex.chefson@chefai.app',
    memberSince: 'Oct 2023',
    avatar: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400'
  });

  const fileInputRef = useRef(null);

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
    if (showSettings) setShowSettings(false);
    else if (isEditing) setIsEditing(false);
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setUser({ ...user, avatar: reader.result });
      reader.readAsDataURL(file);
    }
  };

  const [dietaryPrefs, setDietaryPrefs] = useState([
    { id: 1, label: 'Vegan', active: true },
    { id: 2, label: 'Gluten-free', active: true },
    { id: 3, label: 'Keto', active: false },
    { id: 4, label: 'Low Carb', active: false },
  ]);

  return (
    <div className={`app-viewport ${darkMode ? 'dark' : 'light'}`}>
      <div className="main-phone-wrapper">
        
        <header className="app-navbar">
          <button className="nav-action-btn" onClick={handleBack}>
            <ArrowLeft size={24} strokeWidth={2.5} />
          </button>
          <h1 className="nav-page-title">
            {showSettings ? "Settings" : isEditing ? "Edit Profile" : "My Profile"}
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
              <section className="profile-hero-card">
                <div className="profile-avatar-group">
                  <div className="avatar-ring">
                    <img src={user.avatar} alt="User" />
                  </div>
                  <button className="camera-fab" onClick={() => fileInputRef.current.click()}>
                    <Camera size={18} fill="white" color="white" />
                  </button>
                  <input type="file" ref={fileInputRef} hidden onChange={handleImageChange} accept="image/*" />
                </div>

                {isEditing ? (
                  <div className="editing-form-container">
                    <div className="input-group">
                      <label>Full Name</label>
                      <input 
                        className="pro-input" 
                        value={user.name} 
                        onChange={(e) => setUser({...user, name: e.target.value})} 
                      />
                    </div>
                    <div className="input-group">
                      <label>Email Address</label>
                      <input 
                        className="pro-input" 
                        value={user.email} 
                        onChange={(e) => setUser({...user, email: e.target.value})} 
                      />
                    </div>
                    <button className="primary-save-btn" onClick={() => setIsEditing(false)}>
                      <Save size={18} /> Save Profile
                    </button>
                  </div>
                ) : (
                  <div className="user-text-center">
                    <h2 className="user-display-name">{user.name}</h2>
                    <p className="user-display-email">{user.email}</p>
                    <div className="status-chip">
                      <Calendar size={14} /> 
                      <span>Joined {user.memberSince}</span>
                    </div>
                  </div>
                )}
              </section>

              {!isEditing && (
                <>
                  <div className="action-button-grid">
                    <button className="main-orange-btn" onClick={() => setIsEditing(true)}>
                      Edit Profile
                    </button>
                    <button className="sq-share-btn" onClick={handleShare}>
                      <Share2 size={22} />
                    </button>
                  </div>

                  <section className="content-section">
                    <div className="section-flex-header">
                      <h3>Dietary Preferences</h3>
                      {/* MODIFY text has been removed */}
                    </div>
                    <div className="chip-flex-wrap">
                      {dietaryPrefs.map(pref => (
                        <button 
                          key={pref.id} 
                          className={`modern-chip ${pref.active ? 'filled' : ''}`}
                          onClick={() => setDietaryPrefs(dietaryPrefs.map(p => p.id === pref.id ? {...p, active: !p.active} : p))}
                        >
                          {pref.active && <Check size={16} strokeWidth={4} />}
                          {pref.label}
                        </button>
                      ))}
                    </div>
                  </section>
                </>
              )}
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

                <div className="setting-tile danger-tile" onClick={() => alert('Logout Success')}>
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