import tkinter as tk
from tkinter import ttk, messagebox  # Import ttk for the dropdowns
from database import db
from tkcalendar import DateEntry


class ClubCreation(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Create a Club", font=("Arial", 18, "bold")).pack(pady=20)

        # Container for the form details
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")
        form_container.columnconfigure(0, weight=1)
        form_container.columnconfigure(1, weight=3)

        # Event Details
        # Name
        tk.Label(form_container, text="Club Name:", anchor="e").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.name_entry = tk.Entry(form_container)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # email
        tk.Label(form_container, text="e-mail:", anchor="e").grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.email_var = tk.StringVar(self)
        self.email_var = tk.Entry(form_container)
        self.email_var.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Description
        tk.Label(form_container, text="Description:", anchor="e").grid(row=6, column=0, sticky="ne", padx=5, pady=5)
        self.description_text = tk.Text(form_container, height=4, width=40)
        self.description_text.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Create Club", command=self.create_club,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def create_club(self):
        name = self.name_entry.get()
        email = self.email_var.get()
        description = self.description_text.get("1.0", tk.END).strip()

        if not name or not email or not description:
            messagebox.showerror("Missing Info", "Please fill in name, email and description.")
            return

        success = db.create_club(name, email, description)

        if success:
            messagebox.showinfo("Success", f"Club '{name}' created!")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()
        else:
            messagebox.showerror("Error", "Could not create club.")

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.email_var.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

