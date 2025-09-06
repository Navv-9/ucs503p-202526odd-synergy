import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <div class="container header-container">
            <div class="logo">
                <h1>My<span>Help</span></h1>
            </div>
            <nav>
                <ul>
                    <li><a href="#">Home</a></li>
                    <li><a href="#">Services</a></li>
                    <li><a href="#">How It Works</a></li>
                    <li><a href="#">About Us</a></li>
                    <li><a href="#">Contact</a></li>
                </ul>
            </nav>
            <div class="auth-buttons">
                <a href="#" class="btn btn-outline">Log In</a>
                <a href="#" class="btn btn-primary">Sign Up</a>
            </div>
        </div>
    </header>
    <section class="hero">
        <div class="container hero-content">
            <h1>Find Trusted Local Service Professionals</h1>
            <p>Connect with skilled professionals ready to help at your preferred price</p>
            <div class="search-box">
                <input type="text" placeholder="What service do you need?" />
                <button>Search</button>
            </div>
        </div>
    </section>
    <section class="services">
        <div class="container">
            <div class="section-title">
                <h2>Our Services</h2>
                <p>Browse through our wide range of professional services</p>
            </div>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-wrench"></i>
                    </div>
                    <div class="service-content">
                        <h3>Plumber</h3>
                        <p>Expert plumbing services for leaks, installations, and repairs.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-fan"></i>
                    </div>
                    <div class="service-content">
                        <h3>AC Service/Repair</h3>
                        <p>Professional AC maintenance, servicing, and repair solutions.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-hammer"></i>
                    </div>
                    <div class="service-content">
                        <h3>Carpenter</h3>
                        <p>Skilled carpenters for furniture, repairs, and custom projects.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-cut"></i>
                    </div>
                    <div class="service-content">
                        <h3>Barber</h3>
                        <p>Professional hairstyling and grooming services at your convenience.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <div class="service-content">
                        <h3>Electrician</h3>
                        <p>Certified electricians for installations, repairs, and maintenance.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
                <div class="service-card">
                    <div class="service-icon">
                        <i class="fas fa-tools"></i>
                    </div>
                    <div class="service-content">
                        <h3>Appliance Repair</h3>
                        <p>Expert repair services for all your home appliances.</p>
                        <a href="#">View Details <i class="fas fa-arrow-right"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <section class="how-it-works">
        <div class="container">
            <div class="section-title">
                <h2>How It Works</h2>
                <p>Getting help has never been easier</p>
            </div>
            <div class="steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <h3>Choose a Service</h3>
                    <p>Select from our wide range of professional services</p>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <h3>Compare & Book</h3>
                    <p>View profiles, compare prices, and book your professional</p>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <h3>Get It Done</h3>
                    <p>Relax while our experts deliver quality service</p>
                </div>
            </div>
        </div>
    </section>
    <section class="trust">
        <div class="container">
            <div class="section-title">
                <h2>Why Choose MyHelp</h2>
                <p>Trusted by thousands of customers nationwide</p>
            </div>
            <div class="trust-badges">
                <div class="badge">
                    <i class="fas fa-users"></i>
                    <h3>500+</h3>
                    <p>Verified Professionals</p>
                </div>
                <div class="badge">
                    <i class="fas fa-smile"></i>
                    <h3>10,000+</h3>
                    <p>Happy Customers</p>
                </div>
                <div class="badge">
                    <i class="fas fa-map-marker-alt"></i>
                    <h3>50+</h3>
                    <p>Cities Served</p>
                </div>
            </div>
        </div>
    </section>
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-column">
                    <h3>MyHelp</h3>
                    <p>Connecting customers with trusted local service professionals for mutual benefit.</p>
                    <div class="social-links">
                        <a href="#"><i class="fab fa-facebook-f"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                        <a href="#"><i class="fab fa-linkedin-in"></i></a>
                    </div>
                </div>
                <div class="footer-column">
                    <h3>Services</h3>
                    <ul>
                        <li><a href="#">Plumber</a></li>
                        <li><a href="#">AC Service/Repair</a></li>
                        <li><a href="#">Carpenter</a></li>
                        <li><a href="#">Barber</a></li>
                        <li><a href="#">Electrician</a></li>
                        <li><a href="#">Appliance Repair</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Company</h3>
                    <ul>
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">How It Works</a></li>
                        <li><a href="#">Careers</a></li>
                        <li><a href="#">Press</a></li>
                        <li><a href="#">Blog</a></li>
                    </ul>
                </div>
                <div class="footer-column">
                    <h3>Support</h3>
                    <ul>
                        <li><a href="#">Help Center</a></li>
                        <li><a href="#">Contact Us</a></li>
                        <li><a href="#">Privacy Policy</a></li>
                        <li><a href="#">Terms of Service</a></li>
                        <li><a href="#">Safety Tips</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>Copyright © 2023 MyHelp. All rights reserved.</p>
            </div>
        </div>
    </footer>
    </div>
  );
}

export default App;
