import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DATABASE = "flight_management.db"
SETUP_SCRIPT = "create_database.py"
VALID_STATUSES = ("Scheduled", "Delayed", "Cancelled")
REQUIRED_TABLES = {"Flights", "Pilots", "Airports", "Flight_Pilot_Assignments"}


# ---------------------------------------------------------------------------
# Database connection and helper functions
# ---------------------------------------------------------------------------

@contextmanager
def database():
    """Open a connection with foreign keys enforced.

    Changes are committed if the block finishes normally, rolled back if an
    error occurs, and the connection is always closed afterwards.
    """
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def database_ready():
    """Return True if the database file exists and contains all four tables."""
    if not os.path.exists(DATABASE):
        return False
    with database() as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    return REQUIRED_TABLES <= {row[0] for row in rows}


def show_table(headers, rows):
    """Print query results as an aligned table with a header row."""
    if not rows:
        print("No matching records found.")
        return

    # Work out the width of each column from the headers and the data.
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))

    def line(values):
        return " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(values))

    print(line(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(line(row))


def ask_int(prompt):
    """Ask for a whole number. Returns None (after a message) if invalid."""
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Please enter a number.")
        return None


def valid_date(text):
    """Check a date is in YYYY-MM-DD format and is a real calendar date."""
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def valid_time(text):
    """Check a time is in 24-hour HH:MM format."""
    try:
        datetime.strptime(text, "%H:%M")
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def display_menu():
    """Print the main menu."""
    print("\n=== Flight Management System ===")
    print("1.  Add a New Flight")
    print("2.  View Flights by Criteria")
    print("3.  Update Flight Information")
    print("4.  Assign Pilot to Flight")
    print("5.  View Pilot Schedule")
    print("6.  View/Update Airport Information")
    print("7.  View Flight Statistics")
    print("8.  Delete a Flight")
    print("9.  Remove Pilot from Flight")
    print("10. View All Pilots")
    print("0.  Exit")


# ---------------------------------------------------------------------------
# Menu option 1: Add a new flight (CREATE)
# ---------------------------------------------------------------------------

def add_flight():
    """Collect flight details, validate them, and INSERT a row into Flights."""
    print("\n=== Add a New Flight ===")
    flight_number = input("Flight number: ").strip().upper()
    departure_date = input("Departure date (YYYY-MM-DD): ").strip()
    departure_time = input("Departure time (HH:MM): ").strip()
    status = input("Status (Scheduled, Delayed, Cancelled): ").strip().title()
    origin = input("Origin airport code: ").strip().upper()
    destination = input("Destination airport code: ").strip().upper()

    # Input validation before touching the database
    if not all([flight_number, departure_date, departure_time,
                status, origin, destination]):
        print("All fields are required.")
        return
    if not valid_date(departure_date):
        print("Invalid date. Use the format YYYY-MM-DD.")
        return
    if not valid_time(departure_time):
        print("Invalid time. Use the 24-hour format HH:MM.")
        return
    if status not in VALID_STATUSES:
        print("Invalid status.")
        return
    if origin == destination:
        print("Origin and destination must be different.")
        return

    try:
        with database() as connection:
            # Parameterised INSERT: the ? placeholders prevent SQL injection.
            # The foreign keys reject airport codes that don't exist.
            cursor = connection.execute("""
                INSERT INTO Flights
                (flight_number, departure_date, departure_time, status,
                 origin_airport_code, destination_airport_code)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (flight_number, departure_date, departure_time, status,
                  origin, destination))
            new_id = cursor.lastrowid
        print(f"Flight added successfully (Flight ID {new_id}).")
    except sqlite3.IntegrityError:
        print("Could not add flight. Check that both airport codes exist.")


# ---------------------------------------------------------------------------
# Menu option 2: View flights by criteria (READ)
# ---------------------------------------------------------------------------

def view_flights():
    """SELECT flights, optionally filtered by destination, status and/or date."""
    print("\n=== View Flights ===")
    print("1. All flights")
    print("2. By destination")
    print("3. By status")
    print("4. By departure date")
    print("5. Combine filters (leave a filter blank to skip it)")

    choice = input("Choose a filter: ").strip()

    # WHERE conditions and their values are built up in two parallel lists.
    conditions = []
    parameters = []

    if choice == "2":
        conditions.append("destination_airport_code = ?")
        parameters.append(input("Destination airport code: ").strip().upper())
    elif choice == "3":
        conditions.append("status = ?")
        parameters.append(
            input("Status (Scheduled, Delayed, Cancelled): ").strip().title())
    elif choice == "4":
        conditions.append("departure_date = ?")
        parameters.append(input("Departure date (YYYY-MM-DD): ").strip())
    elif choice == "5":
        destination = input("Destination airport code (blank to skip): ")
        status = input("Status (blank to skip): ")
        date = input("Departure date YYYY-MM-DD (blank to skip): ")
        if destination.strip():
            conditions.append("destination_airport_code = ?")
            parameters.append(destination.strip().upper())
        if status.strip():
            conditions.append("status = ?")
            parameters.append(status.strip().title())
        if date.strip():
            conditions.append("departure_date = ?")
            parameters.append(date.strip())
    elif choice != "1":
        print("Invalid choice.")
        return

    query = """
        SELECT flight_id, flight_number, departure_date, departure_time,
               status, origin_airport_code, destination_airport_code
        FROM Flights
    """
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY departure_date, departure_time"

    with database() as connection:
        rows = connection.execute(query, parameters).fetchall()

    show_table(["ID", "Flight", "Date", "Time", "Status", "Origin", "Dest"], rows)


# ---------------------------------------------------------------------------
# Menu option 3: Update flight information (UPDATE)
# ---------------------------------------------------------------------------

def update_flight():
    """UPDATE the date, time or status of one flight, identified by Flight ID.

    Flight ID is used (not flight number) because the same flight number can
    run on several dates, and a number-based update would change all of them.
    """
    print("\n=== Update Flight ===")
    print("(Use option 2 to look up a Flight ID.)")
    flight_id = ask_int("Flight ID to update: ")
    if flight_id is None:
        return

    print("1. Change departure date")
    print("2. Change departure time")
    print("3. Change status")
    choice = input("Choose what to update: ").strip()

    # Maps the menu choice to the column name and the input prompt.
    fields = {
        "1": ("departure_date", "New departure date (YYYY-MM-DD): "),
        "2": ("departure_time", "New departure time (HH:MM): "),
        "3": ("status", "New status (Scheduled, Delayed, Cancelled): "),
    }

    if choice not in fields:
        print("Invalid choice.")
        return

    column, prompt = fields[choice]
    value = input(prompt).strip()

    if not value:
        print("A value is required.")
        return
    if column == "departure_date" and not valid_date(value):
        print("Invalid date. Use the format YYYY-MM-DD.")
        return
    if column == "departure_time" and not valid_time(value):
        print("Invalid time. Use the 24-hour format HH:MM.")
        return
    if column == "status":
        value = value.title()
        if value not in VALID_STATUSES:
            print("Invalid status.")
            return

    with database() as connection:
        # The column name comes from the fixed dictionary above (never from
        # user text), so building it into the query string is safe.
        cursor = connection.execute(
            f"UPDATE Flights SET {column} = ? WHERE flight_id = ?",
            (value, flight_id)
        )
        updated = cursor.rowcount

    print("Flight updated successfully." if updated else "Flight not found.")


# ---------------------------------------------------------------------------
# Menu option 4: Assign a pilot to a flight (CREATE)
# ---------------------------------------------------------------------------

def assign_pilot():
    """INSERT a row into Flight_Pilot_Assignments after checking it is valid."""
    print("\n=== Assign Pilot to Flight ===")
    print("(Use option 2 for Flight IDs and option 10 for Pilot IDs.)")
    flight_id = ask_int("Flight ID: ")
    if flight_id is None:
        return
    pilot_id = ask_int("Pilot ID: ")
    if pilot_id is None:
        return

    with database() as connection:
        # Check the flight exists and get its departure time.
        flight = connection.execute("""
            SELECT departure_date, departure_time
            FROM Flights WHERE flight_id = ?
        """, (flight_id,)).fetchone()
        if flight is None:
            print("Flight not found.")
            return

        # Check the pilot exists.
        pilot = connection.execute(
            "SELECT 1 FROM Pilots WHERE pilot_id = ?", (pilot_id,)
        ).fetchone()
        if pilot is None:
            print("Pilot not found.")
            return

        # Check this pilot isn't already assigned to this flight.
        existing = connection.execute("""
            SELECT 1 FROM Flight_Pilot_Assignments
            WHERE flight_id = ? AND pilot_id = ?
        """, (flight_id, pilot_id)).fetchone()
        if existing:
            print("This pilot is already assigned to this flight.")
            return

        # Prevent double-booking: same pilot, same date and departure time.
        clash = connection.execute("""
            SELECT f.flight_number
            FROM Flights AS f
            JOIN Flight_Pilot_Assignments AS a ON f.flight_id = a.flight_id
            WHERE a.pilot_id = ?
              AND f.departure_date = ?
              AND f.departure_time = ?
        """, (pilot_id, flight[0], flight[1])).fetchone()
        if clash:
            print(f"Pilot is already assigned to flight {clash[0]} "
                  "at the same date and time.")
            return

        connection.execute("""
            INSERT INTO Flight_Pilot_Assignments (flight_id, pilot_id)
            VALUES (?, ?)
        """, (flight_id, pilot_id))

    print("Pilot assigned successfully.")


# ---------------------------------------------------------------------------
# Menu option 5: View a pilot's schedule (READ with JOIN)
# ---------------------------------------------------------------------------

def view_pilot_schedule():
    """Show all flights assigned to one pilot, in date and time order."""
    print("\n=== View Pilot Schedule ===")
    pilot_id = ask_int("Pilot ID: ")
    if pilot_id is None:
        return

    with database() as connection:
        pilot = connection.execute("""
            SELECT first_name, last_name
            FROM Pilots WHERE pilot_id = ?
        """, (pilot_id,)).fetchone()

        if pilot is None:
            print("Pilot not found.")
            return

        # JOIN links each assignment to its flight details.
        rows = connection.execute("""
            SELECT f.flight_id, f.flight_number, f.departure_date,
                   f.departure_time, f.status,
                   f.origin_airport_code, f.destination_airport_code
            FROM Flights AS f
            JOIN Flight_Pilot_Assignments AS a
                ON f.flight_id = a.flight_id
            WHERE a.pilot_id = ?
            ORDER BY f.departure_date, f.departure_time
        """, (pilot_id,)).fetchall()

    print(f"Schedule for {pilot[0]} {pilot[1]}:")
    show_table(["ID", "Flight", "Date", "Time", "Status", "Origin", "Dest"], rows)


# ---------------------------------------------------------------------------
# Menu option 6: View / update airport (destination) information
# ---------------------------------------------------------------------------

def manage_airports():
    """View all airports, view one airport, or UPDATE an airport's details."""
    print("\n=== Airport Information ===")
    print("1. View all airports")
    print("2. View one airport")
    print("3. Update airport information")
    choice = input("Choose an option: ").strip()
    headers = ["Code", "Name", "City", "Country"]

    with database() as connection:
        if choice == "1":
            rows = connection.execute("""
                SELECT airport_code, airport_name, city, country
                FROM Airports ORDER BY airport_code
            """).fetchall()
            show_table(headers, rows)

        elif choice == "2":
            code = input("Airport code: ").strip().upper()
            rows = connection.execute("""
                SELECT airport_code, airport_name, city, country
                FROM Airports WHERE airport_code = ?
            """, (code,)).fetchall()
            show_table(headers, rows)

        elif choice == "3":
            code = input("Airport code to update: ").strip().upper()
            print("1. Airport name")
            print("2. City")
            print("3. Country")
            field_choice = input("Choose a field: ").strip()

            # Fixed mapping from menu choice to column name.
            fields = {"1": "airport_name", "2": "city", "3": "country"}

            if field_choice not in fields:
                print("Invalid choice.")
                return

            value = input("New value: ").strip()
            if not value:
                print("A value is required.")
                return

            cursor = connection.execute(
                f"UPDATE Airports SET {fields[field_choice]} = ? "
                "WHERE airport_code = ?",
                (value, code)
            )
            if cursor.rowcount:
                print("Airport updated successfully.")
            else:
                print("Airport not found.")
        else:
            print("Invalid choice.")


# ---------------------------------------------------------------------------
# Menu option 7: Summary statistics (aggregate queries)
# ---------------------------------------------------------------------------

def view_statistics():
    """Run three summary queries using GROUP BY and COUNT."""
    print("\n=== Flight Statistics ===")

    with database() as connection:
        # LEFT JOIN keeps airports that have no flights (count of 0).
        print("\nNumber of flights by destination:")
        rows = connection.execute("""
            SELECT a.airport_code, a.airport_name, a.city,
                   COUNT(f.flight_id)
            FROM Airports AS a
            LEFT JOIN Flights AS f
                ON a.airport_code = f.destination_airport_code
            GROUP BY a.airport_code, a.airport_name, a.city
            ORDER BY COUNT(f.flight_id) DESC, a.airport_code
        """).fetchall()
        show_table(["Code", "Airport", "City", "Flights"], rows)

        # LEFT JOIN keeps pilots with no assignments.
        print("\nNumber of flights assigned to each pilot:")
        rows = connection.execute("""
            SELECT p.pilot_id, p.first_name, p.last_name,
                   COUNT(a.flight_id)
            FROM Pilots AS p
            LEFT JOIN Flight_Pilot_Assignments AS a
                ON p.pilot_id = a.pilot_id
            GROUP BY p.pilot_id, p.first_name, p.last_name
            ORDER BY p.pilot_id
        """).fetchall()
        show_table(["Pilot ID", "First name", "Last name", "Flights"], rows)

        print("\nNumber of flights by status:")
        rows = connection.execute("""
            SELECT status, COUNT(*)
            FROM Flights
            GROUP BY status
            ORDER BY COUNT(*) DESC
        """).fetchall()
        show_table(["Status", "Flights"], rows)


# ---------------------------------------------------------------------------
# Menu option 8: Delete a flight (DELETE)
# ---------------------------------------------------------------------------

def delete_flight():
    """DELETE a flight and its pilot assignments, after confirmation.

    Assignments must be removed first because Flight_Pilot_Assignments has a
    foreign key to Flights. Both deletes happen in one transaction, so either
    both succeed or neither does.
    """
    print("\n=== Delete a Flight ===")
    print("(Use option 2 to look up a Flight ID.)")
    flight_id = ask_int("Flight ID to delete: ")
    if flight_id is None:
        return

    with database() as connection:
        flight = connection.execute("""
            SELECT flight_number, departure_date, departure_time
            FROM Flights WHERE flight_id = ?
        """, (flight_id,)).fetchone()
        if flight is None:
            print("Flight not found.")
            return

        pilot_count = connection.execute("""
            SELECT COUNT(*) FROM Flight_Pilot_Assignments WHERE flight_id = ?
        """, (flight_id,)).fetchone()[0]

        print(f"Flight {flight[0]} on {flight[1]} at {flight[2]} "
              f"has {pilot_count} pilot assignment(s).")
        confirm = input("Delete this flight and its assignments? (y/n): ")
        if confirm.strip().lower() != "y":
            print("Deletion cancelled.")
            return

        connection.execute(
            "DELETE FROM Flight_Pilot_Assignments WHERE flight_id = ?",
            (flight_id,))
        connection.execute(
            "DELETE FROM Flights WHERE flight_id = ?", (flight_id,))

    print("Flight deleted successfully.")


# ---------------------------------------------------------------------------
# Menu option 9: Remove a pilot from a flight (DELETE)
# ---------------------------------------------------------------------------

def remove_pilot_assignment():
    """DELETE one row from Flight_Pilot_Assignments (unassign a pilot)."""
    print("\n=== Remove Pilot from Flight ===")
    flight_id = ask_int("Flight ID: ")
    if flight_id is None:
        return
    pilot_id = ask_int("Pilot ID: ")
    if pilot_id is None:
        return

    with database() as connection:
        cursor = connection.execute("""
            DELETE FROM Flight_Pilot_Assignments
            WHERE flight_id = ? AND pilot_id = ?
        """, (flight_id, pilot_id))
        removed = cursor.rowcount

    if removed:
        print("Pilot removed from flight.")
    else:
        print("No such assignment found.")


# ---------------------------------------------------------------------------
# Menu option 10: View all pilots (READ)
# ---------------------------------------------------------------------------

def view_pilots():
    """List every pilot so staff can find the Pilot ID they need."""
    print("\n=== All Pilots ===")
    with database() as connection:
        rows = connection.execute("""
            SELECT pilot_id, first_name, last_name, licence_number
            FROM Pilots ORDER BY pilot_id
        """).fetchall()
    show_table(["Pilot ID", "First name", "Last name", "Licence"], rows)


# ---------------------------------------------------------------------------
# Main program loop
# ---------------------------------------------------------------------------

def main():
    """Check the database exists, then show the menu until the user exits."""
    if not database_ready():
        print(f"Database not found or incomplete. "
              f"Please run:  python {SETUP_SCRIPT}")
        return

    # Maps each menu choice to the function that handles it.
    actions = {
        "1": add_flight,
        "2": view_flights,
        "3": update_flight,
        "4": assign_pilot,
        "5": view_pilot_schedule,
        "6": manage_airports,
        "7": view_statistics,
        "8": delete_flight,
        "9": remove_pilot_assignment,
        "10": view_pilots,
    }

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            try:
                action()
            except sqlite3.Error as error:
                print("A database error occurred:", error)
        else:
            print("Invalid choice. Please enter a number from 0 to 10.")


if __name__ == "__main__":
    main()
