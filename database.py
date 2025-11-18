import sqlite3
from sqlite3 import Error


class DBManager:
    def __init__(self, db_file="events.db"):
        self.conn = None
        try:
            # Connect to the SQLite database file
            self.conn = sqlite3.connect(db_file)
            self.create_tables()
            print(f"Database connection successful: {db_file}")
        except Error as e:
            print(e)

    def create_tables(self):
        """Creates the necessary tables for the application (Users and Events)."""
        # Note: 'interests' will store a comma-separated string of user preferences
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                         id INTEGER PRIMARY KEY,
                                         name TEXT NOT NULL,
                                         email TEXT UNIQUE NOT NULL,
                                         password TEXT NOT NULL,
                                         interests TEXT
                                     ); """

        # We will add the events table later when we implement the "Create Event" window.
        sql_create_events_table = """ CREATE TABLE IF NOT EXISTS events (
                                          id INTEGER PRIMARY KEY,
                                          event_name TEXT NOT NULL,
                                          host_club TEXT NOT NULL,
                                          description TEXT,
                                          time_frame TEXT,
                                          free_food INTEGER, -- 1 for True, 0 for False
                                          paid INTEGER  -- 1 for True, 0 for False
                                      ); """

        try:
            c = self.conn.cursor()
            c.execute(sql_create_users_table)
            c.execute(sql_create_events_table)
            self.conn.commit()
        except Error as e:
            print(e)

    def register_user(self, name, email, password, interests):
        """Inserts a new user into the database."""
        sql = ''' INSERT INTO users(name, email, password, interests)
                  VALUES (?, ?, ?, ?) '''
        try:
            c = self.conn.cursor()
            c.execute(sql, (name, email, password, interests))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # This handles the case where the email already exists (UNIQUE constraint)
            return False
        except Error as e:
            print(e)
            return False

    def check_credentials(self, email, password):
        """Checks if the email and password combination is valid."""
        sql = ''' SELECT name
                  FROM users
                  WHERE email = ?
                    AND password = ? '''
        try:
            c = self.conn.cursor()
            c.execute(sql, (email, password))
            # Fetch one result (the user's name)
            user_data = c.fetchone()
            if user_data:
                return user_data[0]  # Return the user's name
            return None
        except Error as e:
            print(e)
            return None

db = DBManager()