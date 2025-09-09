// src/components/Home.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { 
  Wrench, 
  Scissors, 
  Hammer, 
  Zap, 
  Wind, 
  Settings,
  RefreshCw,
  AlertCircle 
} from 'lucide-react';
import './Home.css';

const categoryIcons = {
  'Plumber': Wrench,
  'Barber': Scissors,
  'Carpenter': Hammer,
  'Electrician': Zap,
  'AC Service/Repair': Wind,
  'Appliance Repair': Settings
};

const Home = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCategories();
      setCategories(data.categories || []);
      setError(null);
    } catch (err) {
      setError('Failed to load categories. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (categoryName) => {
    navigate(`/service/${categoryName}`);
  };

  const handlePopulateData = async () => {
    try {
      setLoading(true);
      await apiService.populateData();
      await fetchCategories(); // Refresh categories
      alert('Test data populated successfully!');
    } catch (err) {
      alert('Failed to populate data. Make sure Django server is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <RefreshCw className="loading-icon" />
        <p>Loading services...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <AlertCircle className="error-icon" />
        <p>{error}</p>
        <button onClick={fetchCategories} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="home">
      <div className="hero-section">
        <h1>Welcome to FixMate</h1>
        <p>Find trusted service providers in your area</p>
        
        {categories.length === 0 && (
          <div className="no-data">
            <p>No services available yet.</p>
            <button onClick={handlePopulateData} className="populate-btn">
              Load Test Data
            </button>
          </div>
        )}
      </div>

      <div className="categories-section">
        <h2>Choose a Service</h2>
        <div className="categories-grid">
          {categories.map((category) => {
            const IconComponent = categoryIcons[category.name] || Settings;
            
            return (
              <div
                key={category.id}
                className="category-card"
                onClick={() => handleCategoryClick(category.name)}
              >
                <div className="category-icon">
                  <IconComponent size={40} />
                </div>
                <h3>{category.name}</h3>
                <p>{category.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {categories.length > 0 && (
        <div className="actions-section">
          <button onClick={handlePopulateData} className="secondary-btn">
            Refresh Test Data
          </button>
        </div>
      )}
    </div>
  );
};

export default Home;