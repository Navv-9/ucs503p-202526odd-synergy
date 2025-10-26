import React, { useState, useEffect, useContext } from 'react'; // Add useContext
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext'; // ADD THIS
import { apiService } from '../services/api';
import { 
  Star, 
  Phone, 
  MapPin, 
  Users, 
  ArrowLeft,
  RefreshCw,
  AlertCircle 
} from 'lucide-react';
import './ServiceProviders.css';

const ServiceProviders = () => {
  const { categoryName } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useContext(AuthContext); // ADD THIS
  const [providers, setProviders] = useState([]);
  const [categoryInfo, setCategoryInfo] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProviders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryName]);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProviders(categoryName);
      setProviders(data.providers || []);
      setCategoryInfo(data.category || categoryName);
      setError(null);
    } catch (err) {
      setError('Failed to load service providers. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderClick = (providerId) => {
    navigate(`/provider/${providerId}`);
  };

  const handleBack = () => {
    navigate('/');
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="star filled" size={16} />);
    }

    if (hasHalfStar) {
      stars.push(<Star key="half" className="star half" size={16} />);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="star empty" size={16} />);
    }

    return stars;
  };

  // REMOVED renderTrustedBy function - we'll inline it below

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" />
        <p>Loading {categoryName} providers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <AlertCircle className="error-icon" />
        <p>{error}</p>
        <button onClick={fetchProviders} className="retry-btn">
          Try Again
        </button>
        <button onClick={handleBack} className="back-btn">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="service-providers">
      <div className="header">
        <button onClick={handleBack} className="back-button">
          <ArrowLeft size={20} />
          Back
        </button>
        <h1>{categoryInfo} Services</h1>
        <p>{providers.length} providers available</p>
      </div>

      {providers.length === 0 ? (
        <div className="no-providers">
          <p>No {categoryName.toLowerCase()} providers found in your area.</p>
          <button onClick={handleBack} className="back-btn">
            Browse Other Services
          </button>
        </div>
      ) : (
        <div className="providers-list">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className="provider-card"
              onClick={() => handleProviderClick(provider.id)}
            >
              <div className="provider-header">
                <h3>{provider.name}</h3>
                <div className="rating">
                  {renderStars(provider.rating)}
                  <span className="rating-text">
                    {provider.rating} ({provider.total_reviews} reviews)
                  </span>
                </div>
              </div>

              <div className="provider-details">
                <div className="detail-item">
                  <Phone size={16} />
                  <span>{provider.phone}</span>
                </div>
                
                {provider.address && (
                  <div className="detail-item">
                    <MapPin size={16} />
                    <span>{provider.address}</span>
                  </div>
                )}

                <div className="experience">
                  <span className="experience-badge">
                    {provider.experience_years} years experience
                  </span>
                </div>
              </div>

              {/* UPDATED: Only show trust if authenticated AND has data */}
              {isAuthenticated() && provider.trusted_by && provider.trusted_by.count > 0 && (
                <div className="trusted-by">
                  <Users size={16} />
                  <span>{provider.trusted_by.message}</span>
                </div>
              )}

              <div className="provider-actions">
                <button 
                  className="view-details-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleProviderClick(provider.id);
                  }}
                >
                  View Details
                </button>
                
                <button 
                  className="call-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(`tel:${provider.phone}`);
                  }}
                >
                  <Phone size={16} />
                  Call
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ServiceProviders;