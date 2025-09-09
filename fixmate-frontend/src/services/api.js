// src/services/api.js
import axios from 'axios';

const BASE_URL = 'http://localhost:8000'; // Django development server

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Get all service categories
  getCategories: async () => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  // Get providers for a specific category
  getProviders: async (categoryName) => {
    try {
      const response = await api.get(`/service/${categoryName}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching providers:', error);
      throw error;
    }
  },

  // Get detailed info about a provider
  getProviderDetail: async (providerId) => {
    try {
      const response = await api.get(`/provider/${providerId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching provider details:', error);
      throw error;
    }
  },

  // Populate fake data (for testing)
  populateData: async () => {
    try {
      const response = await api.get('/populate-data/');
      return response.data;
    } catch (error) {
      console.error('Error populating data:', error);
      throw error;
    }
  }
};

export default api;