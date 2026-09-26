# SwiftTravel — Bus Reservation System (Python)

A console-based bus reservation system built in Python to practice core programming
and data-handling concepts: OOP design, file-based persistence, data validation,
and clean function-based structure — the same fundamentals used in real
data-processing and ETL scripts.

## Features

- View available buses/journeys and live seat availability
- View a seat map (booked vs. available seats)
- Book a ticket with input validation (name, age, journey, seat)
- Age-based fare calculation (child discount, senior discount, full fare)
- Unique booking ID generation
- Cancel a ticket and automatically release the seat
- Waiting list: when a bus is full, passengers can queue — and when a seat is
  freed by a cancellation, it's automatically reassigned to the earliest
  waiting passenger (FIFO)
- Search bookings by passenger name (partial match) or booking ID
- Persistent storage: all data is saved to and loaded from a JSON file, so
  bookings survive across program runs
- Exception handling for invalid input (non-numeric age, invalid seat, etc.)

## Tech / Concepts Used

- **OOP**: `Passenger`, `Bus`, `Booking`, `WaitingPassenger`, and a
  `ReservationSystem` controller class
- **Data structures**: dictionaries for fast lookups, sets for booked seats,
  tuples for fixed route data, list comprehensions for available seats
- **File handling**: JSON read/write with `with open(...)` for persistence
- **Exception handling**: `try/except` around all user input
- **Pure Python standard library** — no external dependencies

## How to Run

```bash
python bus_reservation_system.py
```

No installation needed — it only uses Python's standard library (`json`, `os`).

## Project Structure

```
bus-reservation-system/
├── bus_reservation_system.py   # main application
├── README.md
└── .gitignore
```

A `reservation_data.json` file is created automatically the first time you run
the program, and is ignored by Git so each user starts with a clean slate.

## Sample Flow

```
=====================================
 BUS RESERVATION SYSTEM - SwiftTravel
=====================================
1. View Buses
2. View Available Seats
3. Book Ticket
4. Cancel Ticket
5. View Booking
6. Search Passenger / Booking
7. Exit
Enter your choice:
```

## Possible Extensions

- Move storage from JSON to a proper database (SQLite/PostgreSQL)
- Add a REST API layer (Flask/FastAPI) on top of the existing logic
- Add automated tests (pytest) for booking/cancellation edge cases
