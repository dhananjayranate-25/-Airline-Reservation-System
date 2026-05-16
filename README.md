# Airline-Reservation-System

A complete airline reservation system built with Python Flask, SQLite, and modern web technologies. Features both a web interface and a legacy Tkinter desktop GUI.

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Flight Search** | Search flights by origin, destination, date, and class |
| 💺 **Seat Selection** | Interactive seat map with real-time availability |
| 📋 **Booking Management** | Book, view, and cancel reservations |
| 🔎 **PNR Lookup** | Retrieve bookings using PNR number |
| 🛡️ **Admin Panel** | Manage flights, view all bookings, cancel/confirm reservations |
| 🔐 **Authentication** | Admin login with session management |
| 🎨 **Responsive UI** | Modern dark theme with animations (Font Awesome, Google Fonts) |
| 🏙️ **20 Indian Cities** | Flights across major Indian metro and tier-2 cities |
| 🖥️ **Desktop GUI** | Legacy Tkinter-based desktop application |

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, Flask, SQLite |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Desktop** | Python, Tkinter |
| **Styling** | Font Awesome, Google Fonts (Outfit, Playfair Display) |

## Project Structure

<img width="696" height="501" alt="image" src="https://github.com/user-attachments/assets/b347b0e2-9554-497e-b7d5-853bc0d03754" />

## Installation

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package manager, comes with Python)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/skybook-airline-reservation.git
   cd skybook-airline-reservation
   ```

2. **Install dependencies**
   ```bash
   pip install flask
   ```

3. **Run the application**
   ```bash
   python server.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

> 💡 The database (`airline_reservation.db`) is included. Flights are auto-populated on first run.

## Usage

### Web Interface

1. **Browse Flights** – Search and filter available flights by origin, destination, and date
2. **Select Seats** – Choose seats from an interactive seat map
3. **Book Ticket** – Enter passenger details and confirm booking
4. **My Bookings** – View bookings using PNR number or email
5. **Cancel Booking** – Cancel a reservation
6. **Admin Login** – Access admin dashboard at `/admin`

### Desktop GUI (Tkinter)

```bash
python airline_reservation.py
```
## Admin Access

- Navigate to **`http://127.0.0.1:5000/admin`**
- Login credentials are stored in the `admin` table in the database

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page |
| `GET` | `/admin` | Admin dashboard |
| `GET` | `/api/cities` | List all cities |
| `POST` | `/api/populate-flights` | Auto-populate flights |
| `POST` | `/api/search-flights` | Search available flights |
| `POST` | `/api/book` | Book a flight |
| `POST` | `/api/cancel-booking` | Cancel a booking |
| `GET` | `/api/booking/<pnr>` | Get booking by PNR |
| `GET` | `/api/seats/<flight_id>` | Get occupied seats for a flight |
| `POST` | `/api/admin/login` | Admin login |

---

## Database Schema

### flights

| Column | Type | Description |
|--------|------|-------------|
| `flight_id` | INTEGER (PK) | Auto-increment ID |
| `flight_number` | TEXT | Flight number (e.g., SKY101) |
| `origin` | TEXT | Departure city |
| `destination` | TEXT | Arrival city |
| `departure_time` | TEXT | Departure time |
| `arrival_time` | TEXT | Arrival time |
| `duration` | TEXT | Flight duration |
| `base_price` | REAL | Base ticket price |
| `available_seats` | INTEGER | Available seat count |
| `aircraft` | TEXT | Aircraft type |

### bookings

| Column | Type | Description |
|--------|------|-------------|
| `pnr` | TEXT (PK) | Unique PNR number |
| `user_id` | TEXT | User identifier |
| `flight_id` | INTEGER | Associated flight |
| `passenger_name` | TEXT | Passenger full name |
| `passenger_email` | TEXT | Passenger email |
| `passenger_phone` | TEXT | Passenger phone |
| `seat_number` | TEXT | Selected seat |
| `class_type` | TEXT | Travel class |
| `status` | TEXT | Booking status |
| `booking_date` | TEXT | Date of booking |
| `total_amount` | REAL | Total fare |

### admin

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Admin ID |
| `username` | TEXT | Admin username |
| `password` | TEXT | Admin password |


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

