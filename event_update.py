import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from constants import INTEREST_TAGS
from tkcalendar import DateEntry
import ast



class EventUpdatePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.event_id = None  # Store ID for deletion

        tk.Label(self, text="Update Event Details", font=("Arial", 18, "bold")).pack(pady=20)

        #build the UI once in init, but refresh data in on_show
        self.build_ui()

    def build_ui(self):
        # Container
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Event Name
        tk.Label(form_container, text="Event Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Club
        tk.Label(form_container, text="Host Club:", anchor="e").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.club_var = tk.StringVar(self)
        self.club_menu = tk.OptionMenu(form_container, self.club_var, "")
        self.club_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Date
        tk.Label(form_container, text="Date:", anchor="e").grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.date_picker = DateEntry(form_container, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Start Time
        tk.Label(form_container, text="Start Time:", anchor="e").grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        start_frame = tk.Frame(form_container)
        start_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.start_hour = ttk.Combobox(start_frame, values=[str(i) for i in range(1, 13)], width=3, state="readonly")
        self.start_hour.pack(side="left")
        tk.Label(start_frame, text=":").pack(side="left")
        self.start_min = ttk.Combobox(start_frame, values=["00", "15", "30", "45"], width=3, state="readonly")
        self.start_min.pack(side="left")
        self.start_ampm = ttk.Combobox(start_frame, values=["AM", "PM"], width=3, state="readonly")
        self.start_ampm.pack(side="left", padx=5)

        # End Time
        tk.Label(form_container, text="End Time:", anchor="e").grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        end_frame = tk.Frame(form_container)
        end_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.end_hour = ttk.Combobox(end_frame, values=[str(i) for i in range(1, 13)], width=3, state="readonly")
        self.end_hour.pack(side="left")
        tk.Label(end_frame, text=":").pack(side="left")
        self.end_min = ttk.Combobox(end_frame, values=["00", "15", "30", "45"], width=3, state="readonly")
        self.end_min.pack(side="left")
        self.end_ampm = ttk.Combobox(end_frame, values=["AM", "PM"], width=3, state="readonly")
        self.end_ampm.pack(side="left", padx=5)

        # Location
        tk.Label(form_container, text="Location:", anchor="e").grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.location_entry = tk.Entry(form_container)
        self.location_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Description
        tk.Label(form_container, text="Description:", anchor="e").grid(row=6, column=0, sticky="ne", padx=5, pady=5)
        self.description_text = tk.Text(form_container, height=4, width=40)
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
            chk = tk.Checkbutton(tags_frame, text=tag, variable=var)
            chk.grid(row=i // columns, column=i % columns, sticky="w", padx=10, pady=2)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Event", command=self.update_event,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Delete Event", command=self.delete_event,
                  width=15, bg="#CC3300", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: self.controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def on_show(self):
        # Update Club Dropdown
        email = self.controller.current_user_email
        clubs = db.get_user_clubs(email)
        menu = self.club_menu["menu"]
        menu.delete(0, "end")

        if clubs:
            for club in clubs:
                menu.add_command(label=club, command=tk._setit(self.club_var, club))
        else:
            self.club_var.set("No Clubs")

        # Populate Data
        if self.controller.selected_event:
            event_data = db.get_event_data_by_event_name(self.controller.selected_event)
            if not event_data: return

            # event_data structure from DB: (name, host_club, desc, time, location, id)
            self.event_id = event_data[5]

            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, event_data[0])
            self.club_var.set(event_data[1])
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert("1.0", event_data[2])
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, event_data[4])

            # Time Parsing
            try:
                time_field = event_data[3]  # "2025-11-25 | 6:00 PM - 8:00 PM"
                parts = [p.strip() for p in time_field.split("|", 1)]
                if parts:
                    self.date_picker.set_date(parts[0])

                if len(parts) > 1:
                    times = parts[1].split("-")  # ["6:00 PM", " 8:00 PM"]
                    if len(times) == 2:
                        start = times[0].strip().split(" ")  # ["6:00", "PM"]
                        end = times[1].strip().split(" ")

                        sh, sm = start[0].split(":")
                        self.start_hour.set(sh)
                        self.start_min.set(sm)
                        self.start_ampm.set(start[1])

                        eh, em = end[0].split(":")
                        self.end_hour.set(eh)
                        self.end_min.set(em)
                        self.end_ampm.set(end[1])
            except Exception:
                pass  # If format changed, just leave defaults

            # Tags
            tags = db.get_tags_by_event_id(self.event_id)
            selected_tags = set(tags) if tags else set()
            for tag, var in self.tag_vars:
                var.set(1 if tag in selected_tags else 0)

    def delete_event(self):
        if not self.event_id: return

        # Get the club hosting this event
        current_club = self.club_var.get()
        current_user = self.controller.current_user_email

        # Check if user is admin of this club
        if not db.is_club_admin(current_user, current_club):
            messagebox.showerror("Permission Denied",
                                 f"Only Admins of '{current_club}' can delete events.")
            return


        confirm = messagebox.askyesno("Confirm Delete",
                                      "Are you sure you want to permanently delete this event?")
        if confirm:
            if db.delete_event(self.event_id):
                messagebox.showinfo("Deleted", "Event has been removed.")
                self.controller.show_frame("CalendarPage")
            else:
                messagebox.showerror("Error", "Failed to delete event.")

    def update_event(self):
        name = self.name_entry.get()
        club = self.club_var.get()
        location = self.location_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        # Time Construction
        selected_date = self.date_picker.get_date()

        # Construct Start Time String
        start_time = f"{self.start_hour.get()}:{self.start_min.get()} {self.start_ampm.get()}"

        # Construct End Time String
        end_time = f"{self.end_hour.get()}:{self.end_min.get()} {self.end_ampm.get()}"

        # Combine them into the format: "YYYY-MM-DD | 6:00 PM - 9:00 PM"
        # Preserves the Date at the front so filtering still works
        final_time_string = f"{selected_date} | {start_time} - {end_time}"

        selected_tags = [tag for tag, var in self.tag_vars if var.get() == 1]

        if db.update_event(self.event_id, name, club, description, final_time_string, location, selected_tags):
            messagebox.showinfo("Success", "Event updated!")
            self.controller.show_frame("CalendarPage")
        else:
            messagebox.showerror("Error", "Update failed.")