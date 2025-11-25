import tkinter as tk
from tkinter import ttk, messagebox  # Import ttk for the dropdowns
from database import db
from constants import CLUB_OPTIONS, INTEREST_TAGS
from tkcalendar import DateEntry



class EventUpdateSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        # Event names
        self.event_names = db.get_events_name_by_user_email(self.controller.current_user_email)

        tk.Label(self, text="Select an Event to Update", font=("Arial", 18, "bold")).pack(pady=20)

        self.update(parent, controller)

    def update(self, parent, controller):

        # Remove previous widgets (keep the main title label if present)
        for child in list(self.winfo_children()):
            if isinstance(child, tk.Label) and child.cget("text") == "Select an Event to Update":
                continue
            child.destroy()

        # Refresh event list for the UI
        self.event_names = db.get_events_by_user_email(self.controller.current_user_email)
        print(f'event names: {self.event_names}')
        # print(f'Event names: {self.event_names}')

        # Container for the form details
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Event Name
        tk.Label(form_container, text="Event Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.StringVar(self)
        if(len(self.event_names) > 0):
            self.name_entry.set("")
            tk.OptionMenu(form_container, self.name_entry, *self.event_names).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Event", command=self.select_event,
                width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                width=15).pack(side="left", padx=10)
    
    def select_event(self):
        self.controller.selected_event = self.name_entry.get()
        self.controller.show_frame("EventUpdatePage")

    def on_show(self):
        """Called by the controller when this page is displayed."""

        # Update events
        self.update(self.master, self.controller)
