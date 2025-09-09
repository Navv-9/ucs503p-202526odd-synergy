// src/components/Navbar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, Settings, User } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          FixMate
        </Link>
        
        <div className="nav-links">
          <Link to="/" className="nav-link">
            <Home size={20} />
            Home
          </Link>
          
          <button className="nav-link" onClick={() => alert('Profile coming soon!')}>
            <User size={20} />
            Profile
          </button>
          
          <button className="nav-link" onClick={() => alert('Settings coming soon!')}>
            <Settings size={20} />
            Settings
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;