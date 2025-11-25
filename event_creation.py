import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from constants import INTEREST_TAGS
from tkcalendar import DateEntry
from datetime import date


class EventCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Create New Event Listing", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for the form details
        self.form_container = tk.Frame(self)
        self.form_container.pack(padx=20, pady=10, fill="x")
        self.form_container.columnconfigure(0, weight=1)
        self.form_container.columnconfigure(1, weight=3)

        # Initialize Static Widgets (Labels, Entries)

        # Name
        tk.Label(self.form_container, text="Event Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(self.form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Club (initialize it empty, populate it later)
        tk.Label(self.form_container, text="Host Club:", anchor="e").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.club_var = tk.StringVar(self)
        self.club_menu = tk.OptionMenu(self.form_container, self.club_var, "")  # Empty start
        self.club_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Date
        tk.Label(self.form_container, text="Date:", anchor="e").grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.date_picker = DateEntry(self.form_container, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Start Time
        tk.Label(self.form_container, text="Start Time:", anchor="e").grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        start_frame = tk.Frame(self.form_container)
        start_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.start_hour = ttk.Combobox(start_frame, values=[str(i) for i in range(1, 13)], width=3, state="readonly")
        self.start_hour.set("6")
        self.start_hour.pack(side="left")

        tk.Label(start_frame, text=":").pack(side="left")

        self.start_min = ttk.Combobox(start_frame, values=["00", "15", "30", "45"], width=3, state="readonly")
        self.start_min.set("00")
        self.start_min.pack(side="left")

        self.start_ampm = ttk.Combobox(start_frame, values=["AM", "PM"], width=3, state="readonly")
        self.start_ampm.set("PM")
        self.start_ampm.pack(side="left", padx=5)

        # End Time
        tk.Label(self.form_container, text="End Time:", anchor="e").grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        end_frame = tk.Frame(self.form_container)
        end_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.end_hour = ttk.Combobox(end_frame, values=[str(i) for i in range(1, 13)], width=3, state="readonly")
        self.end_hour.set("8")
        self.end_hour.pack(side="left")

        tk.Label(end_frame, text=":").pack(side="left")

        self.end_min = ttk.Combobox(end_frame, values=["00", "15", "30", "45"], width=3, state="readonly")
        self.end_min.set("00")
        self.end_min.pack(side="left")

        self.end_ampm = ttk.Combobox(end_frame, values=["AM", "PM"], width=3, state="readonly")
        self.end_ampm.set("PM")
        self.end_ampm.pack(side="left", padx=5)

        # Location
        tk.Label(self.form_container, text="Location:", anchor="e").grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.location_entry = tk.Entry(self.form_container)
        self.location_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Description
        tk.Label(self.form_container, text="Description:", anchor="e").grid(row=6, column=0, sticky="ne", padx=5,
                                                                            pady=5)
        self.description_text = tk.Text(self.form_container, height=4, width=40)
        self.description_text.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        # Tags
        tk.Label(self, text="Select Tags & Interests:").pack(anchor='w', padx=20, pady=(10, 0))
        self.tag_vars = []
        tags_frame = tk.Frame(self)
        tags_frame.pack(anchor="w", padx=20, pady=5, fill="x")

        columns = 3
        for i, tag in enumerate(INTEREST_TAGS):
            var = tk.IntVar()
            self.tag_vars.append((tag, var))
            r = i // columns
            c = i % columns
            chk = tk.Checkbutton(tags_frame, text=tag, variable=var)
            chk.grid(row=r, column=c, sticky="w", padx=10, pady=2)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Post Event", command=self.post_event,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def on_show(self):
        """Called whenever the view is shown. Now we have a user email!"""
        self.update_club_menu()

    def update_club_menu(self):
        """Refreshes the Host Club dropdown with the user's clubs."""
        email = self.controller.current_user_email
        if not email:
            return

        clubs = db.get_user_clubs(email)

        # update an OptionMenu without recreating it
        menu = self.club_menu["menu"]
        menu.delete(0, "end")  # Clear old options

        if not clubs:
            self.club_var.set("No Clubs Found")
            # Disable it if they have no clubs
            self.club_menu.configure(state="disabled")
        else:
            self.club_var.set(clubs[0])
            self.club_menu.configure(state="normal")
            for club in clubs:
                menu.add_command(label=club, command=tk._setit(self.club_var, club))

    def post_event(self):
        name = self.name_entry.get()
        club = self.club_var.get()
        location = self.location_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        if club == "No Clubs Found" or not club:
            messagebox.showerror("Error", "You must belong to a club to post an event.")
            return

        selected_date = self.date_picker.get_date()

        # future date event check
        if selected_date < date.today():
            messagebox.showerror("Invalid Date", "You cannot create an event in the past.")
            return

        # Construct Start Time String
        start_time = f"{self.start_hour.get()}:{self.start_min.get()} {self.start_ampm.get()}"

        # Construct End Time String
        end_time = f"{self.end_hour.get()}:{self.end_min.get()} {self.end_ampm.get()}"

        # Combine them into the format: "YYYY-MM-DD | 6:00 PM - 9:00 PM"
        # Preserves the Date at the front so filtering still works
        final_time_string = f"{selected_date} | {start_time} - {end_time}"

        selected_tags = [tag for tag, var in self.tag_vars if var.get() == 1]

        if not name or not location:
            messagebox.showerror("Missing Info", "Please fill in Event Name and Location.")
            return

        success = db.create_event(name, club, description, final_time_string, location, selected_tags)

        if success:
            messagebox.showinfo("Success", f"Event '{name}' posted!")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not post event.")

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

        # Reset Time Defaults
        self.start_hour.set("6")
        self.start_min.set("00")
        self.start_ampm.set("PM")

        self.end_hour.set("8")
        self.end_min.set("00")
        self.end_ampm.set("PM")

        for _, var in self.tag_vars:
            var.set(0)