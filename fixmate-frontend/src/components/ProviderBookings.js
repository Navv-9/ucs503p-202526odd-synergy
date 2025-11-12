// src/components/ProviderBookings.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Clock, 
  Phone, 
  MapPin, 
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Package
} from 'lucide-react';
import { apiService } from '../services/api';
import './Login.css';

const ProviderBookings = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [bookings, setBookings] = useState({
    all: [],
    pending: [],
    accepted: [],
    completed: [],
    cancelled: []
  });
  const [activeTab, setActiveTab] = useState('pending');
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const data = await apiService.getProviderBookings();
      console.log('📦 Bookings fetched:', data); // Debug log
      setBookings(data);
      setError('');
    } catch (err) {
      console.error('❌ Error fetching bookings:', err);
      setError('Failed to load bookings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (bookingId) => {
    setActionLoading(bookingId);
    try {
      console.log('✅ Accepting booking:', bookingId);
      await apiService.acceptBooking(bookingId);
      
      // Refresh bookings
      await fetchBookings();
      
      // Show success message
      alert('Booking accepted successfully!');
    } catch (err) {
      console.error('❌ Error accepting booking:', err);
      alert('Failed to accept booking. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (bookingId) => {
    if (!window.confirm('Are you sure you want to reject this booking?')) {
      return;
    }
    
    setActionLoading(bookingId);
    try {
      console.log('❌ Rejecting booking:', bookingId);
      await apiService.rejectBooking(bookingId);
      
      // Refresh bookings
      await fetchBookings();
      
      // Show success message
      alert('Booking rejected successfully!');
    } catch (err) {
      console.error('❌ Error rejecting booking:', err);
      alert('Failed to reject booking. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplete = async (bookingId) => {
    const completionNotes = prompt('Add completion notes (optional):');
    if (completionNotes === null) return;

    setActionLoading(bookingId);
    try {
      console.log('✔️ Completing booking:', bookingId);
      await apiService.completeBooking(bookingId, completionNotes);
      
      // Refresh bookings
      await fetchBookings();
      
      // Show success message
      alert('Booking marked as completed!');
    } catch (err) {
      console.error('❌ Error completing booking:', err);
      alert('Failed to complete booking. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const renderBooking = (booking) => {
    const getInitials = (name) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase();
    };

    return (
      <div key={booking.id} className="booking-card">
        <div className="booking-header">
          <div className="booking-customer">
            <div className="customer-avatar">
              {getInitials(booking.customer_name)}
            </div>
            <div className="customer-info">
              <h3>{booking.customer_name}</h3>
              <p>{booking.customer_phone}</p>
            </div>
          </div>
          <span className={`status-badge ${booking.status}`}>
            {booking.status}
          </span>
        </div>

        <div className="booking-details">
          <div className="booking-detail">
            <Calendar size={18} />
            <span>{booking.booking_date}</span>
          </div>
          <div className="booking-detail">
            <Clock size={18} />
            <span>{booking.booking_time}</span>
          </div>
          <div className="booking-detail">
            <MapPin size={18} />
            <span>{booking.customer_address || 'No address provided'}</span>
          </div>
        </div>

        {booking.notes && (
          <div className="booking-notes">
            <h4>Customer Notes</h4>
            <p>{booking.notes}</p>
          </div>
        )}

        {booking.completion_notes && (
          <div className="booking-notes" style={{ borderLeftColor: '#10b981' }}>
            <h4>Completion Notes</h4>
            <p>{booking.completion_notes}</p>
          </div>
        )}

        <div className="booking-actions">
          {booking.status === 'pending' && (
            <>
              <button
                className="action-btn accept"
                onClick={() => handleAccept(booking.id)}
                disabled={actionLoading === booking.id}
              >
                <CheckCircle size={18} />
                {actionLoading === booking.id ? 'Accepting...' : 'Accept'}
              </button>
              <button
                className="action-btn reject"
                onClick={() => handleReject(booking.id)}
                disabled={actionLoading === booking.id}
              >
                <XCircle size={18} />
                {actionLoading === booking.id ? 'Rejecting...' : 'Reject'}
              </button>
            </>
          )}

          {booking.status === 'accepted' && (
            <button
              className="action-btn complete"
              onClick={() => handleComplete(booking.id)}
              disabled={actionLoading === booking.id}
            >
              <CheckCircle size={18} />
              {actionLoading === booking.id ? 'Completing...' : 'Mark as Completed'}
            </button>
          )}

          {booking.status === 'completed' && (
            <div style={{ color: '#10b981', fontWeight: 600, fontSize: '14px' }}>
              ✓ Service Completed
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bookings-container">
        <div className="loading-state">
          <p>Loading bookings...</p>
        </div>
      </div>
    );
  }

  const currentBookings = bookings[activeTab] || [];

  return (
    <div className="bookings-container">
      <div className="bookings-header">
        <h1>My Bookings</h1>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="tabs-container">
        <button
          className={`tab-btn ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          Pending
          <span className="tab-badge">{bookings.pending.length}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'accepted' ? 'active' : ''}`}
          onClick={() => setActiveTab('accepted')}
        >
          Accepted
          <span className="tab-badge">{bookings.accepted.length}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          Completed
          <span className="tab-badge">{bookings.completed.length}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'cancelled' ? 'active' : ''}`}
          onClick={() => setActiveTab('cancelled')}
        >
          Cancelled/Rejected
          <span className="tab-badge">{bookings.cancelled.length}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All
          <span className="tab-badge">{bookings.all.length}</span>
        </button>
      </div>

      <div className="bookings-list">
        {currentBookings.length > 0 ? (
          currentBookings.map(booking => renderBooking(booking))
        ) : (
          <div className="empty-state">
            <Package size={64} />
            <h3>No {activeTab} bookings</h3>
            <p>You don't have any {activeTab} bookings at the moment.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProviderBookings;