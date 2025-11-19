import tkinter as tk
from tkinter import messagebox
from database import db
from constants import INTEREST_TAGS

class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        self.interest_vars = []
        self.all_interest_tags = INTEREST_TAGS

        tk.Label(self, text="Account & Profile Management", font=("Arial", 18, "bold")).pack(pady=20)

        # Profile Frame
        profile_frame = tk.LabelFrame(self, text="Update Profile", padx=20, pady=20)
        profile_frame.pack(pady=10, padx=50, fill="x")

        profile_frame.columnconfigure(1, weight=1)

        # Name Input
        tk.Label(profile_frame, text="Full Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(profile_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Email Input (used as ID)
        tk.Label(profile_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = tk.Entry(profile_frame, width=40)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Interest Checkbox
        tk.Label(profile_frame, text="Interests:").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Frame to hold the checkboxes
        interest_check_frame = tk.Frame(profile_frame)
        interest_check_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Create Checkboxes dynamically
        for i, tag in enumerate(self.all_interest_tags):
            var = tk.IntVar()
            self.interest_vars.append((tag, var))
            chk = tk.Checkbutton(interest_check_frame, text=tag, variable=var)

            # Layout the checkboxes in two columns for better spacing
            col = i % 2
            row = i // 2
            chk.grid(row=row, column=col, sticky="w", padx=5)

        # Action Buttons
        button_frame = tk.Frame(profile_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Update Profile", command=self.update_profile, width=15, bg="#0066AA",
                  fg="white").pack(side="left", padx=10)
        tk.Button(button_frame, text="Delete Account", command=self.delete_account, width=15, bg="#CC3300",
                  fg="white").pack(side="left", padx=10)

        # Event Management
        tk.Label(self, text="--- My Events ---", font=("Arial", 12, "bold")).pack(pady=15)
        tk.Label(self, text="[ List of Events posted by user / Club Moderator ]", relief="sunken", padx=20,
                 pady=20).pack(fill="x", padx=50)

        # Back Button
        tk.Button(self, text="Back to Calendar", command=lambda: controller.show_frame("CalendarPage")).pack(pady=20)

    def on_show(self):
        """Called by the controller when this page is displayed."""
        self.load_profile_data()

    def load_profile_data(self):
        """Fetches and displays the current user's data, setting checkbox states."""
        email = self.controller.current_user_email
        if not email: return

        # user_data is (name, user_email, [interest1, interest2, ...])
        user_data = db.get_user_by_email(email)

        if user_data:
            name, user_email, interests_list = user_data

            # 1. Update Name/Email fields
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, user_email)
            self.current_user_email_id = user_email  # Store original email for updates/deletes

            # 2. Set Checkbox States based on the database list
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

        # Collect selected interests from checkboxes
        new_interests = []
        for tag, var in self.interest_vars:
            if var.get() == 1:
                new_interests.append(tag)

        # Call the database update function
        messagebox.showinfo("Update Pending",
                            "Database update logic for interests needs finalization.")

        result = db.update_user_profile(old_email, new_name, new_email, ", ".join(new_interests))

        if result is True:
            # If email changed, update the app's state
            if old_email != new_email:
                self.controller.current_user_email = new_email
                self.current_user_email_id = new_email

            messagebox.showinfo("Success", "Profile updated successfully!")

        elif result == "EmailExists":
            messagebox.showerror("Error", "Update failed: The new email is already in use by another account.")
        else:
            messagebox.showerror("Error", "Failed to update profile due to a database error.")

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