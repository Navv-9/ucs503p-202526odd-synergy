// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import './App.css';
import Home from './components/Home';
import ServiceProviders from './components/ServiceProviders';
import ProviderDetail from './components/ProviderDetail';
import Login from './components/Login';
import Register from './components/Register';
import MyBookings from './components/MyBookings';
import Navbar from './components/Navbar';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/service/:categoryName" element={<ServiceProviders />} />
              <Route path="/provider/:providerId" element={<ProviderDetail />} />
              <Route path="/my-bookings" element={<MyBookings />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;