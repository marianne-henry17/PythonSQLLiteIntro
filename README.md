# Flight Management System

A command-line application for an airline's staff to manage flights, pilots and airports. It is written in Python and stores its data in an SQLite database using the built-in `sqlite3` module.

Staff can add, view, update and delete flights, assign pilots to flights, view a pilot's schedule, view and update airport information, and see summary statistics.

## Requirements

- Python 3
- No extra packages are needed (`sqlite3` is part of Python's standard library)

## How to run

Run these commands from the repository folder (for example in the GitHub Codespaces terminal):

1. Create and fill the database:

   ```
   python create_database.py
   ```

   This creates `flight_management.db` with four tables and sample data (15 airports, 15 pilots, 15 flights and 26 pilot assignments). It is safe to run more than once.

2. Start the application:

   ```
   python main.py
   ```

   If the database is missing, the program tells you to run step 1 first.

A ready-made `flight_management.db` is also included in the repository, so step 2 works straight away.

## Menu options

| Option | What it does |
| --- | --- |
| 1 | Add a new flight |
| 2 | View flights (all, or filtered by destination, status, date, or a combination) |
| 3 | Update a flight's departure date, departure time or status (by Flight ID) |
| 4 | Assign a pilot to a flight |
| 5 | View a pilot's schedule |
| 6 | View all airports, view one airport, or update airport details |
| 7 | View statistics (flights per destination, flights per pilot, flights per status) |
| 8 | Delete a flight (and its pilot assignments) |
| 9 | Remove a pilot from a flight |
| 10 | View all pilots |
| 0 | Exit |

## Database tables

- **Pilots**: `pilot_id` (primary key), `first_name`, `last_name`, `licence_number` (unique)
- **Airports**: `airport_code` (primary key), `airport_name`, `city`, `country`
- **Flights**: `flight_id` (primary key), `flight_number`, `departure_date`, `departure_time`, `status`, `origin_airport_code` and `destination_airport_code` (both foreign keys to Airports)
- **Flight_Pilot_Assignments**: `flight_id` and `pilot_id` together form the primary key, and each is a foreign key. This table links pilots to flights (a many-to-many relationship).

## Files in this repository

- `main.py`: the command-line application and all its SQL queries
- `create_database.py`: creates the tables and inserts the sample data
- `flight_management.db`: the SQLite database
- `README.md`: this file

## Assumptions

- A flight is identified by its Flight ID, because the same flight number can run on different dates.
- A flight's status must be Scheduled, Delayed or Cancelled.
- Dates are stored as text in `YYYY-MM-DD` format and times as text in 24-hour `HH:MM` format, because SQLite has no separate date type.
- A flight's origin and destination must be different airports that already exist in the database.
- A pilot cannot be assigned to two flights with the same departure date and time.
- Deleting a flight also deletes its pilot assignments, after the user confirms.

## AI use

Generative AI (Claude) was used to help write and test the application code and to generate sample data. The design decisions and the final code are my responsibility.
