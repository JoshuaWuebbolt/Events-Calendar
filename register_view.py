import tkinter as tk
from tkinter import messagebox
from database import db


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="Create Account", font=("Arial", 18, "bold")).pack(pady=20)

        # Form Container
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = tk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.pass_entry = tk.Entry(form_frame, show="*")
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)

        # Interest tags
        tk.Label(self, text="Select Interests (for event recommendations):", font=("Arial", 10, "bold")).pack(
            pady=(20, 5))

        self.var_free_food = tk.IntVar()
        self.var_academic = tk.IntVar()
        self.var_sports = tk.IntVar()
        self.var_social = tk.IntVar()

        chk_frame = tk.Frame(self)
        chk_frame.pack()

        tk.Checkbutton(chk_frame, text="Free Food", variable=self.var_free_food).grid(row=0, column=0, padx=10)
        tk.Checkbutton(chk_frame, text="Academic", variable=self.var_academic).grid(row=0, column=1, padx=10)
        tk.Checkbutton(chk_frame, text="Clubs/Sports", variable=self.var_sports).grid(row=1, column=0, padx=10)
        tk.Checkbutton(chk_frame, text="Social", variable=self.var_social).grid(row=1, column=1, padx=10)

        # Buttons
        tk.Button(self, text="Sign Up", command=self.register_user, width=15, bg="#4CAF50", fg="white").pack(pady=20)
        tk.Button(self, text="Back", command=lambda: controller.show_frame("LoginPage")).pack()

    def register_user(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()

        interests = []
        if self.var_free_food.get(): interests.append("Free Food")
        if self.var_academic.get(): interests.append("Academic")
        if self.var_sports.get(): interests.append("Clubs/Sports")
        if self.var_social.get(): interests.append("Social")

        # Convert list to a comma-separated string for easy storage
        interests_str = ",".join(interests)

        if name and email and password:
            success = db.register_user(name, email, password, interests_str)

            if success:
                messagebox.showinfo("Success", f"Account created for {name}! Interests saved.")
                self.controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Error", "Registration failed. Email may already be in use.")
        else:
            messagebox.showwarning("Missing Info", "Please fill in all required fields.")