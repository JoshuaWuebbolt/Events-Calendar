import tkinter as tk
from tkinter import messagebox
from database import db
from constants import INTEREST_TAGS
from datetime import datetime, date


class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.current_user_email_id = None

        self.interest_vars = []
        self.all_interest_tags = INTEREST_TAGS

        # Header
        tk.Label(self, text="Account & Profile Management", font=("Arial", 18, "bold")).pack(pady=10)

        # Bottom Navigation Frame
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x", pady=20)

        tk.Button(bottom_frame, text="Back to Calendar",
                  command=lambda: controller.show_frame("CalendarPage"),
                  height=2, bg="#ddd").pack()

        # Profile Frame
        profile_frame = tk.LabelFrame(self, text="Update Profile", padx=20, pady=10)
        profile_frame.pack(pady=5, padx=50, fill="x")
        profile_frame.columnconfigure(1, weight=1)

        # Name
        tk.Label(profile_frame, text="Full Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(profile_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Email
        tk.Label(profile_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = tk.Entry(profile_frame, width=40)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Interests
        tk.Label(profile_frame, text="Interests:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        interest_check_frame = tk.Frame(profile_frame)
        interest_check_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        for i, tag in enumerate(self.all_interest_tags):
            var = tk.IntVar()
            self.interest_vars.append((tag, var))
            chk = tk.Checkbutton(interest_check_frame, text=tag, variable=var)
            chk.grid(row=i // 2, column=i % 2, sticky="w", padx=5)

        # Profile Buttons
        btn_frame = tk.Frame(profile_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Update Profile", command=self.update_profile, bg="#0066AA", fg="white").pack(
            side="left", padx=10)
        tk.Button(btn_frame, text="Delete Account", command=self.delete_account, bg="#CC3300", fg="white").pack(
            side="left", padx=10)

        # Event Management List
        tk.Label(self, text="--- My Events ---", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=50, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.events_listbox = tk.Listbox(list_frame, height=6, yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.events_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.events_listbox.yview)

    def on_show(self):
        self.load_profile_data()
        self.load_user_events()

    def load_user_events(self):
        self.events_listbox.delete(0, tk.END)
        email = self.controller.current_user_email
        if email:
            user_events = db.get_events_by_user_email(email)
            today = date.today()

            if user_events:
                for evt in user_events:
                    # Logic to determine status
                    status = "[UPCOMING]"
                    try:
                        # Extract "2025-11-25" from "2025-11-25 | 6:00 PM - 8:00 PM"
                        event_date_str = evt['time'].split('|')[0].strip()
                        event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()

                        if event_date < today:
                            status = "[COMPLETED]"
                    except Exception:
                        status = "[UNKNOWN]"

                    # Format: "[COMPLETED] Math Party | 2025-11-01... | IB 110"
                    display_str = f"{status:<11} {evt['name']} | {evt['time']} | {evt['location']}"
                    self.events_listbox.insert(tk.END, display_str)
            else:
                self.events_listbox.insert(tk.END, "No events found (Join a club and create one!)")

    def load_profile_data(self):
        """Fetches and displays the current user's data, setting checkbox states."""
        email = self.controller.current_user_email
        if not email: return

        # user_data is (name, user_email, [interest1, interest2, ...])
        user_data = db.get_user_by_email(email)

        if user_data:
            name, user_email, interests_list = user_data

            # Update Name/Email fields
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, user_email)
            self.current_user_email_id = user_email  # Store original email for updates/deletes

            # Set Checkbox States based on the database list
            active_interests = set(interests_list)
            for tag, var in self.interest_vars:
                if tag in active_interests:
                    var.set(1)  # Check the box
                else:
                    var.set(0)  # Uncheck the box

    def update_profile(self):
        """Handles updating the user's profile information and interests."""
        old_email = self.current_user_email_id
        new_name = self.name_entry.get()
        new_email = self.email_entry.get()

        if not new_name or not new_email:
            messagebox.showerror("Error", "Name and Email cannot be empty.")
            return

        new_interests = [tag for tag, var in self.interest_vars if var.get() == 1]
        result = db.update_user_profile(old_email, new_name, new_email, new_interests)

        if result is True:
            # If email changed, update the app's state
            if old_email != new_email:
                self.controller.current_user_email = new_email
                self.current_user_email_id = new_email
            messagebox.showinfo("Success", "Profile updated!")
        elif result == "EmailExists":
            messagebox.showerror("Error", "Email taken.")
        else:
            messagebox.showerror("Error", "Update failed.")

    def delete_account(self):
        """Handles deleting the user's account."""
        confirm = messagebox.askyesno("Confirm Delete",
                                      "Are you sure you want to permanently delete your account? "
                                      "This action cannot be undone.")

        if confirm:
            email = self.current_user_email_id
            if db.delete_user_account(email):
                messagebox.showinfo("Deleted", "Your account has been successfully deleted.")
                self.controller.logout()
            else:
                messagebox.showerror("Error", "Failed to delete account.")