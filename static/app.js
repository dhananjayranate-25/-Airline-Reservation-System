let currentBookingData = null;
let selectedSeat = null;
let occupiedSeats = [];
let currentUser = null;
let isAdmin = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initForms();
    setDefaultDate();
    loadFlightDropdown();
    generateSeatGrid();
    loadOccupiedSeats();
    checkAuthStatus();
    
    // Handle initial tab from URL
    if (activeTab && activeTab !== 'search') {
        const navItem = document.querySelector(`.nav-item[data-tab="${activeTab}"]`);
        if (navItem) {
            navItem.click();
        }
    }
});

// Authentication Functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        console.log('Auth status response:', data);
        isAdmin = data.is_admin || false;
        if (data.logged_in) {
            currentUser = data.user;
            console.log('Setting currentUser:', currentUser);
            updateUserUI(currentUser);
            updateAdminButtons();
            console.log('updateUserUI called');
        } else {
            console.log('User not logged in');
            // Show login button, hide user info
            const userInfo = document.getElementById('userInfo');
            const loginBtn = document.getElementById('loginBtn');
            if (userInfo) userInfo.style.display = 'none';
            if (loginBtn) loginBtn.style.display = 'flex';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

function updateAdminButtons() {
    const viewUsersBtn = document.getElementById('viewUsersBtn');
    if (viewUsersBtn) {
        viewUsersBtn.style.display = isAdmin ? 'flex' : 'none';
    }
}

function updateUserUI(user) {
    const userInfo = document.getElementById('userInfo');
    const loginBtn = document.getElementById('loginBtn');
    const loginBtnTop = document.getElementById('loginBtn');
    const userName = document.getElementById('userName');
    const userIdDisplay = document.getElementById('userIdDisplay');
    
    // Try both selectors for compatibility
    const buttons = [loginBtn, loginBtnTop].filter(Boolean);
    
    if (user) {
        if (userInfo) userInfo.style.display = 'flex';
        buttons.forEach(btn => { if(btn) btn.style.display = 'none'; });
        if (userName) userName.textContent = user.name;
        if (userIdDisplay) userIdDisplay.textContent = user.user_id;
        
        // Auto-fill booking form with user data
        autoFillUserData();
    } else {
        if (userInfo) userInfo.style.display = 'none';
        buttons.forEach(btn => { 
            if(btn) btn.style.display = 'flex'; 
        });
    }
}

function showLoginModal() {
    document.getElementById('authModal').classList.add('show');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('show');
    // Reset forms
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
        console.log('Login response:', data);
        
        if (response.ok) {
            currentUser = {
                user_id: data.user_id,
                name: data.name,
                email: data.email,
                phone: data.phone
            };
            console.log('currentUser set to:', currentUser);
            updateUserUI(currentUser);
            closeAuthModal();
            showSuccess('Welcome back!', `Logged in as ${data.name}`, `User ID: ${data.user_id}`);
            
            // Also autofill in booking form
            autoFillUserData();
        } else {
            showError(data.error || 'Login failed');
        }
    } catch (error) {
        showError('Login failed. Please try again.');
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
        console.log('Register response:', data);
        
        if (response.ok) {
            currentUser = {
                user_id: data.user_id,
                name: data.name,
                email: data.email,
                phone: data.phone
            };
            updateUserUI(currentUser);
            closeAuthModal();
            showSuccess('Registration Successful!', `Welcome ${data.name}!`, `Your User ID: ${data.user_id}<br>You can now book tickets.`);
            
            // Also autofill in booking form
            autoFillUserData();
        } else {
            showError(data.error || 'Registration failed');
        }
    } catch (error) {
        showError('Registration failed. Please try again.');
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        updateUserUI(null);
        showSuccess('Logged Out', 'You have been logged out successfully.');
    } catch (error) {
        showError('Logout failed');
    }
}

