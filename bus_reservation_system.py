"""
SwiftTravel - Console-Based Bus Reservation System
====================================================
A practice Python project demonstrating:
    - OOP (classes, objects, __init__, methods)
    - Collections (lists, dicts, tuples, sets, comprehensions)
    - Conditionals & loops
    - Functions & clean code structure
    - String handling & built-in functions
    - File handling (save/load with JSON)
    - Exception handling
    - A "final challenge" waiting-list auto-assignment feature

Run with:  python bus_reservation_system.py
"""

import json
import os

DATA_FILE = "reservation_data.json"


# ---------------------------------------------------------------------------
# OOP CLASSES
# ---------------------------------------------------------------------------

class Passenger:
    """Represents a single passenger."""

    def __init__(self, name, age):
        self.name = name.strip().title()
        self.age = age

    def to_dict(self):
        return {"name": self.name, "age": self.age}

    @staticmethod
    def from_dict(data):
        return Passenger(data["name"], data["age"])

    def __str__(self):
        return f"{self.name} (Age: {self.age})"


class Bus:
    """Represents a bus/journey with a fixed route (tuple) and seat layout."""

    def __init__(self, bus_id, source, destination, departure, arrival,
                 total_seats, fare, booked_seats=None):
        self.bus_id = bus_id
        self.route = (source, destination)          # tuple: fixed info
        self.departure = departure
        self.arrival = arrival
        self.total_seats = total_seats
        self.fare = fare
        self.booked_seats = set(booked_seats) if booked_seats else set()  # unique values

    @property
    def available_seats(self):
        """List comprehension: all seats not currently booked."""
        return [seat for seat in range(1, self.total_seats + 1)
                if seat not in self.booked_seats]

    @property
    def seats_available_count(self):
        return len(self.available_seats)

    def is_seat_available(self, seat_no):
        return seat_no in self.available_seats

    def book_seat(self, seat_no):
        self.booked_seats.add(seat_no)

    def release_seat(self, seat_no):
        self.booked_seats.discard(seat_no)

    def to_dict(self):
        return {
            "bus_id": self.bus_id,
            "source": self.route[0],
            "destination": self.route[1],
            "departure": self.departure,
            "arrival": self.arrival,
            "total_seats": self.total_seats,
            "fare": self.fare,
            "booked_seats": list(self.booked_seats),
        }

    @staticmethod
    def from_dict(data):
        return Bus(
            data["bus_id"], data["source"], data["destination"],
            data["departure"], data["arrival"], data["total_seats"],
            data["fare"], data.get("booked_seats", []),
        )


class Booking:
    """Represents a single confirmed / cancelled booking."""

    def __init__(self, booking_id, passenger: Passenger, bus_id, seat_no,
                 fare, status="CONFIRMED"):
        self.booking_id = booking_id
        self.passenger = passenger
        self.bus_id = bus_id
        self.seat_no = seat_no
        self.fare = fare
        self.status = status

    def cancel(self):
        self.status = "CANCELLED"

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "passenger": self.passenger.to_dict(),
            "bus_id": self.bus_id,
            "seat_no": self.seat_no,
            "fare": self.fare,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        return Booking(
            data["booking_id"],
            Passenger.from_dict(data["passenger"]),
            data["bus_id"], data["seat_no"], data["fare"], data["status"],
        )

    def display(self):
        print("=" * 40)
        print(" BOOKING DETAILS")
        print("=" * 40)
        print(f"Booking ID : {self.booking_id}")
        print(f"Passenger  : {self.passenger.name}")
        print(f"Journey    : {self.bus_id}")
        print(f"Seat       : {self.seat_no:02d}")
        print(f"Fare       : Rs.{self.fare}")
        print(f"Status     : {self.status}")
        print("=" * 40)


class WaitingPassenger:
    """A passenger waiting for a seat on a fully booked bus."""

    def __init__(self, passenger: Passenger, bus_id):
        self.passenger = passenger
        self.bus_id = bus_id

    def to_dict(self):
        return {"passenger": self.passenger.to_dict(), "bus_id": self.bus_id}

    @staticmethod
    def from_dict(data):
        return WaitingPassenger(Passenger.from_dict(data["passenger"]), data["bus_id"])


# ---------------------------------------------------------------------------
# RESERVATION SYSTEM (core application logic)
# ---------------------------------------------------------------------------

