from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import random
import string
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'skybook_secret_key_2024'

def get_db():
    conn = sqlite3.connect('airline_reservation.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    return dict(row) if row else None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    return render_template('admin.html')

@app.route('/api/cities')
def get_cities():
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Chandigarh", "Goa", "Kochi", "Coimbatore", "Nagpur",
        "Indore", "Bhopal", "Patna", "Ranchi", "Srinagar"
    ]
    return jsonify(cities)

@app.route('/api/populate-flights', methods=['POST'])
def populate_flights():
    cities = [
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
        "Chandigarh", "Goa", "Kochi", "Coimbatore", "Nagpur",
        "Indore", "Bhopal", "Patna", "Ranchi", "Srinagar"
    ]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Clear existing flights
    cursor.execute("DELETE FROM flights")
    
    # Create routes between all major cities with realistic prices
    aircrafts = ["Boeing 737", "Airbus A320", "Boeing 787", "Airbus A321", "ATR 72"]
    flight_num = 1000
    
    for i, origin in enumerate(cities):
        for j, dest in enumerate(cities):
            if origin != dest:
                # Calculate distance-based price (rough estimate)
                price = 2500 + (abs(i-j) * 400) + random.randint(-500, 500)
                price = max(2000, min(8000, price)) # Clamp between 2000-8000
                
                # Multiple flights per route
                for time_idx, departure in enumerate(["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]):
                    flight_num += 1
                    
                    # Calculate duration based on city pair (rough estimate)
                    hour_diff = abs(i - j) * 0.5
                    hr = int(hour_diff + 1)
                    min_part = int((hour_diff % 1) * 60)
                    duration = f"{hr}h {min_part}m"
                    
                    # Calculate arrival
                    dep_h, dep_m = map(int, departure.split(':'))
                    arr_h = (dep_h + hr) % 24
                    arr_m = dep_m + min_part
                    if arr_m >= 60:
                        arr_h = (arr_h + 1) % 24
                        arr_m = arr_m % 60
                    arrival = f"{arr_h:02d}:{arr_m:02d}"
                    
                    seats = random.randint(80, 180)
                    aircraft = random.choice(aircrafts)
                    
                    cursor.execute('''INSERT INTO flights 
                        (flight_number, origin, destination, departure_time, arrival_time, duration, base_price, available_seats, aircraft)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (f"SK{flight_num}", origin, dest, departure, arrival, duration, price, seats, aircraft))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Added flights for 20 cities'})

@app.route('/app')
def index():
    tab = request.args.get('tab', 'search')
    user_logged_in = 'user_id' in session
    user_data = session.get('user_data', {})
    return render_template('index.html', active_tab=tab, user_logged_in=user_logged_in, user_data=user_data)

@app.route('/api/flights')
def get_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if origin and destination:
        cursor.execute("SELECT * FROM flights WHERE origin = ? AND destination = ?", (origin, destination))
    else:
        cursor.execute("SELECT * FROM flights")
    
    flights = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(flights)

@app.route('/api/flights/all')
def get_all_flights():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT flight_number FROM flights")
    flights = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(flights)

@app.route('/api/cost/calculate', methods=['POST'])
def calculate_cost():
    data = request.json
    flight_num = data.get('flight_number')
    passengers = int(data.get('passengers', 1))
    class_type = data.get('class_type', 'Economy')
    trip_type = data.get('trip_type', 'one_way')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT base_price FROM flights WHERE flight_number = ?", (flight_num,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Flight not found'}), 404
    
    base_price = result[0]
    class_multiplier = {'Economy': 1, 'Business': 2, 'First': 3}.get(class_type, 1)
    
    base_fare = base_price * class_multiplier * passengers
    tax = base_fare * 0.10
    discount = 0
    
    if trip_type == 'round_trip':
        discount = (base_fare + tax) * 0.05
    
    total = base_fare + tax - discount
    
    return jsonify({
        'base_fare': int(base_fare),
        'tax': int(tax),
        'discount': int(discount),
        'total': int(total),
        'class_multiplier': class_multiplier
    })

@app.route('/api/book', methods=['POST'])
def book_ticket():
    data = request.json
    
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to book tickets'}), 401
    
    user_id = session.get('user_id')
    user_data = session.get('user_data', {})
    
    flight_number = data.get('flight_number')
    passenger_name = data.get('passenger_name') or user_data.get('name', '')
    passenger_email = data.get('passenger_email') or user_data.get('email', '')
    passenger_phone = data.get('passenger_phone') or user_data.get('phone', '')
    class_type = data.get('class_type', 'Economy')
    payment_method = data.get('payment_method')
    card_number = data.get('card_number')
    cvv = data.get('cvv')
    
    if not all([flight_number, passenger_name, passenger_email, passenger_phone, payment_method, card_number, cvv]):
        return jsonify({'error': 'Please fill all fields'}), 400
    
    if len(card_number) < 12:
        return jsonify({'error': 'Invalid card number'}), 400
    
    if '@' not in passenger_email or '.' not in passenger_email:
        return jsonify({'error': 'Invalid email address'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_number,))
    flight = cursor.fetchone()
    
    if not flight:
        conn.close()
        return jsonify({'error': 'Flight not found'}), 404
    
    class_multiplier = {'Economy': 1, 'Business': 2, 'First': 3}.get(class_type, 1)
    base_price = flight['base_price']
    base_fare = base_price * class_multiplier
    tax = base_fare * 0.10
    total_cost = base_fare + tax
    
    pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    try:
        cursor.execute('''INSERT INTO bookings 
            (pnr, user_id, flight_id, passenger_name, passenger_email, passenger_phone, 
             seat_number, class_type, trip_type, booking_date, total_cost, status, gate_number, boarding_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (pnr, user_id, flight['flight_id'], passenger_name, passenger_email, passenger_phone,
             None, class_type, 'one_way', datetime.now().strftime('%Y-%m-%d %H:%M'), total_cost, 'Confirmed',
             f'Gate {random.randint(1, 20)}', flight['departure_time']))
        
        # Only insert into passengers if not exists
        cursor.execute("SELECT user_id FROM passengers WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute('''INSERT OR IGNORE INTO passengers (user_id, name, email, phone, created_at)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, passenger_name, passenger_email, passenger_phone, datetime.now().strftime('%Y-%m-%d %H:%M')))
        
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    conn.close()
    
    return jsonify({
        'pnr': pnr,
        'user_id': user_id,
        'flight_number': flight_number,
        'origin': flight['origin'],
        'destination': flight['destination'],
        'departure_time': flight['departure_time'],
        'arrival_time': flight['arrival_time'],
        'class_type': class_type,
        'total_cost': int(total_cost),
        'passenger_name': passenger_name
    })

@app.route('/api/booking/retrieve', methods=['POST'])
def retrieve_booking():
    data = request.json
    pnr = data.get('pnr')
    user_id = data.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if pnr:
            cursor.execute('''SELECT * FROM bookings WHERE pnr = ? AND status = 'Confirmed' ''', (pnr,))
            booking = cursor.fetchone()
            
            if not booking:
                conn.close()
                return jsonify({'error': 'No active booking found'}), 404
            
            # Get flight details separately
            cursor.execute('SELECT * FROM flights WHERE flight_id = ?', (booking['flight_id'],))
            flight = cursor.fetchone()
            conn.close()
            
            if not flight:
                return jsonify({'error': 'Flight data not found'}), 404
            
            return jsonify({
                'pnr': booking['pnr'],
                'user_id': booking['user_id'],
                'passenger_name': booking['passenger_name'],
                'passenger_email': booking['passenger_email'],
                'passenger_phone': booking['passenger_phone'],
                'flight_number': flight['flight_number'],
                'origin': flight['origin'],
                'destination': flight['destination'],
                'departure_time': flight['departure_time'],
                'arrival_time': flight['arrival_time'],
                'class_type': booking['class_type'],
                'seat_number': booking['seat_number'],
                'booking_date': booking['booking_date'],
                'total_cost': booking['total_cost'],
                'gate_number': booking['gate_number'] if booking['gate_number'] else 'TBD',
                'aircraft': flight['aircraft'] if flight['aircraft'] else 'TBD'
            })
            
        elif user_id:
            cursor.execute('''SELECT * FROM bookings WHERE user_id = ? AND status = 'Confirmed' 
                ORDER BY booking_date DESC LIMIT 1''', (user_id,))
            booking = cursor.fetchone()
            
            if not booking:
                conn.close()
                return jsonify({'error': 'No active booking found'}), 404
            
            cursor.execute('SELECT * FROM flights WHERE flight_id = ?', (booking['flight_id'],))
            flight = cursor.fetchone()
            conn.close()
            
            if not flight:
                return jsonify({'error': 'Flight data not found'}), 404
            
            return jsonify({
                'pnr': booking['pnr'],
                'user_id': booking['user_id'],
                'passenger_name': booking['passenger_name'],
                'passenger_email': booking['passenger_email'],
                'passenger_phone': booking['passenger_phone'],
                'flight_number': flight['flight_number'],
                'origin': flight['origin'],
                'destination': flight['destination'],
                'departure_time': flight['departure_time'],
                'arrival_time': flight['arrival_time'],
                'class_type': booking['class_type'],
                'seat_number': booking['seat_number'],
                'booking_date': booking['booking_date'],
                'total_cost': booking['total_cost'],
                'gate_number': booking['gate_number'] if booking['gate_number'] else 'TBD',
                'aircraft': flight['aircraft'] if flight['aircraft'] else 'TBD'
            })
        else:
            conn.close()
            return jsonify({'error': 'Please provide PNR or User ID'}), 400
            
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/boarding-pass', methods=['POST'])
def generate_boarding_pass():
    data = request.json
    pnr = data.get('pnr')
    seat_number = data.get('seat_number')
    
    if not pnr or not seat_number:
        return jsonify({'error': 'PNR and seat number required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''UPDATE bookings SET seat_number = ? WHERE pnr = ?''', (seat_number, pnr))
    conn.commit()
    
    cursor.execute('''SELECT b.*, f.flight_number, f.origin, f.destination, 
        f.departure_time, f.arrival_time, f.aircraft FROM bookings b 
        JOIN flights f ON b.flight_id = f.flight_id WHERE b.pnr = ?''', (pnr,))
    
    booking = cursor.fetchone()
    conn.close()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    return jsonify({
        'pnr': booking['pnr'],
        'user_id': booking['user_id'],
        'passenger_name': booking['passenger_name'],
        'flight_number': booking['flight_number'],
        'origin': booking['origin'],
        'destination': booking['destination'],
        'date': booking['booking_date'][:10],
        'time': booking['departure_time'],
        'seat_number': seat_number,
        'gate': booking['gate_number'] if booking['gate_number'] else 'TBD',
        'class_type': booking['class_type'],
        'aircraft': booking['aircraft'] if booking['aircraft'] else 'TBD'
    })

@app.route('/api/cancel/check', methods=['POST'])
def check_booking():
    data = request.json
    pnr = data.get('pnr')
    
    if not pnr:
        return jsonify({'error': 'Please enter PNR'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM bookings WHERE pnr = ? AND status = "Confirmed"', (pnr,))
        booking = cursor.fetchone()
        
        if not booking:
            conn.close()
            return jsonify({'error': 'No active booking found'}), 404
        
        cursor.execute('SELECT flight_number, origin, destination, departure_time FROM flights WHERE flight_id = ?', (booking['flight_id'],))
        flight = cursor.fetchone()
        conn.close()
        
        if not flight:
            return jsonify({'error': 'Flight data not found'}), 404
        
        refund_amount = int(booking['total_cost'] * 0.80)
        
        return jsonify({
            'passenger_name': booking['passenger_name'],
            'flight_number': flight[0],
            'origin': flight[1],
            'destination': flight[2],
            'class_type': booking['class_type'],
            'total_cost': booking['total_cost'],
            'refund_amount': refund_amount,
            'refund_percent': 80
        })
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cancel/confirm', methods=['POST'])
def cancel_booking():
    data = request.json
    pnr = data.get('pnr')
    
    if not pnr:
        return jsonify({'error': 'Please enter PNR'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''UPDATE bookings SET status = 'Cancelled' WHERE pnr = ?''', (pnr,))
    conn.commit()
    conn.close()
    
    refund_ref = f'REF{random.randint(100000, 999999)}'
    
    return jsonify({
        'success': True,
        'refund_reference': refund_ref,
        'message': 'Your booking has been cancelled. Refund will be processed within 5-7 days.'
    })

@app.route('/api/seats/occupied')
def get_occupied_seats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT seat_number FROM bookings WHERE seat_number IS NOT NULL AND status = 'Confirmed'")
    seats = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return jsonify(seats)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    # Check if admin registration
    is_admin = email and email.lower() == 'admin@skybook.com'
    
    if not all([name, email, phone, password]):
        return jsonify({'error': 'Please fill all fields'}), 400
    
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email address'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM passengers WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400
    
    # Generate unique user_id
    while True:
        if is_admin:
            user_id = 'ADMIN'
        else:
            user_id = 'SK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        cursor.execute("SELECT user_id FROM passengers WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            break
    
    try:
        cursor.execute('''INSERT INTO passengers (user_id, name, email, phone, created_at)
            VALUES (?, ?, ?, ?, ?)''',
            (user_id, name, email, phone, datetime.now().strftime('%Y-%m-%d %H:%M')))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Registration failed'}), 500
    
    session['user_id'] = user_id
    session['user_data'] = {
        'name': name,
        'email': email,
        'phone': phone,
        'user_id': user_id,
        'is_admin': is_admin
    }
    session['is_admin'] = is_admin
    
    conn.close()
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'name': name,
        'email': email,
        'phone': phone,
        'is_admin': is_admin
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Please enter email and password'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM passengers WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found. Please register first.'}), 404
    
    is_admin = user['email'].lower() == 'admin@skybook.com'
    
    session['user_id'] = user['user_id']
    session['is_admin'] = is_admin
    session['user_data'] = {
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'user_id': user['user_id'],
        'is_admin': is_admin
    }
    
    return jsonify({
        'success': True,
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'is_admin': is_admin
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': session.get('user_data', {}),
            'is_admin': session.get('is_admin', False)
        })
    return jsonify({'logged_in': False, 'user': None, 'is_admin': False})

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, phone, created_at FROM passengers ORDER BY created_at DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM passengers")
    user_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status != 'Cancelled'")
    booking_count = cursor.fetchone()['count']
    conn.close()
    return jsonify({'users': user_count, 'bookings': booking_count})

@app.route('/api/auth/delete-account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Cancel all bookings first
        cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE user_id = ?", (user_id,))
        
        # Delete passenger
        cursor.execute("DELETE FROM passengers WHERE user_id = ?", (user_id,))
        
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500
    
    conn.close()
    session.clear()
    
    return jsonify({'success': True, 'message': 'Account deleted successfully'})

if __name__ == '__main__':
    # Auto-populate flights for 20 cities on first run
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM flights")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count < 100:
            print("Populating flights for 20 cities...")
            with app.test_client() as client:
                client.post('/api/populate-flights')
            print(f"Done! Added flights for 20 cities")
    except Exception as e:
        print(f"Error populating flights: {e}")
    
    app.run(debug=True, port=5000)