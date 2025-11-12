import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Home, Calendar, User, LogOut, LogIn, UserPlus, Briefcase } from 'lucide-react';
import CitySelector from './CitySelector';
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

  const isProvider = user?.user_type === 'provider' || user?.is_provider === true;

  const handleDropdownToggle = () => {
    setShowDropdown(!showDropdown);
  };

  const handleDropdownClose = () => {
    setShowDropdown(false);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          FixMate
        </Link>
        
        {/* Wrapped in a div for better control */}
        <div className="nav-city-selector">
          <CitySelector />
        </div>

        <div className="nav-links">
          <Link to="/" className="nav-link">
            <Home size={20} />
            <span>Home</span>
          </Link>

          {/* Show Dashboard link only for providers */}
          {isAuthenticated() && isProvider && (
            <Link to="/provider/dashboard" className="nav-link">
              <Briefcase size={20} />
              <span>Dashboard</span>
            </Link>
          )}

          {/* Show My Bookings for everyone (authenticated users) */}
          <Link to="/my-bookings" className="nav-link">
            <Calendar size={20} />
            <span>My Bookings</span>
          </Link>

          <div className="profile-dropdown">
            <button
              className="nav-link profile-btn"
              onClick={handleDropdownToggle}
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

                    {/* Show Dashboard in dropdown only for providers */}
                    {isProvider && (
                      <Link
                        to="/provider/dashboard"
                        className="dropdown-item"
                        onClick={handleDropdownClose}
                      >
                        <Briefcase size={18} />
                        <span>Dashboard</span>
                      </Link>
                    )}

                    {/* My Bookings visible to all authenticated users */}
                    <Link
                      to="/my-bookings"
                      className="dropdown-item"
                      onClick={handleDropdownClose}
                    >
                      <Calendar size={18} />
                      <span>My Bookings</span>
                    </Link>

                    {/* Show Profile link only for providers */}
                    {isProvider && (
                      <Link
                        to="/provider/profile"
                        className="dropdown-item"
                        onClick={handleDropdownClose}
                      >
                        <User size={18} />
                        <span>Profile</span>
                      </Link>
                    )}

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
                      onClick={handleDropdownClose}
                    >
                      <LogIn size={18} />
                      <span>Login</span>
                    </Link>
                    <Link
                      to="/register"
                      className="dropdown-item"
                      onClick={handleDropdownClose}
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
          onClick={handleDropdownClose}
        ></div>
      )}
    </nav>
  );
};

export default Navbar;