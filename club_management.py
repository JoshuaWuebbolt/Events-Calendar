import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class ClubManagement(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Club Management", font=("Arial", 18, "bold")).pack(pady=20)

        # Container
        form_container = tk.Frame(self)
        form_container.pack(padx=20, pady=10, fill="x")

        # Create new club button
        tk.Button(form_container, text="Create New Club", command=lambda: controller.show_frame("ClubCreation"),
                  width=15, bg="#22AA00", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        # Tags/Clubs List
        tk.Label(self, text="Select Clubs to join:").pack(anchor='w', padx=20, pady=(10, 0))

        self.club_vars = []
        self.tags_frame = tk.Frame(self)
        self.tags_frame.pack(anchor="w", padx=20, pady=5, fill="x")

        # Buttons
        # Packing this last with ample padding ensures it sits at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Update Clubs", command=self.update_clubs,
                  width=15, bg="#0066AA", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

        tk.Button(button_frame, text="Cancel", command=lambda: controller.show_frame("CalendarPage"),
                  width=15).pack(side="left", padx=10)

    def load_and_display_clubs(self):
        """Displays all clubs."""

        # FIX: Clear existing widgets first so we don't get duplicates
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        self.club_vars = []  # Clear the list of variables

        clubs = db.get_club_names()

        # Pre-check clubs user is already in
        user_clubs = []
        if self.controller.current_user_email:
            user_clubs = db.get_user_clubs(self.controller.current_user_email)

        columns = 3
        for i, club_name in enumerate(clubs):
            var = tk.IntVar()
            # If user is already in this club, check the box
            if club_name in user_clubs:
                var.set(1)

            self.club_vars.append((club_name, var))

            r = i // columns
            c = i % columns
            chk = tk.Checkbutton(self.tags_frame, text=club_name, variable=var)
            chk.grid(row=r, column=c, sticky="w", padx=10, pady=2)

    def update_clubs(self):
        selected_clubs = [club for club, var in self.club_vars if var.get() == 1]

        result = db.update_user_clubs(self.controller.current_user_email, selected_clubs)

        if result is True:
            messagebox.showinfo("Success", f"Club membership updated!")
            self.controller.show_frame("CalendarPage")
            self.clear_fields()

        # if admin, can't uncheck a club you own
        elif result == "AdminConstraint":
            messagebox.showerror("Permission Denied",
                                 "You cannot uncheck a club you own.\n\n"
                                 "As an Admin, you must either delete the club entirely "
                                 "or transfer ownership before leaving.")
            # Reload the checkboxes so the Admin box gets re-checked visually
            self.load_and_display_clubs()

        else:
            messagebox.showerror("Error", "Could not update clubs.")

    def on_show(self):
        self.load_and_display_clubs()