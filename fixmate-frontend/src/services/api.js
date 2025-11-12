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

  // ==================== AUTH APIs ====================
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

  // ==================== SERVICE PROVIDER APIs ====================
  async getCategories() {
    const response = await fetch(`${API_BASE_URL}/`);
    return this.handleResponse(response);
  }

  async getProviders(categoryName, city = null) {
    let url = `${API_BASE_URL}/service/${categoryName}/`;
    if (city) {
      url += `?city=${encodeURIComponent(city)}`;
    }
    
    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });
    
    return this.handleResponse(response);
  }

  async getProviderDetail(providerId) {
    const response = await fetch(`${API_BASE_URL}/provider/${providerId}/`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // ==================== REVIEW APIs ====================
  async submitReview(providerId, reviewData) {
    const response = await fetch(`${API_BASE_URL}/api/provider/${providerId}/review/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(reviewData)
    });

    return this.handleResponse(response);
  }

  // ==================== BOOKING APIs (Customer) ====================
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

  // ==================== PROVIDER REGISTRATION & AUTH ====================
  async providerRegister(userData) {
    const response = await fetch(`${API_BASE_URL}/api/provider/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    return this.handleResponse(response);
  }

  // ==================== PROVIDER DASHBOARD ====================
  async getProviderDashboard() {
    const response = await fetch(`${API_BASE_URL}/api/provider/dashboard/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  // ==================== PROVIDER BOOKINGS ====================
  async getProviderBookings() {
    const response = await fetch(`${API_BASE_URL}/api/provider/bookings/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  async acceptBooking(bookingId) {
    const response = await fetch(`${API_BASE_URL}/api/provider/bookings/${bookingId}/accept/`, {
      method: 'PUT',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);  // ✅ FIXED: Use handleResponse
  }

  async rejectBooking(bookingId) {
    const response = await fetch(`${API_BASE_URL}/api/provider/bookings/${bookingId}/reject/`, {
      method: 'PUT',
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);  // ✅ FIXED: Use handleResponse
  }

  async completeBooking(bookingId, completionNotes) {
    const response = await fetch(`${API_BASE_URL}/api/provider/bookings/${bookingId}/complete/`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ completion_notes: completionNotes })
    });

    return this.handleResponse(response);  // ✅ FIXED: Use handleResponse
  }

  // ==================== PROVIDER PROFILE ====================
  async getProviderProfile() {
    const response = await fetch(`${API_BASE_URL}/api/provider/profile/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  async updateProviderProfile(profileData) {
    const response = await fetch(`${API_BASE_URL}/api/provider/profile/`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData)
    });

    return this.handleResponse(response);
  }

  // ==================== PROVIDER REVIEWS ====================
  async getProviderReviews() {
    const response = await fetch(`${API_BASE_URL}/api/provider/reviews/`, {
      headers: this.getAuthHeaders()
    });

    return this.handleResponse(response);
  }

  // ==================== UTILITY ====================
  async populateData() {
    const response = await fetch(`${API_BASE_URL}/populate-data/`);
    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();