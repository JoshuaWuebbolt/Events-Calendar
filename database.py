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
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                         id INTEGER PRIMARY KEY,
                                         name TEXT NOT NULL,
                                         email TEXT UNIQUE NOT NULL,
                                         password TEXT NOT NULL
                                     ); """

        sql_create_events_table = """ CREATE TABLE IF NOT EXISTS events (
                                          id INTEGER PRIMARY KEY,
                                          event_name TEXT NOT NULL,
                                          host_club TEXT NOT NULL,
                                          description TEXT,
                                          time_frame TEXT,
                                          location TEXT
                                      ); """

        sql_create_event_interests_table = """ CREATE TABLE IF NOT EXISTS event_interests ( 
                                            event_id INTEGER, 
                                            interest_tag TEXT  NOT NULL, 
                                            FOREIGN  KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
                                            PRIMARY KEY (event_id,interest_tag)
                                            ); """

        sql_create_user_interests_table = """ CREATE TABLE IF NOT EXISTS user_interests ( 
                                            user_email TEXT, 
                                            interest_tag TEXT  NOT NULL, 
                                            FOREIGN  KEY (user_email) REFERENCES users (email) ON DELETE CASCADE,
                                            PRIMARY KEY (user_email,interest_tag)
                                            ); """

        try:
            c = self.conn.cursor()
            c.execute(sql_create_users_table)
            c.execute(sql_create_events_table)
            c.execute(sql_create_event_interests_table)
            c.execute(sql_create_user_interests_table)
            self.conn.commit()
        except Error as e:
            print(e)

    def register_user(self, name, email, password, interests):
        """Inserts a new user into the database."""
        sql_user = ''' INSERT INTO users(name, email, password) VALUES (?, ?, ?) '''
        try:
            c = self.conn.cursor()
            c.execute(sql_user, (name, email, password))

            # insert interests
            sql_interest = ''' INSERT INTO user_interests(user_email, interest_tag) VALUES (?, ?) '''
            for tags in interests:
                c.execute(sql_interest, (email, tags))

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
        sql = ''' SELECT name FROM users WHERE email = ? AND password = ? '''
        try:
            c = self.conn.cursor()
            c.execute(sql, (email, password))
            # Fetch one result (the user's name)
            user_data = c.fetchone()
            if user_data:
                return user_data[0]  # Return the user's email
            return None
        except Error as e:
            print(e)
            return None

    def get_user_by_email(self, email):
        """Fetches the user's name, email, and interests from the database."""
        sql_user = ''' SELECT name, email FROM users WHERE email = ? '''
        sql_interests = ''' SELECT interest_tag FROM user_interests WHERE user_email = ? '''

        try:
            c = self.conn.cursor()
            c.execute(sql_user, (email,))
            user_data = c.fetchone()

            if user_data:
                # Fetch interests separately
                c.execute(sql_interests, (email,))
                interests = [row[0] for row in c.fetchall()]  # Returns a list of strings
                return (user_data[0], user_data[1], interests)
            return None
        except Error as e:
            print(e)
            return None

    def update_user_profile(self, old_email, new_name, new_email, new_interests_list):
        """Updates the user's profile details and associated interests."""

        sql_update_user = ''' UPDATE users SET name  = ?,
                                               email = ? WHERE email = ? '''

        sql_delete_interests = ''' DELETE  FROM user_interests WHERE user_email = ? '''
        sql_insert_interest = ''' INSERT INTO user_interests(user_email, interest_tag) VALUES (?, ?) '''

        try:
            c = self.conn.cursor()

            # Update basic user data (Name and Email)
            c.execute(sql_update_user, (new_name, new_email, old_email))

            # Delete all old interests for the user
            c.execute(sql_delete_interests, (new_email,))  # Use new_email if changed, else old

            # Insert the new set of interests
            for tag in new_interests_list:
                c.execute(sql_insert_interest, (new_email, tag))

            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # if new email already taken, rollback
            self.conn.rollback()
            return "EmailExists"
        except Error as e:
            print(e)
            return False

    def delete_user_account(self, email):
        """Deletes a user account and their associated data (e.g., events)."""
        sql_delete_user = ''' DELETE 
                              FROM users 
                              WHERE email = ? '''
        # TODO: add DELETE FROM events WHERE user_email = ? for removing events from account
        try:
            c = self.conn.cursor()
            c.execute(sql_delete_user, (email,))
            self.conn.commit()
            return True
        except Error as e:
            print(e)
            return False

    def create_event(self, name, club, description, time, location, tags_list):
        """Inserts a new event listing into the database."""
        sql = ''' INSERT INTO events(event_name, host_club, description, time_frame, 
                                     location)
                  VALUES(?,?,?,?,?) '''

        sql_tag = '''INSERT INTO event_interests(event_id, interest_tag) VALUES(?, ?) '''
        try:
            c = self.conn.cursor()
            c.execute(sql, (name, club, description, time, location))

            new_event_id = c.lastrowid
            for tag in tags_list:
                c.execute(sql_tag, (new_event_id, tag))

            self.conn.commit()
            return True
        except Error as e:
            print(f"Error creating event: {e}")
            return False

    def get_all_events(self):
        """
        Retrieves all events and their associated tags from the database.
        Returns a list of dictionaries.
        """
        sql_events = "SELECT * FROM events"
        sql_tags = "SELECT interest_tag FROM event_interests WHERE event_id = ?"

        events_list = []
        try:
            c = self.conn.cursor()
            c.execute(sql_events)
            rows = c.fetchall()

            # Convert raw tuple rows into a list of dictionaries
            for row in rows:
                event_id = row[0]

                # Fetch tags for this specific event
                c_tag = self.conn.cursor()
                c_tag.execute(sql_tags, (event_id,))
                tags = [t[0] for t in c_tag.fetchall()]

                event_dict = {
                    "id": row[0],
                    "name": row[1],
                    "club": row[2],
                    "description": row[3],
                    "time": row[4],
                    "location": row[5],
                    "tags": tags  # Add the list of tags to the dictionary
                }
                events_list.append(event_dict)

            return events_list

        except Error as e:
            print(e)
            return []

    def get_events_name_by_user_email(self, email: str):
        """
        Need to fully impliment clubs. Once they are this method will only return the events run by clubs that they user is a part of

        Retrieves the names of all events associated with a given email
        Returns a list of event names
        """

        try:
            c = self.conn.cursor()
            # This line will be changed so don't bother making it a variable
            c.execute("""
                SELECT event_name
                FROM events            
            """)
            rows = c.fetchall()

            # convert list of 1-tuples to a list of plain strings
            rows = [str(row[0]) for row in rows]
            # print(f'rows: {rows}')

            return rows
        except Error as e:
            print(e)
            return []
        
    def get_event_data_by_event_name(self, event_name: str):
        sql_event = ''' SELECT event_name, host_club, description, time_frame, location, id FROM events WHERE event_name = ? '''


        try:
            c = self.conn.cursor()
            # This line will be changed so don't bother making it a variable
            c.execute(sql_event, (event_name,))
            event = c.fetchone()
            print(f'The selected event data for {event_name}: {event}')

            return event
        except Error as e:
            print(e)
            return []
        
    def get_tags_by_event_id(self, event_id: str):
        sql_tags = ''' SELECT interest_tag FROM event_interests WHERE event_id = ? '''
        # Fetch all tags for the given event_id and return as a list of strings
        try:
            c = self.conn.cursor()
            c.execute(sql_tags, (event_id,))
            tags = [row[0] for row in c.fetchall()]
            print(f'The selected tag data for {event_id}: {tags}')
            return tags
        except Error as e:
            print(e)
            return []

    def update_event(self, id, event_name, host_club, description, time, location, tags):
        """Update an existing event and its associated tags."""
        sql_update_event = ''' UPDATE events
                       SET event_name = ?,
                       host_club = ?,
                       description = ?,
                       time_frame = ?,
                       location = ?
                       WHERE id = ? '''
        sql_delete_tags = ''' DELETE FROM event_interests WHERE event_id = ? '''
        sql_insert_tag = ''' INSERT INTO event_interests(event_id, interest_tag) VALUES(?, ?) '''

        try:
            c = self.conn.cursor()
            # Update event row
            c.execute(sql_update_event, (event_name, host_club, description, time, location, id))

            # Replace tags: remove old ones, then insert new ones
            c.execute(sql_delete_tags, (id,))
            if tags:
                for tag in tags:
                    c.execute(sql_insert_tag, (id, tag))

            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False
        except Error as e:
            print(e)
            return False
        
db = DBManager()