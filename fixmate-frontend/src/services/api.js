// src/services/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  // Helper method to get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Handle API responses
  async handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
      throw data;
    }

    return data;
  }

  // Auth APIs
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/api/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    return this.handleResponse(response);
  }

  async login(credentials) {
    const response = await fetch(`${API_BASE_URL}/api/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials)
    });

    return this.handleResponse(response);
  }

  async getUserProfile() {
    const response = await fetch(`${API_BASE_URL}/api/profile/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  // Service Provider APIs
  async getCategories() {
    const response = await fetch(`${API_BASE_URL}/`);
    return this.handleResponse(response);
  }

  async getProviders(categoryName) {
    const response = await fetch(`${API_BASE_URL}/service/${categoryName}/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getProviderDetail(providerId) {
    const headers = this.getAuthHeaders();
    console.log('🔑 Auth headers being sent:', headers);
    console.log('🔑 Token exists:', !!localStorage.getItem('access_token'));

    const response = await fetch(`${API_BASE_URL}/provider/${providerId}/`, {
      headers: headers
    });
    return this.handleResponse(response);
  }

  // Review APIs
  async submitReview(providerId, reviewData) {
    const response = await fetch(`${API_BASE_URL}/api/provider/${providerId}/review/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(reviewData)
    });

    return this.handleResponse(response);
  }

  // Booking APIs
  async createBooking(bookingData) {
    const response = await fetch(`${API_BASE_URL}/api/bookings/create/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(bookingData)
    });

    return this.handleResponse(response);
  }

  async getUserBookings() {
    const response = await fetch(`${API_BASE_URL}/api/bookings/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  async cancelBooking(bookingId) {
    const response = await fetch(`${API_BASE_URL}/api/bookings/${bookingId}/cancel/`, {
      method: 'PUT',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  // Utility
  async populateData() {
    const response = await fetch(`${API_BASE_URL}/populate-data/`);
    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();