class ReservationSystem:
    def __init__(self):
        self.buses = {}          # bus_id -> Bus
        self.bookings = {}       # booking_id -> Booking
        self.waiting_list = []   # list[WaitingPassenger], FIFO order preserved
        self.booking_counter = 1000
        self._seed_default_buses()
        self.load_data()

    # ---------------- setup / persistence ----------------

    def _seed_default_buses(self):
        """Only used if no saved data exists yet."""
        self.buses["B101"] = Bus("B101", "Pune", "Mumbai", "08:00 AM", "12:00 PM", 10, 450)
        self.buses["B102"] = Bus("B102", "Pune", "Nashik", "09:30 AM", "01:00 PM", 12, 350)

    def save_data(self):
        """Persist buses, bookings, waiting list and counter to a JSON file."""
        data = {
            "buses": [b.to_dict() for b in self.buses.values()],
            "bookings": [bk.to_dict() for bk in self.bookings.values()],
            "waiting_list": [w.to_dict() for w in self.waiting_list],
            "booking_counter": self.booking_counter,
        }
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Warning: could not save data ({e}).")

    def load_data(self):
        """Load previously saved data, if the file exists."""
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            self.buses = {b["bus_id"]: Bus.from_dict(b) for b in data.get("buses", [])}
            self.bookings = {bk["booking_id"]: Booking.from_dict(bk)
                              for bk in data.get("bookings", [])}
            self.waiting_list = [WaitingPassenger.from_dict(w)
                                  for w in data.get("waiting_list", [])]
            self.booking_counter = data.get("booking_counter", 1000)
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"Warning: could not load saved data ({e}). Starting fresh.")

    # ---------------- helpers ----------------

    def generate_booking_id(self):
        """Generate a unique, human-readable booking ID."""
        self.booking_counter += 1
        return f"ST{self.booking_counter}"

    @staticmethod
    def calculate_fare(base_fare, age):
        """Apply simple age-based discount rules."""
        if age < 12:
            return round(base_fare * 0.5, 2)
        elif age >= 60:
            return round(base_fare * 0.7, 2)
        else:
            return base_fare

    def _process_waiting_list(self, bus_id):
        """
        FINAL CHALLENGE feature:
        When a seat frees up on a bus, automatically pull the earliest
        waiting passenger(s) for that bus and confirm bookings for them,
        while keeping the rest of the waiting list in original order.
        """
        bus = self.buses.get(bus_id)
        if not bus:
            return

        still_waiting = []
        for waiter in self.waiting_list:
            if waiter.bus_id == bus_id and bus.available_seats:
                seat_no = bus.available_seats[0]
                bus.book_seat(seat_no)
                fare = self.calculate_fare(bus.fare, waiter.passenger.age)
                booking_id = self.generate_booking_id()
                booking = Booking(booking_id, waiter.passenger, bus_id, seat_no, fare)
                self.bookings[booking_id] = booking
                print(f"  -> Waiting passenger {waiter.passenger.name} auto-assigned "
                      f"seat {seat_no:02d} (Booking ID: {booking_id}).")
            else:
                still_waiting.append(waiter)
        self.waiting_list = still_waiting

    # ---------------- core features ----------------

    def view_buses(self):
        print("-" * 65)
        print(f"{'ID':<6}{'ROUTE':<20}{'TIME':<12}{'FARE':<10}{'SEATS':<6}")
        print("-" * 65)
        for bus in self.buses.values():
            route_str = f"{bus.route[0]}-{bus.route[1]}"
            print(f"{bus.bus_id:<6}{route_str:<20}{bus.departure:<12}"
                  f"Rs.{bus.fare:<8}{bus.seats_available_count:<6}")
        print("-" * 65)

    def view_seats(self, bus_id):
        bus = self.buses.get(bus_id)
        if not bus:
            print(f"No bus found with ID '{bus_id}'.")
            return
        print(f"\n BUS {bus.bus_id}")
        for row_start in range(1, bus.total_seats + 1, 2):
            row = []
            for seat in (row_start, row_start + 1):
                if seat <= bus.total_seats:
                    row.append(f"[{seat:02d}]")
            print(" " + " ".join(row))
        available_str = " ".join(f"{s:02d}" for s in sorted(bus.available_seats))
        booked_str = " ".join(f"{s:02d}" for s in sorted(bus.booked_seats))
        print(f"\nAvailable: {available_str if available_str else 'None'}")
        print(f"Booked   : {booked_str if booked_str else 'None'}")

    def book_ticket(self):
        try:
            name = input("Enter passenger name: ").strip()
            if not name:
                print("Name cannot be empty.")
                return

            age = int(input("Enter age: ").strip())
            if age <= 0 or age > 120:
                print("Please enter a realistic age.")
                return

            bus_id = input("Enter journey ID: ").strip().upper()
            bus = self.buses.get(bus_id)
            if not bus:
                print(f"No journey found with ID '{bus_id}'.")
                return

            if not bus.available_seats:
                self._offer_waiting_list(name, age, bus_id)
                return

            seat_no = int(input("Select seat: ").strip())
            if not bus.is_seat_available(seat_no):
                print(f"Seat {seat_no} is not available. Please choose another seat.")
                return

            print("Processing booking...")
            passenger = Passenger(name, age)
            fare = self.calculate_fare(bus.fare, age)
            booking_id = self.generate_booking_id()
            booking = Booking(booking_id, passenger, bus_id, seat_no, fare)

            bus.book_seat(seat_no)
            self.bookings[booking_id] = booking
            self.save_data()

            print("\nBooking successful!")
            print("=" * 40)
            print(" BOOKING CONFIRMED")
            print("=" * 40)
            print(f"Booking ID : {booking_id}")
            print(f"Passenger  : {passenger.name}")
            print(f"Journey    : {bus_id}")
            print(f"Route      : {bus.route[0]} -> {bus.route[1]}")
            print(f"Seat       : {seat_no:02d}")
            print(f"Fare       : Rs.{fare}")
            print(f"Status     : CONFIRMED")
            print("=" * 40)

        except ValueError:
            print("Invalid input. Age and seat number must be numbers. Please try again.")
        except Exception as e:
            print(f"Unexpected error while booking: {e}")

    def _offer_waiting_list(self, name, age, bus_id):
        print(f"Bus {bus_id} is fully booked.")
        choice = input("Would you like to join the waiting list? (yes/no): ").strip().lower()
        if choice == "yes":
            passenger = Passenger(name, age)
            self.waiting_list.append(WaitingPassenger(passenger, bus_id))
            self.save_data()
            print(f"{passenger.name} added to the waiting list for {bus_id}.")
        else:
            print("Booking not made.")

    def cancel_ticket(self):
        try:
            booking_id = input("Enter Booking ID: ").strip().upper()
            booking = self.bookings.get(booking_id)

            if not booking:
                print("Booking not found.")
                return

            if booking.status == "CANCELLED":
                print("This booking is already cancelled.")
                return

            print("Booking found.")
            print(f"Passenger: {booking.passenger.name}")
            print(f"Seat: {booking.seat_no:02d}")
            confirm = input("Cancel booking? (yes/no): ").strip().lower()

            if confirm == "yes":
                bus = self.buses.get(booking.bus_id)
                booking.cancel()
                if bus:
                    bus.release_seat(booking.seat_no)
                print("Booking cancelled successfully.")
                print(f"Seat {booking.seat_no:02d} is now available.")

                # Final-challenge behaviour: auto-fill freed seat from waiting list
                self._process_waiting_list(booking.bus_id)
                self.save_data()
            else:
                print("Cancellation aborted.")

        except Exception as e:
            print(f"Unexpected error while cancelling: {e}")

    def view_booking(self):
        booking_id = input("Enter Booking ID: ").strip().upper()
        booking = self.bookings.get(booking_id)
        if not booking:
            print("Booking not found.")
            return
        booking.display()

    def search(self):
        query = input("Enter passenger name or Booking ID: ").strip().lower()
        if not query:
            print("Please enter a search term.")
            return

        # Search by exact booking ID first
        exact = self.bookings.get(query.upper())
        results = [exact] if exact else []

        # Partial name matching (case-insensitive)
        results += [
            bk for bk in self.bookings.values()
            if bk not in results and query in bk.passenger.name.lower()
        ]

        if not results:
            print("No matching bookings found.")
            return

        print("\nSearch Results")
        print("-" * 40)
        for bk in results:
            print(f"Booking ID : {bk.booking_id}")
            print(f"Passenger  : {bk.passenger.name}")
            print(f"Journey    : {bk.bus_id}")
            print(f"Seat       : {bk.seat_no:02d}")
            print(f"Status     : {bk.status}")
            print("-" * 40)


# ---------------------------------------------------------------------------
# MENU / DRIVER CODE
# ---------------------------------------------------------------------------

def display_menu():
    print("\n" + "=" * 37)
    print(" BUS RESERVATION SYSTEM - SwiftTravel")
    print("=" * 37)
    print("1. View Buses")
    print("2. View Available Seats")
    print("3. Book Ticket")
    print("4. Cancel Ticket")
    print("5. View Booking")
    print("6. Search Passenger / Booking")
    print("7. Exit")


def main():
    system = ReservationSystem()

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            system.view_buses()
        elif choice == "2":
            bus_id = input("Enter journey ID: ").strip().upper()
            system.view_seats(bus_id)
        elif choice == "3":
            system.book_ticket()
        elif choice == "4":
            system.cancel_ticket()
        elif choice == "5":
            system.view_booking()
        elif choice == "6":
            system.search()
        elif choice == "7":
            system.save_data()
            print("Thank you for using SwiftTravel. Safe travels!")
            break
        else:
            print("Invalid choice. Please select an option from 1-7.")


if __name__ == "__main__":
    main()
