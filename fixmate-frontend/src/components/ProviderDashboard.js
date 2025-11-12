// src/components/ProviderDashboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Users, 
  Star, 
  TrendingUp, 
  Briefcase,
  Phone,
  Mail,
  MapPin,
  Clock,
  Award,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../services/api';
import './Login.css';

const ProviderDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const data = await apiService.getProviderDashboard(token);
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const { provider, statistics } = dashboardData;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Provider Dashboard</h1>
        <p>Welcome back, {provider.name}!</p>
      </div>

      {/* Statistics Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Calendar size={24} />
            </div>
          </div>
          <div className="stat-value">{statistics.total_bookings}</div>
          <div className="stat-label">Total Bookings</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Users size={24} />
            </div>
          </div>
          <div className="stat-value">{statistics.pending_requests}</div>
          <div className="stat-label">Pending Requests</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <TrendingUp size={24} />
            </div>
          </div>
          <div className="stat-value">{statistics.month_bookings}</div>
          <div className="stat-label">This Month</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Star size={24} />
            </div>
          </div>
          <div className="stat-value">{statistics.average_rating.toFixed(1)}</div>
          <div className="stat-label">Average Rating</div>
        </div>
      </div>

      {/* Provider Profile Card */}
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {provider.name.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h2>{provider.name}</h2>
            <p>{provider.category_name} • {provider.experience_years} years experience</p>
          </div>
        </div>

        <div className="profile-details">
          <div className="detail-item">
            <div className="detail-icon">
              <Phone size={20} />
            </div>
            <div className="detail-content">
              <h4>Phone Number</h4>
              <p>{provider.phone_number}</p>
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-icon">
              <Mail size={20} />
            </div>
            <div className="detail-content">
              <h4>Email</h4>
              <p>{provider.email || 'Not provided'}</p>
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-icon">
              <MapPin size={20} />
            </div>
            <div className="detail-content">
              <h4>Service Area</h4>
              <p>{provider.service_area}</p>
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-icon">
              <Clock size={20} />
            </div>
            <div className="detail-content">
              <h4>Availability</h4>
              <p>{provider.availability}</p>
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-icon">
              <Award size={20} />
            </div>
            <div className="detail-content">
              <h4>Total Reviews</h4>
              <p>{provider.total_reviews} reviews</p>
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-icon">
              <Briefcase size={20} />
            </div>
            <div className="detail-content">
              <h4>Status</h4>
              <p>{provider.is_verified ? '✓ Verified' : 'Pending Verification'}</p>
            </div>
          </div>
        </div>

        {provider.description && (
          <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
            <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px', fontWeight: 600 }}>
              About
            </h4>
            <p style={{ fontSize: '14px', color: '#1f2937', lineHeight: '1.6' }}>
              {provider.description}
            </p>
          </div>
        )}

        <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
          <button 
            className="submit-btn" 
            onClick={() => navigate('/provider/bookings')}
            style={{ flex: 1 }}
          >
            View Bookings
          </button>
          <button 
            className="submit-btn" 
            onClick={() => navigate('/provider/profile')}
            style={{ flex: 1, background: 'white', color: '#667eea', border: '2px solid #667eea' }}
          >
            Edit Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;