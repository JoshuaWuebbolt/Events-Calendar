import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from constants import INTEREST_TAGS
from tkcalendar import DateEntry
from datetime import datetime, date


class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.tag_vars = []
        self.club_vars = []

        # Grid layout: Row 0=Nav, Row 1=Body
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navbar
        nav = tk.Frame(self, bg="#333", height=50)
        nav.grid(row=0, column=0, columnspan=2, sticky="new")
        nav.pack_propagate(False)

        tk.Label(nav, text="UTM Events Calendar", fg="white", bg="#333", font=("Arial", 14, "bold")).pack(side="left",
                                                                                                          padx=15)

        tk.Button(nav, text="Log Out", command=self.logout).pack(side="right", padx=10)
        tk.Button(nav, text="👤 Account", command=lambda: controller.show_frame("AccountPage")).pack(side="right",
                                                                                                    padx=10)
        tk.Button(nav, text="👥 Clubs", command=lambda: controller.show_frame("ClubManagement")).pack(side="right",
                                                                                                     padx=10)
        tk.Button(nav, text="↺ Update Event", command=lambda: controller.show_frame("EventUpdateSelectionPage"),
                  bg="#1A4FFF", fg="white").pack(side="right", padx=10)
        tk.Button(nav, text="➕ Post Event", command=lambda: controller.show_frame("EventCreationPage"),
                  bg="#00AA00", fg="white").pack(side="right", padx=10)


        # Sidebar (Filters)
        sidebar = tk.Frame(self, width=280, bg="#f0f0f0", relief="groove", bd=1)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        tk.Label(sidebar, text="Event Filters", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

        # Date Filters
        tk.Label(sidebar, text="Filter by Date:", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10)

        # Specific Date Filter
        self.use_date_filter = tk.IntVar()
        tk.Checkbutton(sidebar, text="Enable Specific Date", variable=self.use_date_filter, bg="#f0f0f0").pack(
            anchor="w", padx=10)

        self.filter_date_picker = DateEntry(sidebar, width=12, background='darkblue',
                                            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.filter_date_picker.pack(padx=10, pady=5)

        # Past Events Filter
        self.show_past_var = tk.IntVar()
        tk.Checkbutton(sidebar, text="Show Past Events (History)", variable=self.show_past_var, bg="#f0f0f0").pack(
            anchor="w", padx=10)

        # Tags Filter
        tk.Label(sidebar, text="By Category:", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10, pady=(10, 0))
        tag_frame = tk.Frame(sidebar, bg="#f0f0f0")
        tag_frame.pack(padx=10, fill="x", pady=5)

        for i, tag in enumerate(INTEREST_TAGS):
            var = tk.IntVar()
            self.tag_vars.append((tag, var))

            # Math to make it 2 columns
            r = i // 2
            c = i % 2
            tk.Checkbutton(tag_frame, text=tag, variable=var, bg="#f0f0f0").grid(row=r, column=c, sticky="w")

        # 3. Clubs Filter (2 Columns)
        tk.Label(sidebar, text="By Host Club:", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10, pady=(15, 0))
        club_frame = tk.Frame(sidebar, bg="#f0f0f0")
        club_frame.pack(padx=10, fill="x", pady=5)
        self.club_frame = club_frame
        self.club_filters(club_frame)

        # Buttons
        tk.Button(sidebar, text="Apply Filters", command=self.refresh_events, bg="#003366", fg="white").pack(pady=20)
        tk.Button(sidebar, text="Clear Filters", command=self.clear_filters).pack()

        # Main Content
        content_frame = tk.Frame(self, bg="white")
        content_frame.grid(row=1, column=1, sticky="nsew")

        self.canvas = tk.Canvas(content_frame, bg="white")
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header for the feed
        self.header_label = tk.Label(self.scrollable_frame, text="Upcoming Events", font=("Arial", 16), bg="white")
        self.header_label.pack(pady=10, padx=20, anchor="w")

    def club_filters(self, club_frame):
        # We fetch clubs dynamically
        clubs = db.get_club_names()
        if not clubs: clubs = []

        for i, club in enumerate(clubs):
            var = tk.IntVar()
            self.club_vars.append((club, var))

            # Math to make it 2 columns
            r = i // 2
            c = i % 2
            tk.Checkbutton(club_frame, text=club, variable=var, bg="#f0f0f0").grid(row=r, column=c, sticky="w")

    def on_show(self):
        """Called whenever the view is shown."""
        self.refresh_events()
        self.club_filters(self.club_frame)

    def logout(self):
        self.clear_filters()
        self.controller.logout()

    def clear_filters(self):
        for _, var in self.tag_vars: var.set(0)
        for _, var in self.club_vars: var.set(0)
        self.use_date_filter.set(0)
        self.show_past_var.set(0)  # Reset past events toggle
        self.refresh_events()

    def refresh_events(self):
        """Fetches data, applies logic (Upcoming vs Past), and redraws."""
        # Get Filter States
        selected_tags = [tag for tag, var in self.tag_vars if var.get() == 1]
        selected_clubs = [club for club, var in self.club_vars if var.get() == 1]

        specific_date_active = (self.use_date_filter.get() == 1)
        filter_date_str = str(self.filter_date_picker.get_date())

        show_history = (self.show_past_var.get() == 1)

        # Update Header Text based on mode
        if show_history:
            self.header_label.config(text="Past Events (History)")
        elif specific_date_active:
            self.header_label.config(text=f"Events on {filter_date_str}")
        else:
            self.header_label.config(text="Upcoming Events")

        # Get Data
        all_events = db.get_all_events()
        today = date.today()

        # Clear UI
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.header_label:  # Don't delete the title
                widget.destroy()

        count = 0
        for event in all_events:

            # Parse Event Date
            try:
                # Format is "2025-11-25 | 6:00 PM..."
                # Split by | and take the first part
                event_date_str = event['time'].split('|')[0].strip()
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except Exception:
                # If date is corrupted, skip it
                continue

            # Date Filtering
            if specific_date_active:
                # If searching for a SPECIFIC date, ignore "Upcoming vs Past" rules
                if event_date_str != filter_date_str:
                    continue
            else:
                # Normal Mode: Toggle between Upcoming and History
                if show_history:
                    # If "Show Past" is CHECKED, show ONLY past events
                    if event_date >= today:
                        continue
                else:
                    # If "Show Past" is UNCHECKED (Default), show ONLY future/today
                    if event_date < today:
                        continue

            # Club Filtering
            if selected_clubs and event['club'] not in selected_clubs:
                continue

            # Tag Filtering
            if selected_tags:
                event_tags_set = set(event['tags'])
                filter_tags_set = set(selected_tags)
                if not event_tags_set.intersection(filter_tags_set):
                    continue

            self.create_event_card(event)
            count += 1

        if count == 0:
            tk.Label(self.scrollable_frame, text="No events found matching your filters.",
                     fg="gray", bg="white").pack(pady=20)

    def create_event_card(self, event):
        """Draws a visual card for a single event."""
        card = tk.Frame(self.scrollable_frame, bg="#f9f9f9", bd=1, relief="solid")
        card.pack(fill="x", padx=20, pady=10)

        # Header: Name and Time
        header = tk.Frame(card, bg="#e0e0e0")
        header.pack(fill="x")

        tk.Label(header, text=event['name'], font=("Arial", 12, "bold"), bg="#e0e0e0").pack(side="left", padx=10,
                                                                                            pady=5)
        tk.Label(header, text=event['time'], font=("Arial", 10, "italic"), bg="#e0e0e0").pack(side="right", padx=10)

        # Body: Club and Location
        body = tk.Frame(card, bg="#f9f9f9")
        body.pack(fill="x", padx=10, pady=5)

        tk.Label(body, text=f"Hosted by: {event['club']}", fg="#003366", bg="#f9f9f9").pack(anchor="w")
        tk.Label(body, text=f"📍 {event['location']}", fg="#555", bg="#f9f9f9").pack(anchor="w")

        # Description
        tk.Label(body, text=event['description'], wraplength=400, justify="left", bg="#f9f9f9").pack(anchor="w", pady=5)

        # Tags Footer
        if event['tags']:
            tags_str = " | ".join(event['tags'])
            tk.Label(card, text=f"Tags: {tags_str}", bg="#f9f9f9", fg="blue", font=("Arial", 8)).pack(anchor="w",
                                                                                                      padx=10,
                                                                                                      pady=(0, 5))