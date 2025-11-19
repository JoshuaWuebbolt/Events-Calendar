import tkinter as tk
from tkinter import messagebox
from database import db
from constants import CLUB_OPTIONS


class EventCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Create New Event Listing", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for the form details
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")

        # two-column layout
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Event Details
        # name
        tk.Label(form_container, text="Event Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # club
        tk.Label(form_container, text="Host Club:", anchor="e").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        clubs = CLUB_OPTIONS
        self.club_var = tk.StringVar(self)
        self.club_var.set(clubs[0])  # Default value
        self.club_menu = tk.OptionMenu(form_container, self.club_var, *clubs)
        self.club_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # time period
        tk.Label(form_container, text="Date/Time Frame (e.g., Nov 25, 6-8 PM):", anchor="e").grid(row=2, column=0,
                                                                                                  sticky="ew", padx=5,
                                                                                                  pady=5)
        self.time_entry = tk.Entry(form_container)
        self.time_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # location
        tk.Label(form_container, text="Location:", anchor="e").grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.location_entry = tk.Entry(form_container)
        self.location_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # description
        tk.Label(form_container, text="Description:", anchor="e").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.description_text = tk.Text(form_container, height=4, width=40)
        self.description_text.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # checkbox option
        options_frame = tk.Frame(self)
        options_frame.pack(pady=15)

        self.free_food_var = tk.IntVar()
        tk.Checkbutton(options_frame, text="Free Food Provided", variable=self.free_food_var).pack(side="left", padx=10)

        self.paid_var = tk.IntVar()
        tk.Checkbutton(options_frame, text="Paid Event ($)", variable=self.paid_var).pack(side="left", padx=10)

        self.reg_req_var = tk.IntVar()
        tk.Checkbutton(options_frame, text="Registration Required", variable=self.reg_req_var).pack(side="left",
                                                                                                    padx=10)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Post Event", command=self.post_event, width=15, bg="#0066AA", fg="white").pack(
            side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"), width=15).pack(
            side="left", padx=10)

    def post_event(self):
        """Validates input and submits the event to the database."""
        name = self.name_entry.get()
        club = self.club_var.get()
        time = self.time_entry.get()
        location = self.location_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        # Convert checkbox variables to 1 (True) or 0 (False) for database
        free_food = self.free_food_var.get()
        paid = self.paid_var.get()
        reg_req = self.reg_req_var.get()

        if not name or not club or not time or not location:
            messagebox.showerror("Missing Info", "Please fill in Event Name, Club, Time, and Location.")
            return

        success = db.create_event(name, club, description, time, location, reg_req, free_food, paid)

        if success:
            messagebox.showinfo("Success", f"Event '{name}' successfully posted by {club}!")
            # Clear fields and return to calendar
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not post event. Check database connection/inputs.")

    def clear_fields(self):
        """Clears all input fields after successful submission."""
        self.name_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.free_food_var.set(0)
        self.paid_var.set(0)
        self.reg_req_var.set(0)
        # Note: club_var keeps its default state