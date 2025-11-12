// src/components/ProviderProfile.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Clock,
  FileText,
  AlertCircle,
  CheckCircle,
  Star
} from 'lucide-react';
import { apiService } from '../services/api';
import './Login.css';

const ProviderProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    email: '',
    description: '',
    availability: '',
    service_area: '',
    address: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const data = await apiService.getProviderProfile(token);
      setProfile(data);
      setFormData({
        name: data.name,
        phone_number: data.phone_number,
        email: data.email || '',
        description: data.description || '',
        availability: data.availability || '',
        service_area: data.service_area || '',
        address: data.address || ''
      });
    } catch (err) {
      setError('Failed to load profile. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('access_token');
      await apiService.updateProviderProfile(formData, token);
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      await fetchProfile();
    } catch (err) {
      setError('Failed to update profile. Please try again.');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: profile.name,
      phone_number: profile.phone_number,
      email: profile.email || '',
      description: profile.description || '',
      availability: profile.availability || '',
      service_area: profile.service_area || '',
      address: profile.address || ''
    });
    setIsEditing(false);
    setError('');
    setSuccess('');
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>My Profile</h1>
        <p>Manage your service provider profile</p>
      </div>

      {error && (
        <div className="error-message" style={{ marginBottom: '20px' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="success-message" style={{ marginBottom: '20px' }}>
          <CheckCircle size={18} />
          <span>{success}</span>
        </div>
      )}

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {profile.name.charAt(0).toUpperCase()}
          </div>
          <div className="profile-info">
            <h2>{profile.name}</h2>
            <p>{profile.category_name} • {profile.experience_years} years experience</p>
            <div className="rating-display" style={{ marginTop: '8px' }}>
              <Star size={16} fill="#fbbf24" strokeWidth={0} />
              <span style={{ fontWeight: 600, color: '#1f2937' }}>
                {profile.rating.toFixed(1)}
              </span>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>
                ({profile.total_reviews} reviews)
              </span>
            </div>
          </div>
        </div>

        {!isEditing ? (
          <>
            <div className="profile-details">
              <div className="detail-item">
                <div className="detail-icon">
                  <User size={20} />
                </div>
                <div className="detail-content">
                  <h4>Full Name</h4>
                  <p>{profile.name}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <Phone size={20} />
                </div>
                <div className="detail-content">
                  <h4>Phone Number</h4>
                  <p>{profile.phone_number}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <Mail size={20} />
                </div>
                <div className="detail-content">
                  <h4>Email</h4>
                  <p>{profile.email || 'Not provided'}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <MapPin size={20} />
                </div>
                <div className="detail-content">
                  <h4>City</h4>
                  <p>{profile.city}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <MapPin size={20} />
                </div>
                <div className="detail-content">
                  <h4>Service Area</h4>
                  <p>{profile.service_area}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <MapPin size={20} />
                </div>
                <div className="detail-content">
                  <h4>Address</h4>
                  <p>{profile.address}</p>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">
                  <Clock size={20} />
                </div>
                <div className="detail-content">
                  <h4>Availability</h4>
                  <p>{profile.availability}</p>
                </div>
              </div>
            </div>

            {profile.description && (
              <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                  <FileText size={20} color="#6b7280" />
                  <h4 style={{ fontSize: '14px', color: '#6b7280', fontWeight: 600 }}>
                    About / Description
                  </h4>
                </div>
                <p style={{ fontSize: '14px', color: '#1f2937', lineHeight: '1.6' }}>
                  {profile.description}
                </p>
              </div>
            )}

            <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
                <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: profile.is_active ? '#10b981' : '#ef4444' }}>
                    {profile.is_active ? 'Active' : 'Inactive'}
                  </div>
                </div>
                <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Verification</div>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: profile.is_verified ? '#10b981' : '#f59e0b' }}>
                    {profile.is_verified ? 'Verified' : 'Pending'}
                  </div>
                </div>
                <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Joined</div>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: '#1f2937' }}>
                    {new Date(profile.joined_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>

            <button
              className="submit-btn"
              onClick={() => setIsEditing(true)}
              style={{ marginTop: '24px' }}
            >
              Edit Profile
            </button>
          </>
        ) : (
          <form onSubmit={handleSubmit} className="auth-form" style={{ marginTop: '24px' }}>
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone_number">Phone Number</label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="service_area">Service Area</label>
              <input
                type="text"
                id="service_area"
                name="service_area"
                value={formData.service_area}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="address">Address</label>
              <input
                type="text"
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="availability">Availability</label>
              <input
                type="text"
                id="availability"
                name="availability"
                value={formData.availability}
                onChange={handleChange}
                placeholder="e.g., Mon-Sat, 9AM-6PM"
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="4"
                placeholder="Tell customers about your services and expertise..."
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button
                type="submit"
                className="submit-btn"
                disabled={saving}
                style={{ flex: 1 }}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                className="submit-btn"
                onClick={handleCancel}
                style={{ flex: 1, background: 'white', color: '#667eea', border: '2px solid #667eea' }}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ProviderProfile;