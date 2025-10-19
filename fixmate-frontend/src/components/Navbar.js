// src/components/Navbar.js
import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Home, Calendar, User, LogOut, LogIn, UserPlus } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useContext(AuthContext);
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = () => {
    logout();
    setShowDropdown(false);
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          FixMate
        </Link>

        <div className="nav-links">
          <Link to="/" className="nav-link">
            <Home size={20} />
            <span>Home</span>
          </Link>
          
          <Link to="/my-bookings" className="nav-link">
            <Calendar size={20} />
            <span>My Bookings</span>
          </Link>

          <div className="profile-dropdown">
            <button
              className="nav-link profile-btn"
              onClick={() => setShowDropdown(!showDropdown)}
            >
              <User size={20} />
              <span>{isAuthenticated() ? user?.username : 'Account'}</span>
            </button>

            {showDropdown && (
              <div className="dropdown-menu">
                {isAuthenticated() ? (
                  <>
                    <div className="dropdown-header">
                      <p className="user-name">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="user-email">{user?.email}</p>
                    </div>
                    <div className="dropdown-divider"></div>
                    <Link
                      to="/my-bookings"
                      className="dropdown-item"
                      onClick={() => setShowDropdown(false)}
                    >
                      <Calendar size={18} />
                      <span>My Bookings</span>
                    </Link>
                    <button
                      className="dropdown-item logout-btn"
                      onClick={handleLogout}
                    >
                      <LogOut size={18} />
                      <span>Logout</span>
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="dropdown-item"
                      onClick={() => setShowDropdown(false)}
                    >
                      <LogIn size={18} />
                      <span>Login</span>
                    </Link>
                    <Link
                      to="/register"
                      className="dropdown-item"
                      onClick={() => setShowDropdown(false)}
                    >
                      <UserPlus size={18} />
                      <span>Register</span>
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {showDropdown && (
        <div
          className="dropdown-overlay"
          onClick={() => setShowDropdown(false)}
        ></div>
      )}
    </nav>
  );
};

export default Navbar;