// src/components/ProviderDetail.js
// import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { apiService } from '../services/api';
import React, { useState, useEffect, useContext, useCallback } from 'react';
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
  ThumbsDown,
  RefreshCw,
  AlertCircle,
  X,
  Send
} from 'lucide-react';
import './ProviderDetail.css';

const ProviderDetail = () => {
  const { providerId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useContext(AuthContext);
  const [provider, setProvider] = useState(null);
  const [trustedBy, setTrustedBy] = useState(null);
  const [contactReviews, setContactReviews] = useState([]);
  const [otherReviews, setOtherReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [bookingData, setBookingData] = useState({
    booking_date: '',
    booking_time: '',
    notes: ''
  });
  const [reviewData, setReviewData] = useState({
    rating: 0,
    comment: '',
    is_trusted: false
  });
  const [bookingLoading, setBookingLoading] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);

  const fetchProviderDetail = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getProviderDetail(providerId);
      console.log('Full API response:', data);
      console.log('Reviews data:', data.reviews);
      console.log('Contact reviews:', data.reviews?.from_contacts);
      console.log('Other reviews:', data.reviews?.from_others);
      console.log('Trusted by:', data.trusted_by);
      setProvider(data.provider);
      setTrustedBy(data.trusted_by);

      // Split reviews into contact and other reviews
      const allReviews = data.recent_reviews || [];
      const contacts = allReviews.filter(review => review.is_contact);
      const others = allReviews.filter(review => !review.is_contact);

      if (data.reviews) {
        setContactReviews(data.reviews.from_contacts || []);
        setOtherReviews(data.reviews.from_others || []);
      } else {
        setContactReviews([]);
        setOtherReviews([]);
      }
      setError(null);
    } catch (err) {
      setError('Failed to load provider details. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  }, [providerId]);

  // Auto-update is_trusted based on rating
  useEffect(() => {
    if (reviewData.rating < 4) {
      setReviewData(prev => ({ ...prev, is_trusted: false }));
    }
  }, [reviewData.rating]);

  useEffect(() => {
    fetchProviderDetail();
  }, [fetchProviderDetail]);

  const handleBack = () => {
    navigate(-1);
  };

  const handleBookNow = () => {
    if (!isAuthenticated()) {
      // Save current location and provider ID
      localStorage.setItem('redirectAfterLogin', `/provider/${providerId}`);
      alert('Please login to book an appointment');
      navigate('/login');
      return;
    }
    setShowBookingModal(true);
  };

  const handleWriteReview = () => {
    if (!isAuthenticated()) {
      alert('Please login to write a review');
      navigate('/login');
      return;
    }
    setShowReviewModal(true);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setBookingLoading(true);

    try {
      const bookingPayload = {
        provider_id: provider.id,
        booking_date: bookingData.booking_date,
        booking_time: bookingData.booking_time,
        notes: bookingData.notes || ''
      };

      await apiService.createBooking(bookingPayload);
      alert('Booking created successfully!');
      setShowBookingModal(false);
      setBookingData({ booking_date: '', booking_time: '', notes: '' });
      navigate('/my-bookings');
    } catch (err) {
      console.error('Booking error:', err);
      alert(err.error || err.message || 'Failed to create booking. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();

    if (reviewData.rating === 0) {
      alert('Please select a rating');
      return;
    }

    setReviewLoading(true);

    try {
      await apiService.submitReview(providerId, reviewData);
      alert('Review submitted successfully!');
      setShowReviewModal(false);
      setReviewData({ rating: 0, comment: '', is_trusted: false });
      fetchProviderDetail(); // Refresh to show new review
    } catch (err) {
      console.error('Review error:', err);
      alert(err.error || err.message || 'Failed to submit review. Please try again.');
    } finally {
      setReviewLoading(false);
    }
  };

  const renderStars = (rating, interactive = false, onStarClick = null) => {
    const stars = [];

    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= rating;
      stars.push(
        <Star
          key={i}
          className={`star ${isFilled ? 'filled' : 'empty'} ${interactive ? 'interactive' : ''}`}
          size={interactive ? 24 : 16}
          onClick={() => interactive && onStarClick && onStarClick(i)}
          style={{ cursor: interactive ? 'pointer' : 'default' }}
        />
      );
    }

    return stars;
  };

  const renderTrustedBy = (trustedData) => {
    if (!trustedData || trustedData.count === 0) {
      return (
        <div className="trusted-section no-trust">
          <Users size={20} />
          <span>No friends have used this service yet</span>
        </div>
      );
    }

    return (
      <div className="trusted-section has-trust">
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

  // Check if review is from current user
  const isUserReview = (review) => {
    return user && review.user === user.username;
  };

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" size={48} />
        <p>Loading provider details...</p>
      </div>
    );
  }

  if (error || !provider) {
    return (
      <div className="error">
        <AlertCircle className="error-icon" size={48} />
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
          <button className="book-btn primary" onClick={handleBookNow}>
            <Calendar size={20} />
            Book Appointment
          </button>

          <button className="review-btn secondary" onClick={handleWriteReview}>
            <MessageCircle size={20} />
            Write Review
          </button>
        </div>
      </div>

      {/* Reviews Section */}
      {(contactReviews.length > 0 || otherReviews.length > 0) && (
        <div className="reviews-section">
          <h2>
            <MessageCircle size={24} />
            Reviews & Ratings
          </h2>

          {/* Reviews from Contacts */}
          {contactReviews.length > 0 && (
            <div className="contact-reviews">
              <h3 className="reviews-subtitle">
                <Users size={20} />
                Reviews from Your Contacts
              </h3>
              <div className="reviews-list">
                {contactReviews.map((review, index) => (
                  <div key={`contact-${index}`} className={`review-card contact-review ${isUserReview(review) ? 'user-review' : ''}`}>
                    {isUserReview(review) ? (
                      <div className="your-review-badge">Your Review</div>
                    ) : (
                      <div className="contact-badge">Your Contact</div>
                    )}
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
                      {review.is_trusted ? (
                        <div className="trusted-review">
                          <ThumbsUp size={16} />
                          <span>Recommends</span>
                        </div>
                      ) : (
                        <div className="not-trusted-review">
                          <ThumbsDown size={16} />
                          <span>Not recommended</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reviews from Others */}
          {otherReviews.length > 0 && (
            <div className="other-reviews">
              <h3 className="reviews-subtitle">Other Reviews</h3>
              <div className="reviews-list">
                {otherReviews.map((review, index) => (
                  <div key={`other-${index}`} className={`review-card ${isUserReview(review) ? 'user-review' : ''}`}>
                    {isUserReview(review) && (
                      <div className="your-review-badge">Your Review</div>
                    )}
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
                      {review.is_trusted ? (
                        <div className="trusted-review">
                          <ThumbsUp size={16} />
                          <span>Recommends</span>
                        </div>
                      ) : (
                        <div className="not-trusted-review">
                          <ThumbsDown size={16} />
                          <span>Not recommended</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Booking Modal */}
      {showBookingModal && (
        <>
          <div className="modal-overlay" onClick={() => setShowBookingModal(false)}></div>
          <div className="booking-modal modal">
            <div className="modal-header">
              <h2>Book Appointment</h2>
              <button className="close-modal" onClick={() => setShowBookingModal(false)}>
                <X size={24} />
              </button>
            </div>

            <div className="modal-provider-info">
              <h3>{provider.name}</h3>
              <p>{provider.category}</p>
            </div>

            <form onSubmit={handleBookingSubmit} className="booking-form">
              <div className="form-group">
                <label htmlFor="booking_date">
                  <Calendar size={18} />
                  Select Date
                </label>
                <input
                  type="date"
                  id="booking_date"
                  value={bookingData.booking_date}
                  onChange={(e) => setBookingData({ ...bookingData, booking_date: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="booking_time">
                  <Calendar size={18} />
                  Select Time
                </label>
                <input
                  type="time"
                  id="booking_time"
                  value={bookingData.booking_time}
                  onChange={(e) => setBookingData({ ...bookingData, booking_time: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="notes">
                  <MessageCircle size={18} />
                  Additional Notes (Optional)
                </label>
                <textarea
                  id="notes"
                  rows="4"
                  value={bookingData.notes}
                  onChange={(e) => setBookingData({ ...bookingData, notes: e.target.value })}
                  placeholder="Any specific requirements or address details..."
                ></textarea>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowBookingModal(false)}
                  disabled={bookingLoading}
                >
                  Cancel
                </button>
                <button type="submit" className="confirm-btn" disabled={bookingLoading}>
                  {bookingLoading ? 'Booking...' : 'Confirm Booking'}
                </button>
              </div>
            </form>
          </div>
        </>
      )}

      {/* Review Modal */}
      {showReviewModal && (
        <>
          <div className="modal-overlay" onClick={() => setShowReviewModal(false)}></div>
          <div className="review-modal modal">
            <div className="modal-header">
              <h2>Write a Review</h2>
              <button className="close-modal" onClick={() => setShowReviewModal(false)}>
                <X size={24} />
              </button>
            </div>

            <div className="modal-provider-info">
              <h3>{provider.name}</h3>
              <p>{provider.category}</p>
            </div>

            <form onSubmit={handleReviewSubmit} className="review-form">
              <div className="form-group">
                <label>
                  <Star size={18} />
                  Your Rating
                </label>
                <div className="star-rating-input">
                  {renderStars(reviewData.rating, true, (rating) =>
                    setReviewData({ ...reviewData, rating })
                  )}
                  <span className="rating-label">
                    {reviewData.rating > 0 ? `${reviewData.rating} Star${reviewData.rating > 1 ? 's' : ''}` : 'Select rating'}
                  </span>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="comment">
                  <MessageCircle size={18} />
                  Your Review (Optional)
                </label>
                <textarea
                  id="comment"
                  rows="4"
                  value={reviewData.comment}
                  onChange={(e) => setReviewData({ ...reviewData, comment: e.target.value })}
                  placeholder="Share your experience with this service provider..."
                ></textarea>
              </div>

              {/* Conditional Recommendation - Only show if rating >= 4 */}
              {reviewData.rating >= 4 && (
                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={reviewData.is_trusted}
                      onChange={(e) => setReviewData({ ...reviewData, is_trusted: e.target.checked })}
                    />
                    <ThumbsUp size={18} />
                    <span>I recommend this service provider</span>
                  </label>
                </div>
              )}

              {/* Show info message for low ratings */}
              {reviewData.rating > 0 && reviewData.rating < 4 && (
                <div className="rating-info">
                  <AlertCircle size={16} />
                  <span>Your rating indicates you don't recommend this provider</span>
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowReviewModal(false)}
                  disabled={reviewLoading}
                >
                  Cancel
                </button>
                <button type="submit" className="confirm-btn" disabled={reviewLoading}>
                  {reviewLoading ? (
                    'Submitting...'
                  ) : (
                    <>
                      <Send size={18} />
                      Submit Review
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </>
      )}
    </div>
  );
};

export default ProviderDetail;