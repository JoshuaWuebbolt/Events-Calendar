import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class EventUpdateSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        # Dictionary to map "Display String" -> "Event Name"
        self.name_map = {}

        tk.Label(self, text="Select an Event to Update", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for form
        self.form_container = tk.Frame(self)
        self.form_container.pack(padx=20, pady=10, fill="x")
        self.form_container.columnconfigure(0, weight=1)
        self.form_container.columnconfigure(1, weight=3)

        # Label
        tk.Label(self.form_container, text="Event:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Variable for the dropdown
        self.selected_display_str = tk.StringVar(self)
        self.dropdown = tk.OptionMenu(self.form_container, self.selected_display_str, "")
        self.dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Event", command=self.select_event,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def update_list(self):
        """Refreshes the dropdown with detailed event info."""
        email = self.controller.current_user_email
        if not email: return

        # Clear existing map
        self.name_map = {}

        # Fetch list of dictionaries from DB
        events_data = db.get_events_by_user_email(email)

        menu = self.dropdown["menu"]
        menu.delete(0, "end")  # Clear dropdown

        if not events_data:
            self.selected_display_str.set("No Events Found")
            self.dropdown.configure(state="disabled")
            return

        self.dropdown.configure(state="normal")

        # Set default to first item
        first_display = ""

        for i, evt in enumerate(events_data):
            # Create a detailed string for the user to see
            # Format: "Math Party | Robotics Club | 2025-11-01... | IB 110"
            display_str = f"{evt['name']} | {evt['club']} | {evt['time']} | {evt['location']}"

            # Save mapping: Display String -> Real Name
            self.name_map[display_str] = evt['name']

            # Add to menu
            menu.add_command(label=display_str,
                             command=tk._setit(self.selected_display_str, display_str))

            if i == 0:
                first_display = display_str

        # Set default selection
        if first_display:
            self.selected_display_str.set(first_display)

    def select_event(self):
        display_str = self.selected_display_str.get()

        if display_str == "No Events Found" or not display_str:
            messagebox.showerror("Error", "No event selected.")
            return

        # Retrieve the simple event name using map
        real_event_name = self.name_map.get(display_str)

        if real_event_name:
            self.controller.selected_event = real_event_name
            self.controller.show_frame("EventUpdatePage")
        else:
            messagebox.showerror("Error", "Could not find event details.")

    def on_show(self):
        self.update_list()