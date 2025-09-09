// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './components/Home';
import ServiceProviders from './components/ServiceProviders';
import ProviderDetail from './components/ProviderDetail';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/service/:categoryName" element={<ServiceProviders />} />
            <Route path="/provider/:providerId" element={<ProviderDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;