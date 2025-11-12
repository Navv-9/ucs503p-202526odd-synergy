// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LocationProvider } from './context/LocationContext';
import './App.css';
import Home from './components/Home';
import ServiceProviders from './components/ServiceProviders';
import ProviderDetail from './components/ProviderDetail';
import Login from './components/Login';
import Register from './components/Register';
import MyBookings from './components/MyBookings';
import Navbar from './components/Navbar';

// Provider Components
import ProviderRegister from './components/ProviderRegister';
import ProviderDashboard from './components/ProviderDashboard';
import ProviderBookings from './components/ProviderBookings';
import ProviderProfile from './components/ProviderProfile';

function App() {
  return (
    <AuthProvider>
      <LocationProvider>
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

                {/* Provider Routes */}
                <Route path="/provider/register" element={<ProviderRegister />} />
                <Route path="/provider/dashboard" element={<ProviderDashboard />} />
                <Route path="/provider/bookings" element={<ProviderBookings />} />
                <Route path="/provider/profile" element={<ProviderProfile />} />
              </Routes>
            </main>
          </div>
        </Router>
      </LocationProvider>
    </AuthProvider>
  );
}

export default App;