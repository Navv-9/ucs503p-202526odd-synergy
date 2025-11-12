// src/components/CitySelector.js
import React, { useContext, useState } from 'react';
import { createPortal } from 'react-dom';
import { LocationContext } from '../context/LocationContext';
import { MapPin, X } from 'lucide-react';
import { INDIAN_CITIES } from '../utils/cities';
import './CitySelector.css';

const CitySelector = () => {
  const { selectedCity, changeCity, detectCity, isDetecting } = useContext(LocationContext);
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCities = INDIAN_CITIES.filter(city =>
    city.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCitySelect = (city) => {
    changeCity(city);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleDetectCity = async () => {
    await detectCity();
    setIsOpen(false);
  };

  // Modal component that will be rendered via portal
  const modalContent = isOpen ? (
    <div className="city-modal-overlay" onClick={() => setIsOpen(false)}>
      <div className="city-modal" onClick={(e) => e.stopPropagation()}>
        <div className="city-modal-header">
          <h2>Select Your City</h2>
          <button className="close-btn" onClick={() => setIsOpen(false)}>
            <X size={24} />
          </button>
        </div>

        <div className="city-modal-body">
          <button 
            className="detect-city-btn" 
            onClick={handleDetectCity}
            disabled={isDetecting}
          >
            <MapPin size={18} />
            {isDetecting ? 'Detecting...' : 'Detect My City'}
          </button>

          <div className="city-search">
            <input
              type="text"
              placeholder="Search cities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="city-list">
            {filteredCities.map((city) => (
              <button
                key={city}
                className={`city-item ${city === selectedCity ? 'active' : ''}`}
                onClick={() => handleCitySelect(city)}
              >
                {city}
                {city === selectedCity && <span className="checkmark">✓</span>}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  ) : null;

  return (
    <>
      <button className="city-selector-btn" onClick={() => setIsOpen(true)}>
        <MapPin size={18} />
        <span>{selectedCity}</span>
      </button>

      {/* Render modal outside navbar using Portal */}
      {modalContent && createPortal(modalContent, document.body)}
    </>
  );
};

export default CitySelector;