// Show Account Details Modal
function showAccountDetails() {
    if (!currentUser) {
        showError('Please login first');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 450px;">
            <button class="modal-close" onclick="this.closest('.modal').remove()">
                <i class="fas fa-times"></i>
            </button>
            <div style="padding: 30px; text-align: center;">
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <i class="fas fa-user" style="font-size: 36px; color: white;"></i>
                </div>
                <h2 style="margin-bottom: 20px; color: white;">My Account</h2>
                <div style="background: var(--dark); border-radius: 12px; padding: 20px; text-align: left;">
                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(99,102,241,0.2);">
                        <label style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Name</label>
                        <p style="font-size: 16px; color: white; margin: 5px 0;">${currentUser.name || 'N/A'}</p>
                    </div>
                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(99,102,241,0.2);">
                        <label style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Email</label>
                        <p style="font-size: 16px; color: white; margin: 5px 0;">${currentUser.email || 'N/A'}</p>
                    </div>
                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(99,102,241,0.2);">
                        <label style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Phone</label>
                        <p style="font-size: 16px; color: white; margin: 5px 0;">${currentUser.phone || 'N/A'}</p>
                    </div>
                    <div>
                        <label style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">User ID</label>
                        <p style="font-size: 16px; color: var(--primary); margin: 5px 0; font-weight: 600;">${currentUser.user_id || 'N/A'}</p>
                    </div>
                </div>
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button onclick="logout(); document.querySelectorAll('.modal').forEach(m => m.remove());" style="flex:1; padding: 12px; background: transparent; border: 1px solid var(--danger); color: var(--danger); border-radius: 8px; cursor: pointer;">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </button>
                    <button onclick="deleteAccount();" style="flex:1; padding: 12px; background: #dc2626; border: none; color: white; border-radius: 8px; cursor: pointer;">
                        <i class="fas fa-trash-alt"></i> Delete Account
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Show All Users Modal
async function showAllUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const users = await response.json();
        
        if (users.length === 0) {
            showError('No users found');
            return;
        }
        
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 700px; max-height: 80vh; overflow-y: auto;">
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
                <div style="padding: 20px;">
                    <h2 style="margin-bottom: 20px; color: white; text-align: center;">
                        <i class="fas fa-users" style="color: var(--primary);"></i> All Users (${users.length})
                    </h2>
                    <div style="background: var(--dark); border-radius: 12px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
                                <tr>
                                    <th style="padding: 12px; text-align: left; color: white; font-size: 12px;">User ID</th>
                                    <th style="padding: 12px; text-align: left; color: white; font-size: 12px;">Name</th>
                                    <th style="padding: 12px; text-align: left; color: white; font-size: 12px;">Email</th>
                                    <th style="padding: 12px; text-align: left; color: white; font-size: 12px;">Phone</th>
                                    <th style="padding: 12px; text-align: left; color: white; font-size: 12px;">Joined</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${users.map(user => `
                                    <tr style="border-bottom: 1px solid rgba(99,102,241,0.1);">
                                        <td style="padding: 12px; color: var(--primary); font-weight: 600;">${user.user_id}</td>
                                        <td style="padding: 12px; color: white;">${user.name}</td>
                                        <td style="padding: 12px; color: var(--text-secondary);">${user.email}</td>
                                        <td style="padding: 12px; color: var(--text-secondary);">${user.phone || 'N/A'}</td>
                                        <td style="padding: 12px; color: var(--text-muted); font-size: 12px;">${user.created_at ? user.created_at.split(' ')[0] : 'N/A'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } catch (error) {
        showError('Failed to load users');
    }
}

async function deleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This will cancel all your bookings and remove all your data permanently!')) {
        return;
    }
    
    if (!confirm('This action cannot be undone. Are you absolutely sure?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/auth/delete-account', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            currentUser = null;
            updateUserUI(null);
            showSuccess('Account Deleted', data.message);
            // Redirect to home page after 2 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showError(data.error || 'Failed to delete account');
        }
    } catch (error) {
        showError('Delete account failed');
    }
}

// Tab Navigation
function initTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.dataset.tab;
            
            // Update nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');
            
            // Load data if needed
            if (tabId === 'cost') {
                loadCostFlights();
            } else if (tabId === 'booking') {
                loadBookingFlights();
                // Auto-fill user data if logged in
                autoFillUserData();
            }
        });
    });
}

function autoFillUserData() {
    if (!currentUser) return;
    
    // Auto-fill booking form with user data
    if (document.getElementById('passengerName')) {
        document.getElementById('passengerName').value = currentUser.name || '';
    }
    if (document.getElementById('passengerEmail')) {
        document.getElementById('passengerEmail').value = currentUser.email || '';
    }
    if (document.getElementById('passengerPhone')) {
        document.getElementById('passengerPhone').value = currentUser.phone || '';
    }
}

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('travelDate').value = today;
}

// Form Initialization
function initForms() {
    // Search Form
    document.getElementById('searchForm').addEventListener('submit', handleSearchFlights);
    
    // Cost Form
    document.getElementById('costForm').addEventListener('submit', handleCalculateCost);
    
    // Booking Form
    document.getElementById('bookingForm').addEventListener('submit', handleBookTicket);
}

// Quick Search from Panel
function quickSearch() {
    const origin = document.getElementById('panelOrigin')?.value;
    const destination = document.getElementById('panelDestination')?.value;
    
    if (origin && destination && origin !== destination) {
        // Switch to search tab
        const searchTab = document.querySelector('.nav-item[data-tab="search"]');
        if (searchTab) searchTab.click();
        
        // Set the values in search form
        const searchOrigin = document.getElementById('origin');
        const searchDestination = document.getElementById('destination');
        if (searchOrigin && searchDestination) {
            searchOrigin.value = origin;
            searchDestination.value = destination;
            // Trigger search
            handleSearchFlights(new Event('submit'));
        }
    }
}

// API Helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(endpoint, options);
    return response.json();
}

// Search Flights
async function handleSearchFlights(e) {
    e.preventDefault();
    
    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const classType = document.getElementById('searchClass').value;
    
    if (origin === destination) {
        showError('Origin and destination cannot be the same!');
        return;
    }
    
    try {
        const flights = await apiCall(`/api/flights?origin=${origin}&destination=${destination}`);
        displayFlights(flights, classType);
    } catch (error) {
        showError('Failed to load flights');
    }
}

function displayFlights(flights, classType) {
    const container = document.getElementById('flightsList');
    const countBadge = document.getElementById('flightCount');
    
    countBadge.textContent = `${flights.length} flight${flights.length !== 1 ? 's' : ''}`;
    
    if (flights.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-plane-slash"></i>
                <p>No flights available for this route</p>
            </div>
        `;
        return;
    }
    
    const classMultiplier = { 'Economy': 1, 'Business': 2, 'First': 3 }[classType];
    
    container.innerHTML = flights.map(flight => {
        const price = Math.round(flight.base_price * classMultiplier);
        return `
            <div class="flight-card" onclick="selectFlight('${flight.flight_number}', '${flight.origin}', '${flight.destination}')">
                <div class="flight-number">${flight.flight_number}</div>
                <div class="flight-route">
                    ${flight.origin} <i class="fas fa-arrow-right"></i> ${flight.destination}
                </div>
                <div class="flight-details">
                    <div>
                        <div class="flight-time">${flight.departure_time} - ${flight.arrival_time}</div>
                        <div class="flight-seats">${flight.available_seats} seats | ${flight.aircraft}</div>
                    </div>
                    <div class="flight-price">₹${price.toLocaleString()}</div>
                </div>
            </div>
        `;
    }).join('');
}

function selectFlight(flightNumber, origin, destination) {
    // Visual selection
    document.querySelectorAll('.flight-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Store data
    currentBookingData = {
        flightNumber,
        origin,
        destination
    };
    
    // Show success and switch to booking tab
    showSuccess('Flight Selected!', `You selected ${flightNumber}`, `Route: ${origin} → ${destination}<br>Proceed to Book Ticket tab to complete your booking.`);
    
    // Switch to booking tab after delay
    setTimeout(() => {
        switchTab('booking');
        document.getElementById('bookingFlight').value = flightNumber;
        closeSuccessModal();
    }, 2000);
}

// Calculate Cost
async function loadCostFlights() {
    const select = document.getElementById('costFlight');
    try {
        const flights = await apiCall('/api/flights/all');
        select.innerHTML = '<option value="">Select a flight</option>' + 
            flights.map(f => `<option value="${f}">${f}</option>`).join('');
    } catch (error) {
        console.error('Failed to load flights');
    }
}

async function handleCalculateCost(e) {
    e.preventDefault();
    
    const flightNumber = document.getElementById('costFlight').value;
    const passengers = document.getElementById('numPassengers').value;
    const classType = document.getElementById('costClass').value;
    const tripType = document.querySelector('input[name="costTripType"]:checked').value;
    
    if (!flightNumber) {
        showError('Please select a flight!');
        return;
    }
    
    try {
        const result = await apiCall('/api/cost/calculate', 'POST', {
            flight_number: flightNumber,
            passengers: parseInt(passengers),
            class_type: classType,
            trip_type: tripType
        });
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        document.getElementById('baseFare').textContent = `₹${result.base_fare.toLocaleString()}`;
        document.getElementById('taxAmount').textContent = `₹${result.tax.toLocaleString()}`;
        document.getElementById('classMult').textContent = `${result.class_multiplier}x`;
        document.getElementById('discountAmount').textContent = `-₹${result.discount.toLocaleString()}`;
        document.getElementById('totalCost').textContent = `₹${result.total.toLocaleString()}`;
    } catch (error) {
        showError('Failed to calculate cost');
    }
}

// Book Ticket
async function loadBookingFlights() {
    const select = document.getElementById('bookingFlight');
    try {
        const flights = await apiCall('/api/flights');
        select.innerHTML = flights.map(f => 
            `<option value="${f.flight_number}">${f.flight_number} - ${f.origin} to ${f.destination}</option>`
        ).join('');
    } catch (error) {
        console.error('Failed to load flights');
    }
}

async function handleBookTicket(e) {
    e.preventDefault();
    
    // Check if user is logged in
    if (!currentUser) {
        showLoginModal();
        showError('Please login to book tickets!');
        return;
    }
    
    const data = {
        flight_number: document.getElementById('bookingFlight').value,
        passenger_name: document.getElementById('passengerName').value.trim(),
        passenger_email: document.getElementById('passengerEmail').value.trim(),
        passenger_phone: document.getElementById('passengerPhone').value.trim(),
        class_type: document.getElementById('bookingClass').value,
        payment_method: document.getElementById('paymentMethod').value,
        card_number: document.getElementById('cardNumber').value.trim(),
        cvv: document.getElementById('cvv').value.trim()
    };
    
    // Validation
    if (!data.flight_number || !data.passenger_name || !data.passenger_email || 
        !data.passenger_phone || !data.payment_method || !data.card_number || !data.cvv) {
        showError('Please fill all fields!');
        return;
    }
    
    if (data.card_number.length < 12) {
        showError('Invalid card number!');
        return;
    }
    
    if (data.cvv.length < 2) {
        showError('Invalid CVV!');
        return;
    }
    
    if (!data.passenger_email.includes('@') || !data.passenger_email.includes('.')) {
        showError('Invalid email address!');
        return;
    }
    
    try {
        const result = await apiCall('/api/book', 'POST', data);
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        // Update preview
        document.getElementById('previewPnr').textContent = result.pnr;
        document.getElementById('previewName').textContent = result.passenger_name;
        document.getElementById('previewFlight').textContent = result.flight_number;
        document.getElementById('previewRoute').textContent = `${result.origin} → ${result.destination}`;
        document.getElementById('previewClass').textContent = result.class_type;
        document.getElementById('previewTotal').textContent = `₹${result.total_cost.toLocaleString()}`;
        document.getElementById('previewStatus').textContent = 'Confirmed';
        document.getElementById('previewStatus').classList.add('confirmed');
        
        // Store booking data
        currentBookingData = result;
        
        // Clear form
        document.getElementById('bookingForm').reset();
        
        showSuccess('Booking Confirmed!', 
            `Your ticket has been booked successfully!`, 
            `<strong>PNR:</strong> ${result.pnr}<br><strong>User ID:</strong> ${result.user_id}<br><strong>Flight:</strong> ${result.flight_number}<br><strong>Route:</strong> ${result.origin} → ${result.destination}<br><strong>Class:</strong> ${result.class_type}<br><strong>Total:</strong> ₹${result.total_cost.toLocaleString()}<br><br>Proceed to Seat Allocation tab to select your seat.`);
        
        setTimeout(() => {
            switchTab('seat');
            document.getElementById('seatPnr').value = result.pnr;
            retrieveBooking();
            closeSuccessModal();
        }, 3000);
        
    } catch (error) {
        showError('Failed to book ticket');
    }
}

// Seat Allocation
function generateSeatGrid() {
    const grid = document.getElementById('seatGrid');
    const rows = ['A', 'B', 'C', 'D', 'E', 'F'];
    const cols = 20;
    
    grid.innerHTML = rows.map(row => {
        let html = `<div class="seat-row"><span class="seat-row-label">${row}</span>`;
        for (let col = 1; col <= cols; col++) {
            const seatNum = `${row}${col}`;
            html += `<button class="seat available" data-seat="${seatNum}" onclick="selectSeat('${seatNum}')">${seatNum}</button>`;
        }
        html += `<span class="seat-row-label">${row}</span></div>`;
        return html;
    }).join('');
}

async function loadOccupiedSeats() {
    try {
        occupiedSeats = await apiCall('/api/seats/occupied');
        updateSeatDisplay();
    } catch (error) {
        console.error('Failed to load occupied seats');
    }
}

function updateSeatDisplay() {
    document.querySelectorAll('.seat').forEach(seat => {
        const seatNum = seat.dataset.seat;
        if (occupiedSeats.includes(seatNum)) {
            seat.classList.remove('available');
            seat.classList.add('occupied');
            seat.disabled = true;
        }
    });
}

function selectSeat(seatNum) {
    // Deselect previous
    if (selectedSeat) {
        const prevSeat = document.querySelector(`.seat[data-seat="${selectedSeat}"]`);
        if (prevSeat) {
            prevSeat.classList.remove('selected');
            prevSeat.classList.add('available');
        }
    }
    
    // Select new
    const seat = document.querySelector(`.seat[data-seat="${seatNum}"]`);
    seat.classList.remove('available');
    seat.classList.add('selected');
    
    selectedSeat = seatNum;
    document.getElementById('selectedSeatDisplay').textContent = `Selected: ${seatNum}`;
    
    document.getElementById('generateBoardingBtn').disabled = false;
}

async function retrieveBooking() {
    const pnr = document.getElementById('seatPnr').value.trim();
    
    if (!pnr) {
        showError('Please enter a PNR!');
        return;
    }
    
    console.log('Retrieving booking for PNR:', pnr);
    
    try {
        const response = await fetch('/api/booking/retrieve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pnr })
        });
        
        const result = await response.json();
        console.log('Booking response:', result);
        
        if (!response.ok || result.error) {
            showError(result.error || 'Failed to retrieve booking');
            return;
        }
        
        currentBookingData = result;
        
        document.getElementById('seatBookingInfo').innerHTML = `
            <i class="fas fa-check-circle"></i>
            <div>
                <strong>${result.passenger_name}</strong><br>
                Flight: ${result.flight_number}<br>
                ${result.origin} → ${result.destination}<br>
                Class: ${result.class_type}<br>
                Seat: ${result.seat_number || 'Not assigned'}
            </div>
        `;
        
        if (result.seat_number) {
            selectedSeat = result.seat_number;
            document.getElementById('selectedSeatDisplay').textContent = `Seat: ${result.seat_number}`;
        }
        
    } catch (error) {
        showError('Failed to retrieve booking');
    }
}

async function retrieveByUserId() {
    const userId = document.getElementById('seatUserId').value.trim();
    
    if (!userId) {
        showError('Please enter a User ID!');
        return;
    }
    
    try {
        const result = await apiCall('/api/booking/retrieve', 'POST', { user_id: userId });
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        currentBookingData = result;
        document.getElementById('seatPnr').value = result.pnr;
        
        document.getElementById('seatBookingInfo').innerHTML = `
            <i class="fas fa-check-circle"></i>
            <div>
                <strong>${result.passenger_name}</strong><br>
                Flight: ${result.flight_number}<br>
                ${result.origin} → ${result.destination}<br>
                Class: ${result.class_type}<br>
                Seat: ${result.seat_number || 'Not assigned'}
            </div>
        `;
        
        if (result.seat_number) {
            selectedSeat = result.seat_number;
            document.getElementById('selectedSeatDisplay').textContent = `Seat: ${result.seat_number}`;
        }
        
    } catch (error) {
        showError('Failed to retrieve booking');
    }
}

async function generateBoardingPass() {
    if (!currentBookingData) {
        showError('Please retrieve a booking first!');
        return;
    }
    
    if (!selectedSeat) {
        showError('Please select a seat first!');
        return;
    }
    
    try {
        const result = await apiCall('/api/boarding-pass', 'POST', {
            pnr: currentBookingData.pnr,
            seat_number: selectedSeat
        });
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        // Show boarding pass
        document.getElementById('bpPnr').textContent = result.pnr;
        document.getElementById('bpName').textContent = result.passenger_name;
        document.getElementById('bpFlight').textContent = result.flight_number;
        document.getElementById('bpDate').textContent = result.date;
        document.getElementById('bpFrom').textContent = result.origin;
        document.getElementById('bpTo').textContent = result.destination;
        document.getElementById('bpSeat').textContent = result.seat_number;
        document.getElementById('bpGate').textContent = result.gate;
        document.getElementById('bpClass').textContent = result.class_type;
        document.getElementById('bpAircraft').textContent = result.aircraft;
        document.getElementById('bpTime').textContent = result.time;
        
        showModal('boardingPassModal');
        
    } catch (error) {
        showError('Failed to generate boarding pass');
    }
}

// Cancellation
async function checkBooking() {
    const pnr = document.getElementById('cancelPnr').value.trim();
    
    if (!pnr) {
        showError('Please enter a PNR!');
        return;
    }
    
    try {
        const result = await apiCall('/api/cancel/check', 'POST', { pnr });
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        document.getElementById('cancelBookingInfo').innerHTML = `
            <i class="fas fa-check-circle"></i>
            <div>
                <strong>${result.passenger_name}</strong><br>
                Flight: ${result.flight_number}<br>
                ${result.origin} → ${result.destination}<br>
                Class: ${result.class_type}<br>
                Total: ₹${result.total_cost.toLocaleString()}
            </div>
        `;
        
        document.getElementById('refundAmount').textContent = `₹${result.refund_amount.toLocaleString()} (${result.refund_percent}%)`;
        document.getElementById('cancelBookingBtn').disabled = false;
        document.getElementById('cancelBookingBtn').dataset.pnr = pnr;
        
    } catch (error) {
        showError('Failed to check booking');
    }
}

async function cancelBooking() {
    const pnr = document.getElementById('cancelPnr').value.trim();
    
    if (!pnr) {
        showError('Please enter a PNR!');
        return;
    }
    
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    try {
        const result = await apiCall('/api/cancel/confirm', 'POST', { pnr });
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        showSuccess('Booking Cancelled', result.message, 
            `<strong>PNR:</strong> ${pnr}<br><strong>Refund Reference:</strong> ${result.refund_reference}`);
        
        // Reset form
        document.getElementById('cancelPnr').value = '';
        document.getElementById('cancelBookingInfo').innerHTML = '<i class="fas fa-info-circle"></i><span>Enter PNR to view booking details</span>';
        document.getElementById('refundAmount').textContent = '₹0';
        document.getElementById('cancelBookingBtn').disabled = true;
        
    } catch (error) {
        showError('Failed to cancel booking');
    }
}

// Load Flight Dropdown for Search
async function loadFlightDropdown() {
    try {
        const flights = await apiCall('/api/flights/all');
        
        // Load cost flights
        const costSelect = document.getElementById('costFlight');
        if (costSelect) {
            costSelect.innerHTML = '<option value="">Select a flight</option>' + 
                flights.map(f => `<option value="${f}">${f}</option>`).join('');
        }
        
    } catch (error) {
        console.error('Failed to load flights');
    }
}

// Tab Switching Helper
function switchTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.tab === tabName) {
            item.classList.add('active');
        }
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}

// Modal Functions
function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('show');
    });
}

function closeSuccessModal() {
    document.getElementById('successModal').classList.remove('show');
}

function closeErrorModal() {
    document.getElementById('errorModal').classList.remove('show');
}

function showSuccess(title, message, details = '') {
    document.getElementById('successTitle').textContent = title;
    document.getElementById('successMessage').textContent = message;
    document.getElementById('successDetails').innerHTML = details;
    showModal('successModal');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    showModal('errorModal');
}

// Close modals on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Format card number input
document.getElementById('cardNumber')?.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
    let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = formatted.slice(0, 19);
});