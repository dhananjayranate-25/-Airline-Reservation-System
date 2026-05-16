// Navigation
function toggleMobileMenu() {
    document.querySelector('.nav-links').classList.toggle('active');
}

function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
}

function goToHome() {
    window.location.href = '/';
}

function goToSearch() {
    window.location.href = '/app?tab=search';
}

function goToCost() {
    window.location.href = '/app?tab=cost';
}

function goToBooking() {
    // Check if user is logged in before booking
    if (!currentUser) {
        showLoginModal();
        alert('Please login to book tickets!');
        return;
    }
    window.location.href = '/app?tab=booking';
}

function goToSeat() {
    window.location.href = '/app?tab=seat';
}

function goToAdmin() {
    window.location.href = '/admin';
}

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

// Authentication Functions
let currentUser = null;
let isAdmin = false;

document.addEventListener('DOMContentLoaded', () => {
    // Add animation classes to sections
    const sections = document.querySelectorAll('.feature-card, .testimonial-card, .benefit-icon');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'all 0.6s ease';
        observer.observe(section);
    });
    
    // Check if user is logged in
    checkAuthStatus();
});

async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        if (data.logged_in) {
            currentUser = data.user;
            isAdmin = data.is_admin || false;
            updateHomeUserUI(data.user);
            updateHomeAdminLink();
        } else {
            currentUser = null;
            isAdmin = false;
            const adminLink = document.getElementById('homeAdminLink');
            if (adminLink) adminLink.style.display = 'none';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function updateHomeAdminLink() {
    const adminLink = document.getElementById('homeAdminLink');
    if (adminLink) {
        adminLink.style.display = isAdmin ? 'inline-block' : 'none';
    }
}

function updateHomeUserUI(user) {
    const userInfo = document.getElementById('homeUserInfo');
    const loginBtn = document.getElementById('homeLoginBtn');
    const userName = document.getElementById('homeUserName');
    
    if (user) {
        userInfo.style.display = 'flex';
        loginBtn.style.display = 'none';
        userName.textContent = user.name;
    } else {
        userInfo.style.display = 'none';
        loginBtn.style.display = 'flex';
    }
}

function showLoginModal() {
    document.getElementById('authModal').classList.add('show');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('show');
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
}

function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('.auth-tab');
    tabs.forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    if (tab === 'login') {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('registerForm').style.display = 'none';
    } else {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            isAdmin = data.is_admin || false;
            updateHomeUserUI(data);
            updateHomeAdminLink();
            closeAuthModal();
            // Redirect to booking page after successful login
            window.location.href = '/app?tab=booking';
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        alert('Login failed. Please try again.');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            isAdmin = data.is_admin || false;
            updateHomeUserUI(data);
            updateHomeAdminLink();
            closeAuthModal();
            // Redirect to booking page after successful registration
            window.location.href = '/app?tab=booking';
        } else {
            alert(data.error || 'Registration failed');
        }
    } catch (error) {
        alert('Registration failed. Please try again.');
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        updateHomeUserUI(null);
        alert('You have been logged out.');
    } catch (error) {
        alert('Logout failed');
    }
}

// Animate on scroll
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroElements = document.querySelectorAll('.hero-text, .hero-image');
    
    heroElements.forEach(el => {
        el.style.transform = `translateY(${scrolled * 0.1}px)`;
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.style.background = 'rgba(10, 10, 15, 0.95)';
        header.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
    } else {
        header.style.background = 'rgba(10, 10, 15, 0.8)';
        header.style.boxShadow = 'none';
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Add animation class
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    /* Auth Modal Styles */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 1000;
        align-items: center;
        justify-content: center;
    }
    
    .modal.show {
        display: flex;
    }
    
    .modal-content {
        background: #1e293b;
        border-radius: 16px;
        max-width: 420px;
        width: 90%;
        position: relative;
        animation: slideUp 0.4s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .modal-close {
        position: absolute;
        top: 16px;
        right: 16px;
        background: #0f172a;
        border: none;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        color: #94a3b8;
        cursor: pointer;
    }
    
    .modal-close:hover {
        background: #ef4444;
        color: white;
    }
    
    .auth-container {
        padding: 30px;
    }
    
    .auth-tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 30px;
    }
    
    .auth-tab {
        flex: 1;
        padding: 12px;
        background: transparent;
        border: 2px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        color: #94a3b8;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
    }
    
    .auth-tab.active {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-color: transparent;
        color: white;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        font-size: 13px;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 8px;
    }
    
    .form-group label i {
        color: #6366f1;
        margin-right: 8px;
    }
    
    .form-control {
        width: 100%;
        padding: 12px 16px;
        background: #0f172a;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        color: white;
        font-size: 14px;
    }
    
    .form-control:focus {
        outline: none;
        border-color: #6366f1;
    }
    
    .btn {
        padding: 14px 24px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        width: 100%;
    }
    
    .auth-note {
        margin-top: 20px;
        padding: 12px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        text-align: center;
    }
    
    .auth-note p {
        font-size: 12px;
        color: #64748b;
        margin: 0;
    }
    
    .auth-note i {
        color: #6366f1;
        margin-right: 6px;
    }
    
    /* Auth Buttons */
    .auth-buttons {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .login-btn {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .user-avatar {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .user-avatar i {
        color: white;
        font-size: 14px;
    }
    
    .user-name {
        font-size: 14px;
        font-weight: 500;
        color: white;
    }
    
    .logout-btn {
        background: transparent;
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        cursor: pointer;
    }
    
    .logout-btn:hover {
        background: #ef4444;
        color: white;
    }
`;
document.head.appendChild(style);

// Parallax effect for images
document.addEventListener('mousemove', (e) => {
    const cards = document.querySelectorAll('.float-card');
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;
    
    cards.forEach((card, index) => {
        const depth = index + 1;
        card.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
    });
});

// Close modal on outside click
document.getElementById('authModal')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('authModal')) {
        closeAuthModal();
    }
});