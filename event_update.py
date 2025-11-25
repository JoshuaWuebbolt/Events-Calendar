import tkinter as tk
from tkinter import ttk, messagebox  # Import ttk for the dropdowns
from database import db
from constants import CLUB_OPTIONS, INTEREST_TAGS
from tkcalendar import DateEntry
import ast



class EventUpdatePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        # Event names
        self.event_names = db.get_events_by_user_email(self.controller.current_user_email)

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

        # Container for the form details
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Event Name
        tk.Label(form_container, text="Event Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Club
        clubs = db.get_user_clubs(self.controller.current_user_email)
        print(f'Clubs: {clubs}')
        tk.Label(form_container, text="Host Club:", anchor="e").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.club_var = tk.StringVar(self)
        if len(clubs) > 1:
            self.club_var.set(clubs[0])
            tk.OptionMenu(form_container, self.club_var, *clubs).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        else:
            self.club_var.set("")
            tk.OptionMenu(form_container, self.club_var, *["error"]).grid(row=1, column=1, sticky="ew", padx=5, pady=5)


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
        tk.Label(form_container, text="End Time:", anchor="e").grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        end_frame = tk.Frame(form_container)
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

        # Grid: 3 columns wide
        columns = 3
        for i, tag in enumerate(INTEREST_TAGS):
            var = tk.IntVar()
            self.tag_vars.append((tag, var))

            # Calculate row and column
            r = i // columns
            c = i % columns

            chk = tk.Checkbutton(tags_frame, text=tag, variable=var)
            chk.grid(row=r, column=c, sticky="w", padx=10, pady=2)

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Event", command=self.update_event,
                width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                width=15).pack(side="left", padx=10)
    

    def get_event_data(self, event_name: str):
        """Return event data for a given event name."""
        return db.get_event_data_by_event_name(event_name)
        

    def on_show(self):
        """Called by the controller when this page is displayed."""

        # Update events (use the widget master as parent)
        self.update(self.master, self.controller)
        if self.controller.selected_event is not None:

            event_data = db.get_event_data_by_event_name(self.controller.selected_event)
            self.event_id = event_data[5]
            if not event_data:
                return
            
            # populating fields
            # event name
            try:
                # name_entry is a tk.Entry, so use Entry indices (0) not Text indices ("1.0")
                self.name_entry.delete(0, tk.END)
                if len(event_data) > 0 and event_data[0]:
                    self.name_entry.insert(0, event_data[0])
            except Exception:
                pass

            # Club
            try:
                self.club_var.set(event_data[1])
            except Exception:
                pass

            # description_text is a Text widget — replace its contents
            try:
                self.description_text.delete("1.0", tk.END)
                if event_data[2]:
                    self.description_text.insert("1.0", event_data[2])
            except Exception:
                pass
            
            # If your time string is stored in event_data[3] you can parse it here (left as-is)
            # Example parsing can be added later.

            # location_entry is an Entry widget — replace its contents
            try:
                self.location_entry.delete(0, tk.END)
                if len(event_data) > 4 and event_data[4]:
                    self.location_entry.insert(0, event_data[4])
            except Exception:
                pass
            # Date and time
            try:
                # Parse date and time from event_data[3] which is like "2025-11-28 | 8:00 PM - 9:00 PM"
                if len(event_data) > 3 and event_data[3]:
                    time_field = event_data[3]
                    parts = [p.strip() for p in time_field.split("|", 1)]

                    # Date
                    if parts and parts[0]:
                        try:
                            self.date_picker.set_date(parts[0])
                        except Exception:
                            # best-effort fallback: set displayed text if set_date isn't available
                            try:
                                self.date_picker._set_text(parts[0])
                            except Exception:
                                pass

                    # Times
                    if len(parts) > 1 and parts[1]:
                        times = parts[1]
                        if "-" in times:
                            start_str, end_str = [t.strip() for t in times.split("-", 1)]

                            def _parse_time(ts):
                                # returns (hour, minute, AM/PM)
                                if " " in ts:
                                    hm, ampm = ts.rsplit(" ", 1)
                                else:
                                    hm, ampm = ts, ""
                                if ":" in hm:
                                    hour, minute = hm.split(":", 1)
                                else:
                                    hour, minute = hm, "00"
                                return hour.lstrip("0") or "0", minute.zfill(2), ampm.upper()

                            sh, sm, sampm = _parse_time(start_str)
                            eh, em, eampm = _parse_time(end_str)

                            # Set start controls (best-effort, preserving existing on failure)
                            try:
                                self.start_hour.set(str(int(sh)))
                            except Exception:
                                pass
                            try:
                                self.start_min.set(sm if sm in ("00", "15", "30", "45") else sm[:2])
                            except Exception:
                                pass
                            if sampm in ("AM", "PM"):
                                try:
                                    self.start_ampm.set(sampm)
                                except Exception:
                                    pass

                            # Set end controls
                            try:
                                self.end_hour.set(str(int(eh)))
                            except Exception:
                                pass
                            try:
                                self.end_min.set(em if em in ("00", "15", "30", "45") else em[:2])
                            except Exception:
                                pass
                            if eampm in ("AM", "PM"):
                                try:
                                    self.end_ampm.set(eampm)
                                except Exception:
                                    pass
            except Exception:
                pass

            # Parse tags
            tags = db.get_tags_by_event_id(event_data[5])

            # Normalize tags into a set of strings, then set each checkbox accordingly
            try:
                selected_tags = set(tags)

                if tags is None:
                    selected_tags = set()
                elif isinstance(tags, str):
                    # Try to parse Python literal (e.g. "['a', 'b']"), otherwise fall back to comma-split
                    try:
                        parsed = ast.literal_eval(tags)
                        if isinstance(parsed, (list, tuple, set)):
                            selected_tags.update(str(x).strip() for x in parsed if x is not None)
                        else:
                            selected_tags.add(str(parsed).strip())
                    except Exception:
                        selected_tags.update(t.strip() for t in tags.split(",") if t.strip())
                elif isinstance(tags, (list, tuple, set)):
                    selected_tags.update(str(x).strip() for x in tags if x is not None)
                else:
                    # Fallback for single value
                    selected_tags.add(str(tags).strip())

                # Set each checkbox based on membership in selected_tags
                for tag, var in self.tag_vars:
                    var.set(1 if tag in selected_tags else 0)
            except Exception:
                # On any error, clear all checkboxes
                for _, var in self.tag_vars:
                    var.set(0)
        

    def update_event(self):
        name = self.name_entry.get()
        club = self.club_var.get()
        location = self.location_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        # Get Date
        selected_date = self.date_picker.get_date()

        # Construct Start Time String
        start_time = f"{self.start_hour.get()}:{self.start_min.get()} {self.start_ampm.get()}"

        # Construct End Time String
        end_time = f"{self.end_hour.get()}:{self.end_min.get()} {self.end_ampm.get()}"

        # Combine them into the format: "YYYY-MM-DD | 6:00 PM - 9:00 PM"
        # This format preserves the Date at the front, so filtering still works!
        final_time_string = f"{selected_date} | {start_time} - {end_time}"

        selected_tags = [tag for tag, var in self.tag_vars if var.get() == 1]

        if not name or not club or not location:
            messagebox.showerror("Missing Info", "Please fill in Event Name, Club, and Location.")
            return

        success = db.update_event(self.event_id, name, club, description, final_time_string, location, selected_tags)

        if success:
            messagebox.showinfo("Success", f"Event '{name}' updated for {final_time_string}!")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not update event.")

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