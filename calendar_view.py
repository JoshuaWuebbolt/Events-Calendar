import tkinter as tk
from tkinter import messagebox


class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Store the variables for checkboxes
        self.tag_vars = []
        self.club_vars = []

        # 1 row for navbar, 1 row for content in main layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Navbar
        nav = tk.Frame(self, bg="#333", height=50)
        nav.grid(row=0, column=0, columnspan=2, sticky="new")
        nav.pack_propagate(False)

        tk.Label(nav, text="UTM Events Calendar", fg="white", bg="#333", font=("Arial", 14)).pack(side="left", padx=15)
        tk.Button(nav, text="Log Out", command=lambda: controller.show_frame("LoginPage")).pack(side="right", padx=15)

        # Sidebar (Filters)
        sidebar = tk.Frame(self, width=250, bg="#f5f5f5", relief="groove", bd=1)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        tk.Label(sidebar, text="Event Filters", font=("Arial", 14, "bold"), bg="#f5f5f5").pack(pady=10)

        # Tags/Interests Filter (Checkboxes)
        tk.Label(sidebar, text="Filter by Tags (e.g., free food):", bg="#f5f5f5").pack(pady=(5, 2), padx=10, anchor="w")

        tag_options = [
            "Free Food",
            "Registration Required",
            "Paid Event",
            "Academic",
            "Social",
        ]

        tag_frame = tk.Frame(sidebar, bg="#f5f5f5")
        tag_frame.pack(padx=10, fill="x")

        # Create a Checkbox for each tag option
        for i, tag in enumerate(tag_options):
            var = tk.IntVar()
            self.tag_vars.append((tag, var))  # Store both the name and the variable
            chk = tk.Checkbutton(tag_frame, text=tag, variable=var, bg="#f5f5f5")
            chk.grid(row=i, column=0, sticky="w")  # grid alignment

        # Club/Host Filter (Checkboxes)
        tk.Label(sidebar, text="Filter by Club:", bg="#f5f5f5").pack(pady=(15, 2), padx=10, anchor="w")

        club_options = [
            "Robotics Club",
            "CSSA",
            "UTMSU",
            "ICCIT Council",
            "UTM MCSS",
        ]

        club_frame = tk.Frame(sidebar, bg="#f5f5f5")
        club_frame.pack(padx=10, fill="x")

        # Create a Checkbox for each club option
        for i, club in enumerate(club_options):
            var = tk.IntVar()
            self.club_vars.append((club, var))  # Store both the name and the variable
            chk = tk.Checkbutton(club_frame, text=club, variable=var, bg="#f5f5f5")
            chk.grid(row=i, column=0, sticky="w")

        # Apply Button
        tk.Button(sidebar, text="Apply Filters", command=self.apply_filters, bg="#003366", fg="white").pack(pady=15)

        # Main Calendar
        main_content = tk.Frame(self, bg="white")
        main_content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        tk.Label(main_content, text="Upcoming Events (4-Week View)", font=("Arial", 16)).pack(pady=15)

        cal_placeholder = tk.Label(main_content,
                                   text="[ Detailed Calendar Grid ]\nEvents will be filtered by selected Tags and Clubs.",
                                   bg="#f0f0f0", relief="sunken")
        cal_placeholder.pack(fill="both", expand=True, padx=20, pady=20)

    def apply_filters(self):
        """Retrieves selected filters from the Checkbox variables."""
        selected_tags = []
        selected_clubs = []

        # Check the state of each variable
        for tag, var in self.tag_vars:
            if var.get() == 1:  # Checkbox is selected
                selected_tags.append(tag)

        for club, var in self.club_vars:
            if var.get() == 1:  # Checkbox is selected
                selected_clubs.append(club)

        print(f"Tags Applied: {selected_tags}")
        print(f"Clubs Applied: {selected_clubs}")

        messagebox.showinfo("Filters Applied",
                            f"Tags: {', '.join(selected_tags) or 'None'}\n"
                            f"Clubs: {', '.join(selected_clubs) or 'None'}")