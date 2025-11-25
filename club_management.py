import tkinter as tk
from tkinter import ttk, messagebox  # Import ttk for the dropdowns
from database import db
from constants import CLUB_OPTIONS, INTEREST_TAGS
from tkcalendar import DateEntry


class ClubManagement(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Club Management", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for the form details
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Create new club
        tk.Button(form_container, text="Create New Club", command=lambda: controller.show_frame("ClubCreation"),
                width=15, bg="#22AA00", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)


 
        # Tags
        tk.Label(self, text="Select Tags & Interests:").pack(anchor='w', padx=20, pady=(10, 0))

        self.club_vars = []
        self.tags_frame = tk.Frame(self)
        self.tags_frame.pack(anchor="w", padx=20, pady=5, fill="x")

        # Grid: 3 columns wide
        
        self.load_and_display_clubs(self.tags_frame)

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Clubs", command=self.update_clubs,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)
        
    def load_and_display_clubs(self, clubs_frame):
        """ This method is to display all the clubs for a user to be a member in.
            It refreshes upon load to include any new clubs that might have been created."""

        clubs = db.get_club_names()

        columns = 7
        for i, tag in enumerate(clubs):
            var = tk.IntVar()
            self.club_vars.append((tag, var))

            # Calculate row and column
            r = i // columns
            c = i % columns

            chk = tk.Checkbutton(clubs_frame, text=tag, variable=var)
            chk.grid(row=r, column=c, sticky="w", padx=10, pady=2)

    def update_clubs(self):

        selected_tags = [tag for tag, var in self.club_vars if var.get() == 1]
        print(f'Email: {self.controller.current_user_email}')
        print(db.get_user_id_by_email(self.controller.current_user_email))

        success = db.update_user_clubs(self.controller.current_user_email, selected_tags)

        if success:
            messagebox.showinfo("Success", f"Club membership updated!")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not post event.")

    def clear_fields(self):
        for _, var in self.club_vars:
            var.set(0)


    def on_show(self):
        self.load_and_display_clubs(self.tags_frame)