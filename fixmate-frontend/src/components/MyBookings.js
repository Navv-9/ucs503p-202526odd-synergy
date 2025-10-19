// src/components/MyBookings.js
// import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { apiService } from '../services/api';
import {
  Calendar,
  Clock,
  Phone,
  MapPin,
  X,
  CheckCircle,
  XCircle,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import './MyBookings.css';
import React, { useState, useEffect, useContext, useCallback } from 'react';

const MyBookings = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useContext(AuthContext);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getUserBookings();
      setBookings(data.bookings || []);
      setError(null);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setBookings([]);
        setError(null);
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);
  useEffect(() => {
  if (!isAuthenticated()) {
    localStorage.setItem('redirectAfterLogin', '/my-bookings');
    navigate('/login');
    return;
  }
  fetchBookings();
}, [isAuthenticated, navigate, fetchBookings]);


  const categorizeBookings = () => {
    const now = new Date();

    const active = bookings.filter(b => {
      const bookingDate = new Date(b.booking_date);
      return (b.status === 'pending' || b.status === 'confirmed') && bookingDate >= now;
    }).sort((a, b) => new Date(a.booking_date) - new Date(b.booking_date));

    const completed = bookings.filter(b => b.status === 'completed')
      .sort((a, b) => new Date(b.booking_date) - new Date(a.booking_date));

    const cancelled = bookings.filter(b => b.status === 'cancelled')
      .sort((a, b) => new Date(b.booking_date) - new Date(a.booking_date));

    return { active, completed, cancelled };
  };

  const { active, completed, cancelled } = categorizeBookings();

  const handleCancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      await apiService.cancelBooking(bookingId);
      fetchBookings(); // Refresh bookings
      alert('Booking cancelled successfully!');
    } catch (err) {
      alert('Failed to cancel booking. Please try again.');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'status-pending', icon: Clock, text: 'Pending' },
      confirmed: { color: 'status-confirmed', icon: CheckCircle, text: 'Confirmed' },
      completed: { color: 'status-completed', icon: CheckCircle, text: 'Completed' },
      cancelled: { color: 'status-cancelled', icon: XCircle, text: 'Cancelled' }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const IconComponent = config.icon;

    return (
      <div className={`status-badge ${config.color}`}>
        <IconComponent size={16} />
        <span>{config.text}</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" />
        <p>Loading your bookings...</p>
      </div>
    );
  }

  // Add this component inside MyBookings component, before the return
  const BookingCard = ({ booking, onCancel }) => (
    <div className="booking-card">
      <div className="booking-header">
        <div className="booking-title">
          <h3>{booking.provider_name}</h3>
          <span className="category-tag">{booking.provider_category}</span>
        </div>
        {getStatusBadge(booking.status)}
      </div>

      <div className="booking-details">
        <div className="detail-row">
          <Calendar size={18} />
          <span>{new Date(booking.booking_date).toLocaleDateString('en-IN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}</span>
        </div>

        <div className="detail-row">
          <Clock size={18} />
          <span>{booking.booking_time}</span>
        </div>

        <div className="detail-row">
          <Phone size={18} />
          <span>{booking.provider_phone}</span>
        </div>

        {booking.notes && (
          <div className="detail-row notes">
            <MapPin size={18} />
            <span>{booking.notes}</span>
          </div>
        )}
      </div>

      <div className="booking-footer">
        <span className="booking-date">
          Booked on: {new Date(booking.created_at).toLocaleDateString()}
        </span>

        {booking.status !== 'cancelled' && booking.status !== 'completed' && (
          <button
            className="cancel-booking-btn"
            onClick={() => onCancel(booking.id)}
          >
            <X size={16} />
            Cancel Booking
          </button>
        )}
      </div>
    </div>
  );

  if (error) {
    return (
      <div className="error">
        <AlertCircle className="error-icon" />
        <p>{error}</p>
        <button onClick={fetchBookings} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="my-bookings">
      <div className="bookings-header">
        <h1>My Bookings</h1>
        <p>{bookings.length} total booking{bookings.length !== 1 ? 's' : ''}</p>
      </div>

      {bookings.length === 0 ? (
        <div className="no-bookings">
          <Calendar size={64} className="no-bookings-icon" />
          <h2>No Bookings Yet</h2>
          <p>You haven't made any bookings yet. Browse services to get started!</p>
          <button onClick={() => navigate('/')} className="browse-btn">
            Browse Services
          </button>
        </div>
      ) : (
        <>
          {/* Active Bookings Section */}
          {active.length > 0 && (
            <div className="bookings-section">
              <div className="section-header">
                <h2>Active Bookings</h2>
                <span className="count-badge">{active.length}</span>
              </div>
              <div className="bookings-list">
                {active.map((booking) => (
                  <BookingCard
                    key={booking.id}
                    booking={booking}
                    onCancel={handleCancelBooking}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed Bookings Section */}
          {completed.length > 0 && (
            <div className="bookings-section">
              <div className="section-header">
                <h2>Completed Bookings</h2>
                <span className="count-badge">{completed.length}</span>
              </div>
              <div className="bookings-list">
                {completed.map((booking) => (
                  <BookingCard
                    key={booking.id}
                    booking={booking}
                    onCancel={handleCancelBooking}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Cancelled Bookings Section */}
          {cancelled.length > 0 && (
            <div className="bookings-section">
              <div className="section-header">
                <h2>Cancelled Bookings</h2>
                <span className="count-badge">{cancelled.length}</span>
              </div>
              <div className="bookings-list">
                {cancelled.map((booking) => (
                  <BookingCard
                    key={booking.id}
                    booking={booking}
                    onCancel={handleCancelBooking}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MyBookings;