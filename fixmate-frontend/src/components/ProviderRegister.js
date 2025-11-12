// src/components/ProviderRegister.js
import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { apiService } from '../services/api';
import { UserPlus, AlertCircle, Briefcase, User } from 'lucide-react';
import './Login.css';

const ProviderRegister = () => {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [registrationType, setRegistrationType] = useState('both'); // 'customer' or 'both'

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    category_name: '',
    experience_years: '',
    city: '', // ✅ ADDED - This was missing!
    service_area: '',
    description: '',
    availability: 'Mon-Sat, 9AM-6PM'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const categories = [
    'Plumber',
    'Barber',
    'Carpenter',
    'Electrician',
    'AC Service',
    'Appliance Repair'
  ];

  const cities = [
    'Patiala',
    'Chandigarh',
    'Mohali',
    'Ludhiana',
    'Amritsar',
    'Jalandhar',
    'Bathinda',
    'Pathankot',
    'Delhi',
    'Mumbai',
    'Bangalore',
    'Hyderabad',
    'Chennai',
    'Kolkata',
    'Pune',
    'Ahmedabad',
    'Jaipur',
    'Other'
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleRegistrationTypeChange = (type) => {
    setRegistrationType(type);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password2) {
      setError("Passwords don't match!");
      return;
    }

    if (registrationType === 'both') {
      // Validation for provider registration
      if (!formData.category_name) {
        setError("Please select a service category");
        return;
      }
      if (!formData.city) {
        setError("Please select a city");
        return;
      }
      if (!formData.experience_years || formData.experience_years < 0) {
        setError("Please enter valid years of experience");
        return;
      }
      if (!formData.service_area) {
        setError("Please enter your service area");
        return;
      }
    }

    setLoading(true);

    try {
      let response;

      if (registrationType === 'customer') {
        // Register as customer only
        response = await apiService.register(formData);
        login(response.user, response.tokens);
        localStorage.setItem('user_type', 'customer');

        const redirectPath = localStorage.getItem('redirectAfterLogin');
        if (redirectPath) {
          localStorage.removeItem('redirectAfterLogin');
          navigate(redirectPath);
        } else {
          navigate('/');
        }
      } else if (registrationType === 'both') {
        // Register as both customer and provider
        console.log('📤 Sending provider registration data:', formData); // Debug log
        response = await apiService.providerRegister(formData);
        login(response.user, response.tokens);
        localStorage.setItem('user_type', 'both');
        navigate('/provider/dashboard');
      }
    } catch (err) {
      console.error('❌ Registration error:', err); // Debug log
      
      if (err.username) {
        setError(err.username[0]);
      } else if (err.email) {
        setError(err.email[0]);
      } else if (err.password) {
        setError(err.password[0]);
      } else if (err.phone_number) {
        setError(err.phone_number[0]);
      } else if (err.category_name) {
        setError(err.category_name[0]);
      } else if (err.city) {
        setError(err.city[0]);
      } else if (err.service_area) {
        setError(err.service_area[0]);
      } else if (err.experience_years) {
        setError(err.experience_years[0]);
      } else if (err.error) {
        setError(err.error);
      } else {
        setError('Registration failed. Please check all fields and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className={`auth-card register-card ${registrationType === 'both' ? 'provider-register-card' : ''}`}>
        <div className="auth-header">
          <div className="auth-icon-wrapper">
            {registrationType === 'customer' ? (
              <User className="auth-icon-main" size={32} />
            ) : (
              <Briefcase className="auth-icon-main" size={32} />
            )}
          </div>
          <h1>Create Account</h1>
          <p>
            {registrationType === 'customer' && 'Join FixMate to book services'}
            {registrationType === 'both' && 'Join FixMate as Customer & Service Provider'}
          </p>
        </div>

        {/* Registration Type Selector */}
        <div className="registration-type-selector">
          <button
            type="button"
            className={`type-btn ${registrationType === 'customer' ? 'active' : ''}`}
            onClick={() => handleRegistrationTypeChange('customer')}
          >
            <User size={20} />
            <span>Customer</span>
          </button>
          <button
            type="button"
            className={`type-btn ${registrationType === 'both' ? 'active' : ''}`}
            onClick={() => handleRegistrationTypeChange('both')}
          >
            <UserPlus size={20} />
            <span>Customer & Provider</span>
          </button>
        </div>

        {error && (
          <div className="error-message">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Account Information */}
          <div className="form-section">
            <h3 className="section-title">Account Information</h3>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name *</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="First name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Last Name *</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Last name"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="username">Username *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Choose a username"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="your.email@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone_number">Phone Number *</label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+91-9876543210"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="password">Password *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Create a password"
                  required
                  minLength="6"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password2">Confirm Password *</label>
                <input
                  type="password"
                  id="password2"
                  name="password2"
                  value={formData.password2}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>
          </div>

          {/* Service Information - Only show for 'both' */}
          {registrationType === 'both' && (
            <div className="form-section">
              <h3 className="section-title">Service Provider Information</h3>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="category_name">Service Category *</label>
                  <select
                    id="category_name"
                    name="category_name"
                    value={formData.category_name}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select a category</option>
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="experience_years">Years of Experience *</label>
                  <input
                    type="number"
                    id="experience_years"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleChange}
                    placeholder="Years"
                    min="0"
                    required
                  />
                </div>
              </div>

              {/* ✅ ADDED: City field */}
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="city">City *</label>
                  <select
                    id="city"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select your city</option>
                    {cities.map((city) => (
                      <option key={city} value={city}>
                        {city}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="service_area">Service Area *</label>
                  <input
                    type="text"
                    id="service_area"
                    name="service_area"
                    value={formData.service_area}
                    onChange={handleChange}
                    placeholder="e.g., Sector 22, Model Town"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="availability">Availability</label>
                <input
                  type="text"
                  id="availability"
                  name="availability"
                  value={formData.availability}
                  onChange={handleChange}
                  placeholder="Mon-Sat, 9AM-6PM"
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description (Optional)</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Tell customers about your services and expertise..."
                  rows="4"
                />
              </div>
            </div>
          )}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Creating Account...' :
              registrationType === 'customer' ? 'Register as Customer' :
                'Register as Customer & Provider'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProviderRegister;