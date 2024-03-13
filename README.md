# pagehit_db
Flask SQLite database service

## Description
This project is a SQLite database service that tracks page hits from multiple websites. Users can add page hits by sending JSON data to the `/create` API endpoint. Additionally, there is an `/admin` login page available to access the SQL query web interface for managing and querying the database records.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   ```
2. Install the required dependencies:
   ```bash
   pip install flask sqlalchemy python-dotenv
   ```

## Usage
To run the Flask app:
```bash
python main.py
```

## Files
- [`main.py`](./main.py): contains the Flask app with routes for creating page hits and executing SQL queries, as well as admin login and logout functionality.
- [`database.py`](./database.py): contains the SQLAlchemy model for the `PageHit` table and functions for initializing the database, validating data, adding data, and querying the database.

## License
This project is licensed under the [MIT License](LICENSE).