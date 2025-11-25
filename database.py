import sqlite3
from sqlite3 import Error
import bcrypt


class DBManager:
    def __init__(self, db_file="events.db"):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            # Enable Foreign Keys enforcement for ON UPDATE CASCADE to work.
            self.conn.execute("PRAGMA foreign_keys = 1")
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
                                          host_club TEXT,
                                          description TEXT,
                                          time_frame TEXT,
                                          location TEXT,
                                          FOREIGN KEY (host_club) REFERENCES clubs (club_name) ON DELETE CASCADE ON UPDATE CASCADE
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
                                            FOREIGN  KEY (user_email) REFERENCES users (email) ON DELETE CASCADE ON UPDATE CASCADE,
                                            PRIMARY KEY (user_email,interest_tag)
                                            ); """

        sql_create_clubs_table = """CREATE TABLE IF NOT EXISTS clubs (
                                    id INTEGER PRIMARY KEY,
                                    club_name TEXT UNIQUE NOT NULL,   
                                    club_email TEXT NOT NULL,   
                                    club_description TEXT                            
                                    );"""

        sql_create_user_clubs_table = """ CREATE TABLE IF NOT EXISTS user_clubs ( 
                                    user_email TEXT, 
                                    club TEXT  NOT NULL, 
                                    role TEXT DEFAULT 'member',
                                    FOREIGN  KEY (user_email) REFERENCES users (email) ON DELETE CASCADE ON UPDATE CASCADE, 
                                    PRIMARY KEY (user_email,club)
                                    ); """ # if User changes their email in the 'users' table,  it automatically updates in clubs too.
        try:
            c = self.conn.cursor()
            c.execute(sql_create_clubs_table)
            c.execute(sql_create_users_table)
            c.execute(sql_create_events_table)
            c.execute(sql_create_event_interests_table)
            c.execute(sql_create_user_interests_table)
            c.execute(sql_create_user_clubs_table)
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
        """Checks if the email and password combination is valid using bcrypt."""
        sql = ''' SELECT name, password FROM users WHERE email = ? '''
        try:
            c = self.conn.cursor()
            c.execute(sql, (email,))
            row = c.fetchone()
            if not row:
                return None

            name, stored_hash = row[0], row[1]

            # Compare provided password with the stored bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return name
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
        """
        Deletes a user account.
        Logic:
        1. If user is the LAST Admin -> Delete Club.
        2. If user is NOT the last Admin but is the Contact Person -> Transfer Contact to another Admin.
        """
        sql_delete_user = "DELETE FROM users WHERE email = ?"

        try:
            c = self.conn.cursor()

            # Find clubs where this user is an 'admin'
            c.execute("SELECT club FROM user_clubs WHERE user_email = ? AND role = 'admin'", (email,))
            admin_clubs = [row[0] for row in c.fetchall()]

            for club_name in admin_clubs:
                # Count total admins
                c.execute("SELECT count(*) FROM user_clubs WHERE club = ? AND role = 'admin'", (club_name,))
                admin_count = c.fetchone()[0]

                if admin_count == 1:
                    # Case A: User is the LAST/ONLY Admin.
                    # Delete the entire club (cascades to events).
                    print(f"User is last admin of {club_name}. Deleting club.")
                    c.execute("DELETE FROM clubs WHERE club_name = ?", (club_name,))

                else:
                    # Case B: There are other admins remaining.
                    # Check if the deleting user is the registered 'club_email'
                    c.execute("SELECT club_email FROM clubs WHERE club_name = ?", (club_name,))
                    current_club_email = c.fetchone()[0]

                    if current_club_email == email:
                        # The contact person is leaving so transfer this responsibility
                        # Find another admin
                        c.execute(
                            "SELECT user_email FROM user_clubs WHERE club = ? AND role = 'admin' AND user_email != ?",
                            (club_name, email))
                        new_admin_email = c.fetchone()[0]

                        print(f"Transferring ownership of {club_name} to {new_admin_email}")
                        c.execute("UPDATE clubs SET club_email = ? WHERE club_name = ?", (new_admin_email, club_name))

            # Finally delete the user account
            c.execute(sql_delete_user, (email,))

            self.conn.commit()
            return True
        except Error as e:
            print(f"Error deleting account: {e}")
            self.conn.rollback()
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

    def create_club(self, name, email, description, creator_email):
        sql_club = ''' INSERT INTO clubs(club_name, club_email, club_description) \
                       VALUES (?, ?, ?) '''

        # Automatically make the creator an ADMIN
        sql_admin = ''' INSERT INTO user_clubs(user_email, club, role) \
                        VALUES (?, ?, 'admin') '''

        try:
            c = self.conn.cursor()
            # Create Club
            c.execute(sql_club, (name, email, description))
            # Assign Creator as Admin
            c.execute(sql_admin, (creator_email, name))

            self.conn.commit()
            return True
        except Error as e:
            print(f'Error creating club: {e}')
            self.conn.rollback()
            return False




    def get_all_events(self):
        """
        Retrieves all events and their associated tags from the database.
        Returns a list of dictionaries.
        """
        sql_events = "SELECT * FROM events ORDER BY time_frame"
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
        # get the clubs user is in
        clubs = self.get_user_clubs(email)

        if not clubs:
            return []

        # find events hosted by these clubs
        placeholders = ",".join("?" for _ in clubs)
        sql = f"SELECT event_name FROM events WHERE host_club IN ({placeholders})"

        try:
            c = self.conn.cursor()
            c.execute(sql, clubs)
            rows = c.fetchall()

            # Flatten to list of strings
            return [str(row[0]) for row in rows]
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
        """Get all tags associated with a given event id"""
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

    def delete_event(self, event_id):
        """Deletes an event by ID."""
        sql = "DELETE FROM events WHERE id = ?"
        try:
            c = self.conn.cursor()
            c.execute(sql, (event_id,))
            self.conn.commit()
            return True
        except Error as e:
            print(f"Error deleting event: {e}")
            return False

    def get_events_by_user(self):
        pass

    def get_club_names(self):
        """Get a list of all club names."""
        sql_events = "SELECT club_name FROM clubs ORDER BY club_name"

        try:
            c = self.conn.cursor()
            c.execute(sql_events)
            rows = c.fetchall()
            rows = [str(row[0]) for row in rows]
            return rows
        except Error as e:
            print(e)
            return False

    def update_user_clubs(self, user_email, new_club_list):
        """
        Updates user club memberships but PRESERVES existing roles (like 'admin').
        """
        try:
            c = self.conn.cursor()

            # Get current clubs and roles: {'Robotics': 'admin', 'Chess': 'member'}
            c.execute("SELECT club, role FROM user_clubs WHERE user_email = ?", (user_email,))
            current_data = {row[0]: row[1] for row in c.fetchall()}
            current_clubs = set(current_data.keys())
            new_clubs_set = set(new_club_list)

            # Calculate what to add and what to remove
            to_add = new_clubs_set - current_clubs
            to_remove = current_clubs - new_clubs_set

            for club in to_remove:
                if current_data.get(club) == 'admin':
                    # Stop everything. Do not delete.
                    return "AdminConstraint"

            # Remove clubs user 
            for club in to_remove:
                c.execute("DELETE FROM user_clubs WHERE user_email = ? AND club = ?", (user_email, club))

            # Add new clubs (default to 'member')
            for club in to_add:
                c.execute("INSERT INTO user_clubs (user_email, club, role) VALUES (?, ?, 'member')", (user_email, club))

            self.conn.commit()
            return True
        except Error as e:
            print(e)
            self.conn.rollback()
            return False

    def is_club_admin(self, user_email, club_name):
        """Checks if the user is an admin of the club."""
        sql = "SELECT role FROM user_clubs WHERE user_email = ? AND club = ?"
        try:
            c = self.conn.cursor()
            c.execute(sql, (user_email, club_name))
            result = c.fetchone()
            if result and result[0] == 'admin':
                return True
            return False
        except Error as e:
            print(e)
            return False

    def get_user_clubs(self, email):
        """Gets user clubs for a given email."""
        sql_tags = ''' SELECT club FROM user_clubs WHERE user_email = ? '''
        print(f'searching with email: {email}')
        try:
            c = self.conn.cursor()
            c.execute(sql_tags, (email,))
            rows = c.fetchall()
            clubs = [row[0] for row in rows] # flatten list of tuples
            return clubs
        except Error as e:
            print(e)
            return []

    def get_user_id_by_email(self, email):
        sql_user = ''' SELECT id FROM users WHERE email = ?'''

        try:
            c = self.conn.cursor()
            c.execute(sql_user, (email))
            user_id =  c.fetchall()[0][0]
            return user_id
        except Error as e:
            print(e)
            return []

    def get_events_by_clubs(self, clubs):
        """Gets events associated with a given club."""
        # Return empty list if no clubs provided
        if not clubs:
            return []

        # Allow passing a single club as a string
        if isinstance(clubs, str):
            clubs = [clubs]

        placeholders = ",".join("?" for _ in clubs)
        sql = f"SELECT event_name, time_frame, location, host_club FROM events WHERE host_club IN ({placeholders}) ORDER BY time_frame"

        try:
            c = self.conn.cursor()
            # ensure clubs is a flat list of strings (convert from [(name,), ...] to [name, ...])
            if clubs and isinstance(clubs[0], (tuple, list)):
                clubs = [c[0] for c in clubs]
            c.execute(sql, clubs)
            rows = c.fetchall()

            # Return a list of dictionaries, not just strings
            events_data = []
            for row in rows:
                events_data.append({
                    "name": row[0],
                    "time": row[1],
                    "location": row[2],
                    "club": row[3]
                })
            return events_data
        except Error as e:
            print(e)
            return []

    def get_events_by_user_email(self, email):
        """Get events associated with a given email."""
        clubs = self.get_user_clubs(email)
        events = self.get_events_by_clubs(clubs)
        print(f'event from {email}. clubs: {clubs} and events: {events}')
        return events




db = DBManager()