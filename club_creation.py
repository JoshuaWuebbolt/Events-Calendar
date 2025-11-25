import tkinter as tk
from tkinter import messagebox
from database import db


class ClubCreation(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Create a Club", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for the form details
        self.form_container = tk.Frame(self)
        self.form_container.pack(padx=20, pady=10, fill="x")
        self.form_container.columnconfigure(0, weight=1)
        self.form_container.columnconfigure(1, weight=3)

        # Club Name
        tk.Label(self.form_container, text="Club Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(self.form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Club Email
        tk.Label(self.form_container, text="Registered Contact Email:", anchor="e").grid(row=1, column=0, sticky="ew",
                                                                                         padx=5, pady=5)

        # use a Label to display the email, user cannot edit it.
        self.email_label = tk.Label(self.form_container, text="", anchor="w", fg="blue")
        self.email_label.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Description
        tk.Label(self.form_container, text="Description:", anchor="e").grid(row=2, column=0, sticky="ne", padx=5,
                                                                            pady=5)
        self.description_text = tk.Text(self.form_container, height=4, width=40)
        self.description_text.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Create Club", command=self.create_club,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def on_show(self):
        """Refresh the email label when the page is shown."""
        current_email = self.controller.current_user_email
        if current_email:
            self.email_label.config(text=current_email)
        else:
            self.email_label.config(text="Error: Not Logged In")

    def create_club(self):
        name = self.name_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        # We get the email directly from the controller, not an entry field.
        creator_email = self.controller.current_user_email

        if not creator_email:
            messagebox.showerror("Error", "You must be logged in.")
            return

        if not name or not description:
            messagebox.showerror("Missing Info", "Please fill in name and description.")
            return

        # Pass creator_email as BOTH the club email AND the creator
        success = db.create_club(name, creator_email, description, creator_email)

        if success:
            messagebox.showinfo("Success", f"Club '{name}' created! You are the Admin.")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not create club (Name might be taken).")

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

