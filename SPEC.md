# Airline Reservation System - Specification

## 1. Project Overview
- **Project Name**: SkyBook - Airline Reservation System
- **Type**: Desktop GUI Application with SQLite Database
- **Core Functionality**: Complete airline seat reservation, booking management, and cancellations
- **Target Users**: Airline customers and travel agents

## 2. UI/UX Specification

### Layout Structure
- **Header**: Logo, System Title, Navigation Tabs
- **Main Content**: Dynamic panels based on selected function
- **Sidebar**: Quick actions and booking summary
- **Footer**: Status bar with database connection status

### Visual Design
- **Color Scheme**:
  - Primary: #1E3A5F (Deep Navy Blue)
  - Secondary: #3498DB (Sky Blue)
  - Accent: #E74C3C (Coral Red)
  - Background: #ECF0F1 (Light Gray)
  - Success: #27AE60 (Green)
  - Text: #2C3E50 (Dark Gray)
- **Typography**: 
  - Headers: Segoe UI Bold, 18-24px
  - Body: Segoe UI, 12-14px
- **Spacing**: 10px padding, 15px margins
- **Effects**: Rounded corners (8px), subtle shadows on cards

### Components
- Navigation tabs with hover effects
- Form inputs with validation feedback
- Seat map visual (grid of available/selected/booked seats)
- Data tables with alternating row colors
- Modal dialogs for confirmations
- Toast notifications for actions

## 3. Functionality Specification

### B. Retrieve and Display
- **B1: Take Trip**
  - Origin city selection (dropdown)
  - Destination city selection (dropdown)
  - Date picker for travel
  - Class selection (Economy/Business/First)
  - One-way or Round-trip toggle
- **B2: Display Available Flights**
  - List available flights matching criteria
  - Flight number, airline, departure time, duration, price
  - Seat availability indicator

### C. Total Cost Calculation
- **C1: Display Total Cost**
  - Base fare calculation
  - Tax calculation (10%)
  - Class multiplier (Economy: 1x, Business: 2x, First: 3x)
  - Number of passengers
  - Discount for round-trip (5% off)
  - Total with breakdown

### D. Ticket Generation
- **D1: Take User Details and Payment**
  - Passenger name, email, phone
  - Payment method selection
  - Credit card details (simulated)
  - Booking confirmation
- **D2: Generate Tickets and User ID**
  - Unique PNR (Passenger Name Record)
  - Generate 6-character User ID
  - Ticket details with QR code representation
  - Email confirmation (simulated)

### E. Seat Allocation
- **E1: Generate Boarding Pass**
  - Boarding pass with seat number
  -Gate number assignment
  - Boarding time
  - Flight details summary
- **E2: Take User ID**
  - Input PNR/User ID to retrieve booking
  - View booking details
  - Select/change seat

### F. Cancellation
- **F1: Acknowledgement**
  - Enter PNR for cancellation
  - Cancellation confirmation dialog
  - Refund calculation (80% refund for cancellations >24hrs, 50% otherwise)
  - Cancel confirmation with reference number

## 4. Database Schema

### Tables
- **flights**: flight_id, flight_number, origin, destination, departure_time, arrival_time, price, available_seats
- **bookings**: pnr, user_id, flight_id, passenger_name, passenger_email, passenger_phone, seat_number, class, booking_date, total_cost, status
- **passengers**: user_id, name, email, phone, created_at

## 5. Acceptance Criteria
- [ ] All navigation tabs work correctly
- [ ] Flight search returns filtered results
- [ ] Total cost calculates correctly with all factors
- [ ] Booking creates new record in database
- [ ] Seat selection shows visual representation
- [ ] Boarding pass generates with all details
- [ ] Cancellation processes correctly with refund
- [ ] Database persists all data between sessions
- [ ] UI is responsive and visually appealing