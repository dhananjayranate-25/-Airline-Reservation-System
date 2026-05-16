import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime, timedelta
import random
import string

class AirlineReservationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("SkyBook - Airline Reservation System")
        self.root.geometry("1280x800")
        self.root.configure(bg="#1a1a2e")
        
        self.current_user_id = None
        self.current_pnr = None
        self.selected_seat = None
        self.current_booking_data = {}
        self.occupied_seats = set()
        
        self.init_database()
        self.create_ui()
        self.load_occupied_seats()
    
    def init_database(self):
        self.conn = sqlite3.connect("airline_reservation.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            duration TEXT NOT NULL,
            base_price REAL NOT NULL,
            available_seats INTEGER NOT NULL,
            aircraft TEXT NOT NULL
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
            pnr TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            flight_id INTEGER NOT NULL,
            passenger_name TEXT NOT NULL,
            passenger_email TEXT NOT NULL,
            passenger_phone TEXT NOT NULL,
            seat_number TEXT,
            class_type TEXT NOT NULL,
            trip_type TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT NOT NULL,
            gate_number TEXT,
            boarding_time TEXT
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS passengers (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        
        self.cursor.execute("SELECT COUNT(*) FROM flights")
        if self.cursor.fetchone()[0] == 0:
            self.populate_sample_flights()
        
        self.conn.commit()
    
    def populate_sample_flights(self):
        flights = [
            ("SK101", "Mumbai", "Delhi", "08:00", "10:30", "2h 30m", 3500, 120, "Boeing 737"),
            ("SK102", "Mumbai", "Delhi", "14:00", "16:30", "2h 30m", 3800, 120, "Boeing 737"),
            ("SK103", "Mumbai", "Delhi", "20:00", "22:30", "2h 30m", 3200, 120, "Airbus A320"),
            ("SK201", "Delhi", "Mumbai", "09:00", "11:30", "2h 30m", 3600, 120, "Boeing 737"),
            ("SK202", "Delhi", "Mumbai", "15:00", "17:30", "2h 30m", 3900, 120, "Boeing 737"),
            ("SK301", "Mumbai", "Bangalore", "07:00", "08:45", "1h 45m", 2800, 100, "Airbus A320"),
            ("SK302", "Mumbai", "Bangalore", "12:00", "13:45", "1h 45m", 3000, 100, "Airbus A320"),
            ("SK303", "Mumbai", "Bangalore", "18:00", "19:45", "1h 45m", 2700, 100, "Boeing 737"),
            ("SK401", "Bangalore", "Mumbai", "08:00", "09:45", "1h 45m", 2900, 100, "Airbus A320"),
            ("SK402", "Bangalore", "Mumbai", "14:00", "15:45", "1h 45m", 3100, 100, "Boeing 737"),
            ("SK501", "Mumbai", "Chennai", "06:30", "08:00", "1h 30m", 2500, 90, "ATR 72"),
            ("SK502", "Mumbai", "Chennai", "11:00", "12:30", "1h 30m", 2700, 90, "ATR 72"),
            ("SK503", "Mumbai", "Chennai", "16:00", "17:30", "1h 30m", 2400, 90, "ATR 72"),
            ("SK601", "Chennai", "Mumbai", "07:00", "08:30", "1h 30m", 2600, 90, "ATR 72"),
            ("SK602", "Chennai", "Mumbai", "13:00", "14:30", "1h 30m", 2800, 90, "ATR 72"),
            ("SK701", "Delhi", "Bangalore", "10:00", "13:00", "3h 00m", 4500, 150, "Boeing 787"),
            ("SK702", "Delhi", "Bangalore", "16:00", "19:00", "3h 00m", 4800, 150, "Boeing 787"),
            ("SK801", "Bangalore", "Delhi", "11:00", "14:00", "3h 00m", 4600, 150, "Boeing 787"),
            ("SK901", "Delhi", "Chennai", "05:30", "08:15", "2h 45m", 4000, 110, "Airbus A321"),
            ("SK902", "Delhi", "Chennai", "19:00", "21:45", "2h 45m", 4200, 110, "Airbus A321"),
            ("SK1001", "Chennai", "Delhi", "06:00", "08:45", "2h 45m", 4100, 110, "Airbus A321"),
        ]
        
        for flight in flights:
            self.cursor.execute('''INSERT INTO flights 
                (flight_number, origin, destination, departure_time, arrival_time, duration, base_price, available_seats, aircraft)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', flight)
        
        self.conn.commit()
    
    def load_occupied_seats(self):
        self.cursor.execute("SELECT seat_number FROM bookings WHERE seat_number IS NOT NULL AND status = 'Confirmed'")
        for row in self.cursor.fetchall():
            if row[0]:
                self.occupied_seats.add(row[0])
    
    def create_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TNotebook", background="#16213e", tabposition="n")
        style.configure("TNotebook.Tab", background="#0f3460", foreground="white", 
                       padding=[20, 12], font=("Segoe UI", 12, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#e94560")])
        
        style.configure("TFrame", background="#16213e")
        
        self.header_frame = tk.Frame(self.root, bg="#0f3460", height=100)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        self.header_container = tk.Frame(self.header_frame, bg="#0f3460")
        self.header_container.pack(fill="x", padx=30, pady=15)
        
        self.logo_label = tk.Label(self.header_container, text="✈", font=("Segoe UI", 40), 
                            bg="#0f3460", fg="#e94560")
        self.logo_label.pack(side="left")
        
        self.title_frame = tk.Frame(self.header_container, bg="#0f3460")
        self.title_frame.pack(side="left", padx=15)
        
        self.title_label = tk.Label(self.title_frame, text="SkyBook", 
                                  font=("Segoe UI", 28, "bold"), bg="#0f3460", fg="white")
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(self.title_frame, text="Premium Airline Reservation", 
                                   font=("Segoe UI", 11), bg="#0f3460", fg="#e94560")
        self.subtitle_label.pack(anchor="w")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_search = ttk.Frame(self.notebook)
        self.tab_cost = ttk.Frame(self.notebook)
        self.tab_booking = ttk.Frame(self.notebook)
        self.tab_seat = ttk.Frame(self.notebook)
        self.tab_cancel = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_search, text="  🔍 Search Flights  ")
        self.notebook.add(self.tab_cost, text="  💰 Total Cost  ")
        self.notebook.add(self.tab_booking, text="  🎫 Book Ticket  ")
        self.notebook.add(self.tab_seat, text="  💺 Seat Allocation  ")
        self.notebook.add(self.tab_cancel, text="  ❌ Cancellation  ")
        
        self.create_search_tab()
        self.create_cost_tab()
        self.create_booking_tab()
        self.create_seat_tab()
        self.create_cancel_tab()
        
        self.footer_frame = tk.Frame(self.root, bg="#0f3460", height=35)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.footer_frame, text="✓ Database Connected", 
                                   font=("Segoe UI", 10), bg="#0f3460", fg="#00d26a")
        self.status_label.pack(side="right", padx=30, pady=5)
        
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_data())
    
    def create_search_tab(self):
        main_container = tk.Frame(self.tab_search, bg="#16213e")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        left_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        title = tk.Label(left_panel, text="Search Flights", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title.pack(pady=(0, 25), anchor="w")
        
        card = tk.Frame(left_panel, bg="#0f3460", relief="flat", bd=0)
        card.pack(fill="x", pady=10)
        
        form_inner = tk.Frame(card, bg="#0f3460", padx=25, pady=25)
        form_inner.pack(fill="x")
        
        labels = [("From", "origin"), ("To", "destination"), ("Travel Date", "date"), ("Class", "class")]
        for i, (label_text, attr) in enumerate(labels):
            tk.Label(form_inner, text=label_text, bg="#0f3460", fg="#a0a0a0", 
                    font=("Segoe UI", 11)).grid(row=i, column=0, sticky="w", pady=15, padx=(0, 15))
        
        self.origin_combo = ttk.Combobox(form_inner, values=["Mumbai", "Delhi", "Bangalore", "Chennai"], 
                                      state="readonly", width=22, font=("Segoe UI", 11))
        self.origin_combo.grid(row=0, column=1, pady=15, padx=(0, 15))
        self.origin_combo.set("Mumbai")
        
        self.destination_combo = ttk.Combobox(form_inner, values=["Delhi", "Mumbai", "Bangalore", "Chennai"], 
                                                state="readonly", width=22, font=("Segoe UI", 11))
        self.destination_combo.grid(row=1, column=1, pady=15, padx=(0, 15))
        self.destination_combo.set("Delhi")
        
        self.travel_date = ttk.Entry(form_inner, width=24, font=("Segoe UI", 11))
        self.travel_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.travel_date.grid(row=2, column=1, pady=15, padx=(0, 15))
        
        self.class_combo = ttk.Combobox(form_inner, values=["Economy", "Business", "First"], 
                                     state="readonly", width=22, font=("Segoe UI", 11))
        self.class_combo.set("Economy")
        self.class_combo.grid(row=3, column=1, pady=15, padx=(0, 15))
        
        self.trip_type_var = tk.StringVar(value="one_way")
        trip_frame = tk.Frame(form_inner, bg="#0f3460")
        trip_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky="w")
        
        rb1 = tk.Radiobutton(trip_frame, text="One Way", variable=self.trip_type_var, value="one_way", 
                          bg="#0f3460", fg="white", font=("Segoe UI", 11), selectcolor="#0f3460")
        rb1.pack(side="left", padx=15)
        rb2 = tk.Radiobutton(trip_frame, text="Round Trip", variable=self.trip_type_var, value="round_trip", 
                          bg="#0f3460", fg="white", font=("Segoe UI", 11), selectcolor="#0f3460")
        rb2.pack(side="left", padx=15)
        
        search_btn = tk.Button(form_inner, text="🔍 Search Flights", command=self.search_flights,
                          bg="#e94560", fg="white", font=("Segoe UI", 13, "bold"),
                          relief="flat", width=20, height=2, cursor="hand2")
        search_btn.grid(row=5, column=0, columnspan=2, pady=25)
        
        right_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title2 = tk.Label(right_panel, text="Available Flights", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title2.pack(pady=(0, 25), anchor="w")
        
        tree_frame = tk.Frame(right_panel, bg="#0f3460", relief="flat", bd=0)
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("Flight", "Route", "Time", "Duration", "Price", "Seats")
        self.flights_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12,
                                     style="Custom.Treeview")
        
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#0f3460", foreground="white", 
                     fieldbackground="#0f3460", rowheight=40)
        style.configure("Custom.Treeview.Heading", background="#e94560", foreground="white", 
                    font=("Segoe UI", 11, "bold"))
        
        for col in columns:
            self.flights_tree.heading(col, text=col, anchor="center")
            self.flights_tree.column(col, width=90, anchor="center")
        
        self.flights_tree.column("Route", width=160)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.flights_tree.yview)
        self.flights_tree.configure(yscrollcommand=scrollbar.set)
        
        self.flights_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.flights_tree.bind("<Double-1>", self.select_flight)
    
    def search_flights(self):
        origin = self.origin_combo.get()
        destination = self.destination_combo.get()
        
        if origin == destination:
            messagebox.showerror("Error", "Origin and destination cannot be the same!")
            return
        
        self.cursor.execute("SELECT * FROM flights WHERE origin = ? AND destination = ?", 
                        (origin, destination))
        flights = self.cursor.fetchall()
        
        for item in self.flights_tree.get_children():
            self.flights_tree.delete(item)
        
        class_type = self.class_combo.get()
        class_multiplier = {"Economy": 1, "Business": 2, "First": 3}.get(class_type, 1)
        
        for flight in flights:
            price = int(flight[7] * class_multiplier)
            self.flights_tree.insert("", "end", values=(
                flight[1],
                f"{flight[2]} ➝ {flight[3]}",
                f"{flight[4]} - {flight[5]}",
                flight[6],
                f"₹{price:,}",
                flight[8]
            ), tags=(str(flight[0]),))
        
        if not flights:
            messagebox.showinfo("No Flights", "No flights available for this route!")
    
    def select_flight(self, event):
        selection = self.flights_tree.selection()
        if selection:
            item = self.flights_tree.item(selection[0])
            flight_num = item["values"][0]
            self.current_booking_data["flight_number"] = flight_num
            messagebox.showinfo("Flight Selected", f"You selected: {flight_num}\n\nGo to 'Book Ticket' tab to complete your booking!")
            self.notebook.select(2)
    
    def create_cost_tab(self):
        main_container = tk.Frame(self.tab_cost, bg="#16213e")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        left_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        title = tk.Label(left_panel, text="Calculate Total Cost", font=("Segoe UI", 22, "bold"), 
                      bg="#1a1a2e", fg="white")
        title.pack(pady=(0, 25), anchor="w")
        
        card = tk.Frame(left_panel, bg="#0f3460", relief="flat", bd=0)
        card.pack(fill="x", pady=10)
        
        form_inner = tk.Frame(card, bg="#0f3460", padx=25, pady=25)
        form_inner.pack(fill="x")
        
        tk.Label(form_inner, text="Select Flight:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=15)
        self.cost_flight_combo = ttk.Combobox(form_inner, values=self.get_flight_numbers(), 
                                          state="readonly", width=22, font=("Segoe UI", 11))
        self.cost_flight_combo.grid(row=0, column=1, pady=15, padx=15)
        
        tk.Label(form_inner, text="Passengers:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=15)
        self.num_passengers = ttk.Spinbox(form_inner, from_=1, to=10, width=24, font=("Segoe UI", 11))
        self.num_passengers.set(1)
        self.num_passengers.grid(row=1, column=1, pady=15, padx=15)
        
        tk.Label(form_inner, text="Class:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=15)
        self.cost_class_combo = ttk.Combobox(form_inner, values=["Economy", "Business", "First"], 
                                           state="readonly", width=22, font=("Segoe UI", 11))
        self.cost_class_combo.set("Economy")
        self.cost_class_combo.grid(row=2, column=1, pady=15, padx=15)
        
        tk.Label(form_inner, text="Trip Type:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=3, column=0, sticky="w", pady=15)
        self.cost_trip_type_var = tk.StringVar(value="one_way")
        trip_frame = tk.Frame(form_inner, bg="#0f3460")
        trip_frame.grid(row=3, column=1, pady=15, padx=15, sticky="w")
        tk.Radiobutton(trip_frame, text="One Way", variable=self.cost_trip_type_var, value="one_way", 
                      bg="#0f3460", fg="white", font=("Segoe UI", 11), selectcolor="#0f3460").pack(side="left", padx=10)
        tk.Radiobutton(trip_frame, text="Round Trip", variable=self.cost_trip_type_var, value="round_trip", 
                      bg="#0f3460", fg="white", font=("Segoe UI", 11), selectcolor="#0f3460").pack(side="left", padx=10)
        
        calc_btn = tk.Button(form_inner, text="💰 Calculate Cost", command=self.calculate_cost,
                         bg="#27ae60", fg="white", font=("Segoe UI", 13, "bold"),
                         relief="flat", width=20, height=2, cursor="hand2")
        calc_btn.grid(row=4, column=0, columnspan=2, pady=25)
        
        right_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title2 = tk.Label(right_panel, text="Cost Breakdown", font=("Segoe UI", 22, "bold"), 
                       bg="#1a1a2e", fg="white")
        title2.pack(pady=(0, 25), anchor="w")
        
        cost_card = tk.Frame(right_panel, bg="#0f3460", relief="flat", bd=0)
        cost_card.pack(fill="both", expand=True)
        
        self.cost_display = tk.Frame(cost_card, bg="#0f3460", padx=30, pady=30)
        self.cost_display.pack(fill="both", expand=True)
        
        items = [
            ("Base Fare:", "₹0", "base_fare_label"),
            ("Tax (10%):", "₹0", "tax_label"),
            ("Class Multiplier:", "1x", "class_mult_label"),
            ("Discount (Round Trip):", "-₹0", "discount_label"),
        ]
        
        for label_text, default, attr_name in items:
            tk.Label(self.cost_display, text=label_text, bg="#0f3460", fg="#a0a0a0", 
                   font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 0))
            label = tk.Label(self.cost_display, text=default, bg="#0f3460", fg="white", 
                          font=("Segoe UI", 14, "bold"), anchor="e")
            label.pack(fill="x", pady=(0, 10))
            setattr(self, attr_name, label)
        
        sep = tk.Frame(self.cost_display, bg="#e94560", height=2)
        sep.pack(fill="x", pady=15)
        
        tk.Label(self.cost_display, text="TOTAL:", bg="#0f3460", fg="white", 
               font=("Segoe UI", 16, "bold")).pack(anchor="w")
        self.total_cost_label = tk.Label(self.cost_display, text="₹0", bg="#0f3460", 
                                    fg="#e94560", font=("Segoe UI", 24, "bold"), anchor="e")
        self.total_cost_label.pack(fill="x")
    
    def get_flight_numbers(self):
        self.cursor.execute("SELECT flight_number FROM flights")
        return [row[0] for row in self.cursor.fetchall()]
    
    def calculate_cost(self):
        flight_num = self.cost_flight_combo.get()
        if not flight_num:
            messagebox.showerror("Error", "Please select a flight!")
            return
        
        try:
            num_pax = int(self.num_passengers.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of passengers!")
            return
        
        class_type = self.cost_class_combo.get()
        trip_type = self.cost_trip_type_var.get()
        
        class_multiplier = {"Economy": 1, "Business": 2, "First": 3}.get(class_type, 1)
        
        self.cursor.execute("SELECT base_price FROM flights WHERE flight_number = ?", (flight_num,))
        result = self.cursor.fetchone()
        
        if not result:
            return
        
        base_price = result[0]
        base_fare = base_price * class_multiplier * num_pax
        tax = base_fare * 0.10
        discount = 0
        
        if trip_type == "round_trip":
            discount = (base_fare + tax) * 0.05
        
        total = base_fare + tax - discount
        
        self.base_fare_label.config(text=f"₹{base_fare:,}")
        self.tax_label.config(text=f"₹{int(tax):,}")
        self.class_mult_label.config(text=f"{class_multiplier}x")
        self.discount_label.config(text=f"-₹{int(discount):,}")
        self.total_cost_label.config(text=f"₹{int(total):,}")
    
    def create_booking_tab(self):
        main_container = tk.Frame(self.tab_booking, bg="#16213e")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        left_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        title = tk.Label(left_panel, text="Book Your Ticket", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title.pack(pady=(0, 25), anchor="w")
        
        card = tk.Frame(left_panel, bg="#0f3460", relief="flat", bd=0)
        card.pack(fill="both", expand=True)
        
        form_inner = tk.Frame(card, bg="#0f3460", padx=25, pady=25)
        form_inner.pack(fill="both")
        
        fields = [
            ("Select Flight:", "flight", "SK101"),
            ("Passenger Name:", "name", ""),
            ("Email:", "email", ""),
            ("Phone:", "phone", ""),
            ("Class:", "class", "Economy"),
        ]
        
        for i, (label_text, attr, default) in enumerate(fields):
            tk.Label(form_inner, text=label_text, bg="#0f3460", fg="#a0a0a0", 
                    font=("Segoe UI", 11)).grid(row=i, column=0, sticky="w", pady=15)
            
            if attr == "flight":
                combo = ttk.Combobox(form_inner, values=self.get_flight_numbers(), 
                                  state="readonly", width=25, font=("Segoe UI", 11))
                combo.set(default)
                combo.grid(row=i, column=1, pady=15, padx=15)
                setattr(self, f"booking_{attr}_combo", combo)
            elif attr == "class":
                combo = ttk.Combobox(form_inner, values=["Economy", "Business", "First"], 
                                   state="readonly", width=25, font=("Segoe UI", 11))
                combo.set(default)
                combo.grid(row=i, column=1, pady=15, padx=15)
                setattr(self, f"booking_{attr}_combo", combo)
            else:
                entry = ttk.Entry(form_inner, width=27, font=("Segoe UI", 11))
                entry.grid(row=i, column=1, pady=15, padx=15)
                setattr(self, f"booking_{attr}_entry", entry)
        
        sep = tk.Frame(form_inner, bg="#e94560", height=1)
        sep.grid(row=len(fields), column=0, columnspan=2, pady=20, sticky="ew")
        
        payment_fields = [
            ("Payment Method:", "payment", "Credit Card"),
            ("Card Number:", "card", ""),
            ("CVV:", "cvv", ""),
        ]
        
        start_row = len(fields) + 1
        for i, (label_text, attr, default) in enumerate(payment_fields):
            tk.Label(form_inner, text=label_text, bg="#0f3460", fg="#a0a0a0", 
                    font=("Segoe UI", 11)).grid(row=start_row + i, column=0, sticky="w", pady=15)
            
            if attr == "payment":
                combo = ttk.Combobox(form_inner, values=["Credit Card", "Debit Card", "UPI", "Net Banking"], 
                                     state="readonly", width=25, font=("Segoe UI", 11))
                combo.set(default)
                combo.grid(row=start_row + i, column=1, pady=15, padx=15)
                setattr(self, f"booking_{attr}_combo", combo)
            else:
                entry = ttk.Entry(form_inner, width=27, font=("Segoe UI", 11), show="*" if attr == "cvv" else "")
                entry.grid(row=start_row + i, column=1, pady=15, padx=15)
                setattr(self, f"booking_{attr}_entry", entry)
        
        book_btn = tk.Button(form_inner, text="🎫 Book Now", command=self.book_ticket,
                          bg="#e94560", fg="white", font=("Segoe UI", 14, "bold"),
                          relief="flat", width=20, height=2, cursor="hand2")
        book_btn.grid(row=start_row + len(payment_fields), column=0, columnspan=2, pady=25)
        
        right_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title2 = tk.Label(right_panel, text="Booking Summary", font=("Segoe UI", 22, "bold"), 
                       bg="#1a1a2e", fg="white")
        title2.pack(pady=(0, 25), anchor="w")
        
        self.ticket_preview = tk.Frame(right_panel, bg="#0f3460", relief="flat", bd=0)
        self.ticket_preview.pack(fill="both", expand=True)
        
        tk.Label(self.ticket_preview, text="✈ SKYBOOK AIRLINES", bg="#0f3460", fg="#e94560", 
               font=("Segoe UI", 18, "bold")).pack(pady=(30, 10))
        
        self.pnr_display = tk.Label(self.ticket_preview, text="PNR: ---", bg="#0f3460", 
                                   fg="#ffffff", font=("Segoe UI", 16, "bold"))
        self.pnr_display.pack()
        
        self.booking_details = tk.Label(self.ticket_preview, text="Booking details will appear here", 
                                    bg="#0f3460", fg="#a0a0a0", font=("Segoe UI", 11))
        self.booking_details.pack(pady=20)
        
        tk.Label(self.ticket_preview, text="✈", bg="#0f3460", fg="#3498db", 
               font=("Segoe UI", 40)).pack()
        
        self.status_booking = tk.Label(self.ticket_preview, text="Status: Pending", bg="#0f3460", 
                                  fg="#f39c12", font=("Segoe UI", 12, "bold"))
        self.status_booking.pack(pady=10)
    
    def book_ticket(self):
        flight_num = self.booking_flight_combo.get()
        name = self.booking_name_entry.get().strip()
        email = self.booking_email_entry.get().strip()
        phone = self.booking_phone_entry.get().strip()
        class_type = self.booking_class_combo.get()
        payment = self.booking_payment_combo.get()
        card_num = self.booking_card_entry.get().strip()
        cvv = self.booking_cvv_entry.get().strip()
        
        if not all([flight_num, name, email, phone, payment, card_num, cvv]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if len(card_num) < 12:
            messagebox.showerror("Error", "Invalid card number!")
            return
        
        if len(cvv) < 2:
            messagebox.showerror("Error", "Invalid CVV!")
            return
        
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Invalid email address!")
            return
        
        self.cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_num,))
        flight = self.cursor.fetchone()
        
        if not flight:
            messagebox.showerror("Error", "Flight not found!")
            return
        
        class_multiplier = {"Economy": 1, "Business": 2, "First": 3}.get(class_type, 1)
        base_price = flight[7]
        base_fare = base_price * class_multiplier
        tax = base_fare * 0.10
        total_cost = base_fare + tax
        
        user_id = self.generate_user_id()
        pnr = self.generate_pnr()
        
        try:
            self.cursor.execute('''INSERT INTO bookings 
                (pnr, user_id, flight_id, passenger_name, passenger_email, passenger_phone, 
                 seat_number, class_type, trip_type, booking_date, total_cost, status, gate_number, boarding_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (pnr, user_id, flight[0], name, email, phone, None, class_type, "one_way",
                 datetime.now().strftime("%Y-%m-%d %H:%M"), total_cost, "Confirmed", 
                 f"Gate {random.randint(1, 20)}", flight[4]))
            
            self.cursor.execute('''INSERT INTO passengers (user_id, name, email, phone, created_at)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, name, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M")))
            
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Database error: {e}")
            return
        
        self.current_user_id = user_id
        self.current_pnr = pnr
        self.current_booking_data = {
            "pnr": pnr,
            "user_id": user_id,
            "flight": flight_num,
            "route": f"{flight[2]} → {flight[3]}",
            "name": name,
            "class": class_type,
            "total": total_cost
        }
        
        self.pnr_display.config(text=f"PNR: {pnr}")
        self.booking_details.config(text=f"Name: {name}\nFlight: {flight_num}\nRoute: {flight[2]} ➝ {flight[3]}\nClass: {class_type}\nTotal: ₹{int(total_cost):,}")
        self.status_booking.config(text="✓ Confirmed", fg="#00d26a")
        
        messagebox.showinfo("Success", f"🎫 Ticket booked successfully!\n\nPNR: {pnr}\nUser ID: {user_id}\n\nProceed to Seat Allocation to select your seat.")
        self.notebook.select(3)
    
    def generate_user_id(self):
        chars = string.ascii_uppercase + string.digits
        return "SK" + "".join(random.choices(chars, k=6))
    
    def generate_pnr(self):
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=6))
    
    def create_seat_tab(self):
        main_container = tk.Frame(self.tab_seat, bg="#16213e")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        left_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        title = tk.Label(left_panel, text="Seat Allocation", font=("Segoe UI", 22, "bold"), 
                       bg="#1a1a2e", fg="white")
        title.pack(pady=(0, 25), anchor="w")
        
        card = tk.Frame(left_panel, bg="#0f3460", relief="flat", bd=0)
        card.pack(fill="x", pady=10)
        
        inner = tk.Frame(card, bg="#0f3460", padx=25, pady=25)
        inner.pack(fill="x")
        
        tk.Label(inner, text="Enter PNR:", bg="#0f3460", fg="#a0a0a0", 
               font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=15)
        self.pnr_entry = ttk.Entry(inner, width=25, font=("Segoe UI", 11))
        self.pnr_entry.grid(row=0, column=1, pady=15, padx=15)
        
        retrieve_btn = tk.Button(inner, text="🔍 Retrieve Booking", command=self.retrieve_booking,
                                bg="#3498db", fg="white", font=("Segoe UI", 11, "bold"),
                                relief="flat", width=18, height=2, cursor="hand2")
        retrieve_btn.grid(row=1, column=0, columnspan=2, pady=15)
        
        tk.Label(inner, text="Or Enter User ID:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=15)
        self.user_id_entry = ttk.Entry(inner, width=25, font=("Segoe UI", 11))
        self.user_id_entry.grid(row=2, column=1, pady=15, padx=15)
        
        find_btn = tk.Button(inner, text="🔍 Find by User ID", command=self.retrieve_by_user_id,
                          bg="#3498db", fg="white", font=("Segoe UI", 11, "bold"),
                          relief="flat", width=18, height=2, cursor="hand2")
        find_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        self.booking_info = tk.Label(inner, text="No booking loaded", bg="#0f3460", 
                                    fg="#a0a0a0", font=("Segoe UI", 10), wraplength=280)
        self.booking_info.grid(row=4, column=0, columnspan=2, pady=20)
        
        board_btn = tk.Button(inner, text="🎫 Generate Boarding Pass", command=self.generate_boarding_pass,
                             bg="#27ae60", fg="white", font=("Segoe UI", 13, "bold"),
                             relief="flat", width=22, height=2, cursor="hand2")
        board_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
        right_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title2 = tk.Label(right_panel, text="Select Your Seat", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title2.pack(pady=(0, 25), anchor="w")
        
        seat_card = tk.Frame(right_panel, bg="#0f3460", relief="flat", bd=0)
        seat_card.pack(fill="both", expand=True)
        
        seat_frame = tk.Frame(seat_card, bg="#0f3460")
        seat_frame.pack(padx=20, pady=20)
        
        tk.Label(seat_frame, text="FRONT OF AIRCRAFT", bg="#0f3460", fg="#3498db", 
               font=("Segoe UI", 10, "bold")).pack()
        
        self.seat_buttons = {}
        rows = ["A", "B", "C", "D", "E", "F"]
        cols = list(range(1, 21))
        
        for row in rows:
            seat_row = tk.Frame(seat_frame, bg="#0f3460")
            seat_row.pack(pady=2)
            
            tk.Label(seat_row, text=row, bg="#0f3460", fg="white", width=3, 
                   font=("Segoe UI", 10, "bold")).pack(side="left")
            
            for col in cols:
                seat_num = f"{row}{col}"
                btn_color = "#95a5a6" if seat_num in self.occupied_seats else "#27ae60"
                btn = tk.Button(seat_row, text=seat_num, width=4, height=2,
                           bg=btn_color, fg="white", font=("Segoe UI", 8),
                           relief="flat", cursor="hand2",
                           command=lambda s=seat_num: self.select_seat(s),
                           state="disabled" if seat_num in self.occupied_seats else "normal")
                btn.pack(side="left", padx=1)
                self.seat_buttons[seat_num] = btn
            
            tk.Label(seat_row, text=row, bg="#0f3460", fg="white", width=3, 
                   font=("Segoe UI", 10, "bold")).pack(side="left")
        
        tk.Label(seat_frame, text="       AISLE       ", bg="#0f3460", fg="#3498db", 
               font=("Segoe UI", 9)).pack()
        
        legend_frame = tk.Frame(seat_card, bg="#0f3460", pady=15)
        legend_frame.pack()
        
        for color, text in [("#27ae60", "Available"), ("#e94560", "Selected"), ("#95a5a6", "Occupied")]:
            tk.Label(legend_frame, text=text, bg=color, fg="white", width=12, 
                   font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)
    
    def select_seat(self, seat_num):
        if self.selected_seat:
            self.seat_buttons[self.selected_seat].config(bg="#27ae60", state="normal")
        
        self.selected_seat = seat_num
        self.seat_buttons[seat_num].config(bg="#e94560", state="disabled")
        
        messagebox.showinfo("Seat Selected", f"You selected seat {seat_num}")
    
    def retrieve_booking(self):
        pnr = self.pnr_entry.get().strip()
        
        if not pnr:
            messagebox.showerror("Error", "Please enter a PNR!")
            return
        
        self.cursor.execute('''SELECT b.*, f.flight_number, f.origin, f.destination, 
            f.departure_time, f.arrival_time FROM bookings b 
            JOIN flights f ON b.flight_id = f.flight_id WHERE b.pnr = ? AND b.status = 'Confirmed''',
            (pnr,))
        
        booking = self.cursor.fetchone()
        
        if not booking:
            messagebox.showerror("Error", "No active booking found with this PNR!")
            return
        
        self.current_pnr = pnr
        self.current_user_id = booking[1]
        
        seat_text = booking[6] if booking[6] else "Not assigned"
        self.booking_info.config(text=f"Passenger: {booking[3]}\nFlight: {booking[11]}\n{booking[12]} ➝ {booking[13]}\nClass: {booking[8]}\nSeat: {seat_text}")
        
        messagebox.showinfo("Success", "Booking retrieved! Select your seat.")
    
    def retrieve_by_user_id(self):
        user_id = self.user_id_entry.get().strip()
        
        if not user_id:
            messagebox.showerror("Error", "Please enter a User ID!")
            return
        
        self.cursor.execute('''SELECT b.*, f.flight_number, f.origin, f.destination, 
            f.departure_time, f.arrival_time FROM bookings b 
            JOIN flights f ON b.flight_id = f.flight_id WHERE b.user_id = ? AND b.status = 'Confirmed''',
            (user_id,))
        
        booking = self.cursor.fetchone()
        
        if not booking:
            messagebox.showerror("Error", "No active booking found with this User ID!")
            return
        
        self.current_pnr = booking[0]
        self.current_user_id = user_id
        self.pnr_entry.delete(0, "end")
        self.pnr_entry.insert(0, booking[0])
        
        seat_text = booking[6] if booking[6] else "Not assigned"
        self.booking_info.config(text=f"Passenger: {booking[3]}\nFlight: {booking[11]}\n{booking[12]} ➝ {booking[13]}\nClass: {booking[8]}\nSeat: {seat_text}")
        
        messagebox.showinfo("Success", "Booking retrieved! Select your seat.")
    
    def generate_boarding_pass(self):
        if not self.current_pnr:
            messagebox.showerror("Error", "Please retrieve a booking first!")
            return
        
        if not self.selected_seat:
            messagebox.showerror("Error", "Please select a seat first!")
            return
        
        self.cursor.execute('''UPDATE bookings SET seat_number = ? WHERE pnr = ?''',
                            (self.selected_seat, self.current_pnr))
        self.conn.commit()
        
        self.cursor.execute('''SELECT b.*, f.flight_number, f.origin, f.destination, 
            f.departure_time, f.arrival_time, f.aircraft FROM bookings b 
            JOIN flights f ON b.flight_id = f.flight_id WHERE b.pnr = ?''', (self.current_pnr,))
        
        booking = self.cursor.fetchone()
        
        messagebox.showinfo("Boarding Pass", 
            f"═══════════════════════════════\n"
            f"       ✈ SKYBOOK AIRLINES ✈\n"
            f"═══════════════════════════════\n\n"
            f"PNR: {booking[0]}\n"
            f"User ID: {booking[1]}\n\n"
            f"Passenger: {booking[3]}\n\n"
            f"Flight: {booking[11]}\n"
            f"From: {booking[12]}\n"
            f"To: {booking[13]}\n\n"
            f"Date: {booking[10][:10]}\n"
            f"Time: {booking[14]}\n\n"
            f"────────── BOARDING PASS ──────────\n\n"
            f"SEAT: {self.selected_seat}\n"
            f"Gate: {booking[13]}\n"
            f"Class: {booking[8]}\n"
            f"Aircraft: {booking[16]}\n\n"
            f"═══════════════════════════════\n"
            f"     Have a pleasant journey! ✈\n"
            f"═══════════════════════════════")
        
        self.notebook.select(4)
    
    def create_cancel_tab(self):
        main_container = tk.Frame(self.tab_cancel, bg="#16213e")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        left_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        title = tk.Label(left_panel, text="Cancel Booking", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title.pack(pady=(0, 25), anchor="w")
        
        card = tk.Frame(left_panel, bg="#0f3460", relief="flat", bd=0)
        card.pack(fill="x", pady=10)
        
        inner = tk.Frame(card, bg="#0f3460", padx=25, pady=25)
        inner.pack(fill="x")
        
        tk.Label(inner, text="Enter PNR:", bg="#0f3460", fg="#a0a0a0", 
                font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=15)
        self.cancel_pnr = ttk.Entry(inner, width=25, font=("Segoe UI", 11))
        self.cancel_pnr.grid(row=0, column=1, pady=15, padx=15)
        
        check_btn = tk.Button(inner, text="🔍 Check Booking", command=self.check_booking,
                          bg="#f39c12", fg="white", font=("Segoe UI", 12, "bold"),
                          relief="flat", width=18, height=2, cursor="hand2")
        check_btn.grid(row=1, column=0, columnspan=2, pady=15)
        
        self.cancel_booking_info = tk.Label(inner, text="", bg="#0f3460", fg="#a0a0a0", 
                                        font=("Segoe UI", 10), wraplength=300)
        self.cancel_booking_info.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.refund_label = tk.Label(inner, text="", bg="#0f3460", fg="#00d26a", 
                                     font=("Segoe UI", 16, "bold"))
        self.refund_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        cancel_btn = tk.Button(inner, text="❌ Cancel Booking", command=self.cancel_booking,
                              bg="#e74c3c", fg="white", font=("Segoe UI", 13, "bold"),
                              relief="flat", width=18, height=2, cursor="hand2")
        cancel_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        right_panel = tk.Frame(main_container, bg="#1a1a2e", relief="flat", bd=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title2 = tk.Label(right_panel, text="Refund Policy", font=("Segoe UI", 22, "bold"), 
                        bg="#1a1a2e", fg="white")
        title2.pack(pady=(0, 25), anchor="w")
        
        policy_card = tk.Frame(right_panel, bg="#0f3460", relief="flat", bd=0)
        policy_card.pack(fill="both", expand=True)
        
        policy_frame = tk.Frame(policy_card, bg="#0f3460", padx=30, pady=30)
        policy_frame.pack(fill="both")
        
        policies = [
            ("24+ hours before departure", "80%", "#27ae60"),
            ("12-24 hours before departure", "50%", "#f39c12"),
            ("Less than 12 hours", "No refund", "#e74c3c"),
        ]
        
        for time, refund, color in policies:
            tk.Label(policy_frame, text=time, bg="#0f3460", fg="white", 
                   font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(15, 5))
            tk.Label(policy_frame, text=refund, bg="#0f3460", fg=color, 
                   font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))
    
    def check_booking(self):
        pnr = self.cancel_pnr.get().strip()
        
        if not pnr:
            messagebox.showerror("Error", "Please enter a PNR!")
            return
        
        self.cursor.execute('''SELECT b.*, f.flight_number, f.origin, f.destination, 
            f.departure_time FROM bookings b 
            JOIN flights f ON b.flight_id = f.flight_id WHERE b.pnr = ? AND b.status = 'Confirmed''',
            (pnr,))
        
        booking = self.cursor.fetchone()
        
        if not booking:
            messagebox.showerror("Error", "No active booking found with this PNR!")
            return
        
        self.cancel_booking_info.config(text=f"Passenger: {booking[3]}\nFlight: {booking[11]}\n{booking[12]} ➝ {booking[13]}\nClass: {booking[8]}\nTotal: ₹{int(booking[11]):,}")
        
        self.refund_label.config(text=f"Refund: ₹{int(booking[11] * 0.80):,} (80%)")
        
        self.current_refund_percent = 0.80
    
    def cancel_booking(self):
        pnr = self.cancel_pnr.get().strip()
        
        if not pnr:
            messagebox.showerror("Error", "Please enter a PNR!")
            return
        
        confirm = messagebox.askyesno("Confirm Cancellation", 
            f"Are you sure you want to cancel booking {pnr}?")
        
        if not confirm:
            return
        
        self.cursor.execute('''UPDATE bookings SET status = 'Cancelled' WHERE pnr = ?''', (pnr,))
        self.conn.commit()
        
        refund_ref = f"REF{random.randint(100000, 999999)}"
        
        messagebox.showinfo("Cancellation Confirmed", 
            f"✓ Your booking has been cancelled.\n\n"
            f"PNR: {pnr}\n"
            f"Refund Reference: {refund_ref}\n\n"
            f"Refund will be processed within 5-7 days.")
        
        self.cancel_booking_info.config(text="")
        self.refund_label.config(text="")
        self.cancel_pnr.delete(0, "end")
    
    def refresh_data(self):
        try:
            flights = self.get_flight_numbers()
            self.cost_flight_combo["values"] = flights
        except:
            pass

def main():
    root = tk.Tk()
    app = AirlineReservationSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()