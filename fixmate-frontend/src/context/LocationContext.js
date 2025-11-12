import React, { createContext, useState, useEffect } from 'react';
import { detectCityFromIP } from '../utils/cities';

export const LocationContext = createContext();

export const LocationProvider = ({ children }) => {
  const [selectedCity, setSelectedCity] = useState(
    localStorage.getItem('selectedCity') || 'Patiala'
  );
  const [isDetecting, setIsDetecting] = useState(false);

  useEffect(() => {
    // Auto-detect city on first visit
    const hasDetectedCity = localStorage.getItem('hasDetectedCity');
    
    if (!hasDetectedCity) {
      detectCity();
    }
  }, []);

  const detectCity = async () => {
    setIsDetecting(true);
    try {
      const city = await detectCityFromIP();
      setSelectedCity(city);
      localStorage.setItem('selectedCity', city);
      localStorage.setItem('hasDetectedCity', 'true');
    } catch (error) {
      console.error('City detection failed:', error);
    } finally {
      setIsDetecting(false);
    }
  };

  const changeCity = (city) => {
    setSelectedCity(city);
    localStorage.setItem('selectedCity', city);
  };

  return (
    <LocationContext.Provider value={{ selectedCity, changeCity, isDetecting, detectCity }}>
      {children}
    </LocationContext.Provider>
  );
};