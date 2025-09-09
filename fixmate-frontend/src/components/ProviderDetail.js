// src/components/ProviderDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { 
  ArrowLeft,
  Star, 
  Phone, 
  Mail, 
  MapPin, 
  Calendar,
  Users,
  MessageCircle,
  ThumbsUp,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import './ProviderDetail.css';

const ProviderDetail = () => {
  const { providerId } = useParams();
  const navigate = useNavigate();
  const [provider, setProvider] = useState(null);
  const [trustedBy, setTrustedBy] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProviderDetail();
  }, [providerId]);

  const fetchProviderDetail = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProviderDetail(providerId);
      setProvider(data.provider);
      setTrustedBy(data.trusted_by);
      setReviews(data.recent_reviews || []);
      setError(null);
    } catch (err) {
      setError('Failed to load provider details. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(-1); // Go back to previous page
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

  const renderTrustedBy = (trustedData) => {
    if (!trustedData || trustedData.count === 0) {
      return (
        <div className="trusted-section">
          <Users size={20} />
          <span>No friends have used this service yet</span>
        </div>
      );
    }

    return (
      <div className="trusted-section">
        <Users size={20} />
        <div>
          <strong>{trustedData.message}</strong>
          {trustedData.names.length > 0 && (
            <p className="trusted-names">
              {trustedData.names.join(', ')}
            </p>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" />
        <p>Loading provider details...</p>
      </div>
    );
  }

  if (error || !provider) {
    return (
      <div className="error">
        <AlertCircle className="error-icon" />
        <p>{error || 'Provider not found'}</p>
        <button onClick={fetchProviderDetail} className="retry-btn">
          Try Again
        </button>
        <button onClick={handleBack} className="back-btn">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="provider-detail">
      <div className="header">
        <button onClick={handleBack} className="back-button">
          <ArrowLeft size={20} />
          Back
        </button>
      </div>

      <div className="provider-info">
        <div className="provider-header">
          <h1>{provider.name}</h1>
          <div className="category-badge">{provider.category}</div>
        </div>

        <div className="rating-section">
          <div className="rating">
            {renderStars(provider.rating)}
            <span className="rating-text">
              {provider.rating} ({provider.total_reviews} reviews)
            </span>
          </div>
          <div className="experience">
            {provider.experience_years} years of experience
          </div>
        </div>

        <div className="contact-info">
          <div className="contact-item">
            <Phone size={20} />
            <span>{provider.phone}</span>
            <button 
              className="call-btn"
              onClick={() => window.open(`tel:${provider.phone}`)}
            >
              Call Now
            </button>
          </div>

          {provider.email && (
            <div className="contact-item">
              <Mail size={20} />
              <span>{provider.email}</span>
              <button 
                className="email-btn"
                onClick={() => window.open(`mailto:${provider.email}`)}
              >
                Email
              </button>
            </div>
          )}

          {provider.address && (
            <div className="contact-item">
              <MapPin size={20} />
              <span>{provider.address}</span>
            </div>
          )}
        </div>

        {renderTrustedBy(trustedBy)}

        <div className="action-buttons">
          <button 
            className="book-btn primary"
            onClick={() => alert('Booking system coming soon!')}
          >
            <Calendar size={20} />
            Book Appointment
          </button>
          
          <button 
            className="review-btn secondary"
            onClick={() => alert('Review system coming soon!')}
          >
            <MessageCircle size={20} />
            Write Review
          </button>
        </div>
      </div>

      {reviews.length > 0 && (
        <div className="reviews-section">
          <h2>Recent Reviews</h2>
          <div className="reviews-list">
            {reviews.map((review, index) => (
              <div key={index} className="review-card">
                <div className="review-header">
                  <span className="reviewer-name">{review.user}</span>
                  <div className="review-rating">
                    {renderStars(review.rating)}
                  </div>
                  <span className="review-date">{review.created_at}</span>
                </div>
                
                {review.comment && (
                  <p className="review-comment">{review.comment}</p>
                )}
                
                <div className="review-footer">
                  {review.is_trusted && (
                    <div className="trusted-review">
                      <ThumbsUp size={16} />
                      <span>Trusted review</span>
                    </div>
                  )}
                  
                  {review.service_date && (
                    <span className="service-date">
                      Service date: {review.service_date}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProviderDetail;