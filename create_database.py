
import sqlite3


def create_database():
    # Connect to the database file.
    # SQLite creates the file automatically if it doesn't exist.
    connection = sqlite3.connect("flight_management.db")

    # Enable foreign key checking.
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    # Table 1: Pilots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pilots (
            pilot_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            licence_number TEXT NOT NULL UNIQUE
        )
    """)

    # Table 2: Airports
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Airports (
            airport_code TEXT PRIMARY KEY,
            airport_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)

    # Table 3: Flights
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Flights (
            flight_id INTEGER PRIMARY KEY,
            flight_number TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            status TEXT NOT NULL,
            origin_airport_code TEXT NOT NULL,
            destination_airport_code TEXT NOT NULL,
            FOREIGN KEY (origin_airport_code)
                REFERENCES Airports(airport_code),
            FOREIGN KEY (destination_airport_code)
                REFERENCES Airports(airport_code)
        )
    """)

    # Table 4: Flight Pilot Assignments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Flight_Pilot_Assignments (
            flight_id INTEGER NOT NULL,
            pilot_id INTEGER NOT NULL,
            PRIMARY KEY (flight_id, pilot_id),
            FOREIGN KEY (flight_id)
                REFERENCES Flights(flight_id),
            FOREIGN KEY (pilot_id)
                REFERENCES Pilots(pilot_id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database and tables created successfully!")



def add_sample_pilots():
    connection = sqlite3.connect("flight_management.db")
    cursor = connection.cursor()

    pilots = [
    (1, "Amelia", "Carter", "LIC1001"),
    (2, "James", "Wilson", "LIC1002"),
    (3, "Sofia", "Patel", "LIC1003"),
    (4, "Oliver", "Brown", "LIC1004"),
    (5, "Grace", "Taylor", "LIC1005"),
    (6, "Noah", "Davies", "LIC1006"),
    (7, "Isabella", "Evans", "LIC1007"),
    (8, "Ethan", "Thomas", "LIC1008"),
    (9, "Mia", "Roberts", "LIC1009"),
    (10, "Leo", "Walker", "LIC1010"),
    (11, "Harriet", "Cole", "LIC1011"),
    (12, "Samuel", "Okafor", "LIC1012"),
    (13, "Priya", "Nair", "LIC1013"),
    (14, "Lucas", "Fischer", "LIC1014"),
    (15, "Chloe", "Bennett", "LIC1015"),
]

    cursor.executemany("""
        INSERT OR IGNORE INTO Pilots
        (pilot_id, first_name, last_name, licence_number)
        VALUES (?, ?, ?, ?)
    """, pilots)

    connection.commit()
    connection.close()

    print("Sample pilots added successfully!")


def add_sample_airports():
    connection = sqlite3.connect("flight_management.db")
    cursor = connection.cursor()

    airports = [
    ("LHR", "Heathrow Airport", "London", "United Kingdom"),
    ("MAN", "Manchester Airport", "Manchester", "United Kingdom"),
    ("JFK", "John F. Kennedy International Airport", "New York", "United States"),
    ("EDI", "Edinburgh Airport", "Edinburgh", "United Kingdom"),
    ("CDG", "Charles de Gaulle Airport", "Paris", "France"),
    ("AMS", "Amsterdam Airport Schiphol", "Amsterdam", "Netherlands"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
    ("MAD", "Adolfo Suarez Madrid-Barajas Airport", "Madrid", "Spain"),
    ("DUB", "Dublin Airport", "Dublin", "Ireland"),
    ("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates"),
    ("FCO", "Leonardo da Vinci-Fiumicino Airport", "Rome", "Italy"),
    ("SIN", "Changi Airport", "Singapore", "Singapore"),
    ("BCN", "Josep Tarradellas Barcelona-El Prat Airport", "Barcelona", "Spain"),
    ("ZRH", "Zurich Airport", "Zurich", "Switzerland"),
    ("LIS", "Humberto Delgado Airport", "Lisbon", "Portugal"),
]

    cursor.executemany("""
        INSERT OR IGNORE INTO Airports
        (airport_code, airport_name, city, country)
        VALUES (?, ?, ?, ?)
    """, airports)

    connection.commit()
    connection.close()

    print("Sample airports added successfully!")


def add_sample_flights():
    connection = sqlite3.connect("flight_management.db")
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    flights = [
    (1, "BA101", "2026-10-15", "08:30", "Scheduled", "LHR", "JFK"),
    (2, "BA102", "2026-10-15", "12:00", "Scheduled", "JFK", "LHR"),
    (3, "BA205", "2026-10-16", "09:15", "Delayed", "LHR", "MAN"),
    (4, "BA206", "2026-10-16", "14:45", "Scheduled", "MAN", "LHR"),
    (5, "BA310", "2026-10-17", "17:20", "Cancelled", "LHR", "JFK"),
    (6, "BA401", "2026-10-18", "07:00", "Scheduled", "EDI", "CDG"),
    (7, "BA402", "2026-10-18", "11:30", "Scheduled", "CDG", "EDI"),
    (8, "BA501", "2026-10-19", "10:15", "Delayed", "AMS", "FRA"),
    (9, "BA601", "2026-10-20", "16:00", "Scheduled", "MAD", "DUB"),
    (10, "BA701", "2026-10-21", "21:10", "Scheduled", "DXB", "LHR"),
    (11, "BA801", "2026-10-22", "09:00", "Scheduled", "LHR", "FCO"),
    (12, "BA802", "2026-10-22", "13:30", "Scheduled", "FCO", "LHR"),
    (13, "BA901", "2026-10-23", "06:45", "Delayed", "LHR", "SIN"),
    (14, "BA902", "2026-10-24", "15:10", "Scheduled", "BCN", "MAN"),
    (15, "BA950", "2026-10-25", "19:40", "Cancelled", "ZRH", "LIS"),
]

    cursor.executemany("""
        INSERT OR IGNORE INTO Flights
        (flight_id, flight_number, departure_date, departure_time,
         status, origin_airport_code, destination_airport_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, flights)

    connection.commit()
    connection.close()

    print("Sample flights added successfully!")


def add_sample_assignments():
    connection = sqlite3.connect("flight_management.db")
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    assignments = [
    (1, 1), (1, 2),
    (2, 3), (2, 4),
    (3, 1), (3, 5),
    (4, 2), (4, 3),
    (5, 4), (5, 5),
    (6, 6), (6, 7),
    (7, 6),
    (8, 8), (8, 9),
    (9, 10), (9, 7),
    (10, 9), (10, 10),
    (11, 11), (11, 12),
    (12, 13),
    (13, 14), (13, 15),
    (14, 11),
    (15, 12),
]

    cursor.executemany("""
        INSERT OR IGNORE INTO Flight_Pilot_Assignments
        (flight_id, pilot_id)
        VALUES (?, ?)
    """, assignments)

    connection.commit()
    connection.close()

    print("Sample pilot assignments added successfully!")

if __name__ == "__main__":
    create_database()
    add_sample_airports()
    add_sample_pilots()
    add_sample_flights()
    add_sample_assignments()