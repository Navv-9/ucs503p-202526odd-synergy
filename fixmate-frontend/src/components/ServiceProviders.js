import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { apiService } from '../services/api';
import { LocationContext } from '../context/LocationContext';
import { 
  Star, 
  Phone, 
  MapPin, 
  Users, 
  ArrowLeft,
  RefreshCw,
  AlertCircle,
  Navigation
} from 'lucide-react';
import './ServiceProviders.css';

const ServiceProviders = () => {
  const { categoryName } = useParams();
  const { selectedCity } = useContext(LocationContext);
  const navigate = useNavigate();
  const { isAuthenticated } = useContext(AuthContext);
  const [providers, setProviders] = useState([]);
  const [categoryInfo, setCategoryInfo] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProviders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryName, selectedCity]);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProviders(categoryName, selectedCity);
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

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" />
        <p>Loading {categoryName} providers in {selectedCity}...</p>
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
        
        <div className="header-content">
          <h1>{categoryInfo} Services</h1>
          
          {/* Location Badge */}
          <div className="location-badge">
            <Navigation size={16} />
            <span>Showing results in <strong>{selectedCity}</strong></span>
          </div>
          
          <p className="providers-count">
            {providers.length} provider{providers.length !== 1 ? 's' : ''} available
          </p>
        </div>
      </div>

      {providers.length === 0 ? (
        <div className="no-providers">
          <MapPin size={48} className="no-providers-icon" />
          <h3>No providers found in {selectedCity}</h3>
          <p>Try selecting a different city or check back later.</p>
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