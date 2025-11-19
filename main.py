import tkinter as tk

from login_view import LoginPage
from register_view import RegisterPage
from calendar_view import CalendarPage
from event_creation import EventCreationPage
from account_view import AccountPage


class EventsCalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UTM Events Calendar")
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")  # sticky="nsew" expands it

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.current_user_email = None
        self.frames = {}

        # Loop through view screens
        for F in (LoginPage, RegisterPage, CalendarPage, EventCreationPage, AccountPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            # sticky="nsew" makes the specific page fill the container
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


    def login_success(self, email):
        self.current_user_email = email
        self.show_frame("CalendarPage")

    def logout(self):
        self.current_user_email = None
        self.show_frame("LoginPage")


if __name__ == "__main__":
    app = EventsCalendarApp()
    app.mainloop()