import tkinter as tk
from tkinter import messagebox
from database import db


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")
        self.stay_logged_in = 0

        center_frame = tk.Frame(self, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center_frame, text="UTM Events Calendar", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)

        # Inputs
        tk.Label(center_frame, text="Email:", bg="#f0f0f0").pack(pady=5)
        self.email_entry = tk.Entry(center_frame, width=30)
        self.email_entry.pack(pady=5)

        tk.Label(center_frame, text="Password:", bg="#f0f0f0").pack(pady=5)
        self.pass_entry = tk.Entry(center_frame, show="*", width=30)
        self.pass_entry.pack(pady=5)

        # Buttons
        tk.Button(center_frame, text="Login", command=self.validate_login,
                  width=20, bg="#003366", fg="white").pack(pady=20)
        # # Checkbox
        # tk.Checkbutton(center_frame, text="Stay Logged in:", variable=self.stay_logged_in).pack()

        tk.Button(center_frame, text="Don't have one? Create Account", command=lambda: controller.show_frame("RegisterPage"),
                  relief="flat", bg="#f0f0f0", fg="blue").pack()
        tk.Button(center_frame, text="Exit Application", command=self.controller.quit, width=20, bg="#cc3300",
                  fg="white").pack(pady=10)
        


    def validate_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()


        # Check validation
        if email and password:
            user_email = db.check_credentials(email, password)

            if user_email:
                messagebox.showinfo("Login Success", f"Welcome back, {email}!")
                self.controller.login_success(user_email)
            else:
                messagebox.showerror("Login Failed", "Invalid email or password.")
        else:
            messagebox.showerror("Error", "Please enter email and password")