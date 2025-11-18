import tkinter as tk

from login_view import LoginPage
from register_view import RegisterPage
from calendar_view import CalendarPage


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

        self.frames = {}

        # Loop through view screens
        for F in (LoginPage, RegisterPage, CalendarPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            # sticky="nsew" makes the specific page fill the container
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = EventsCalendarApp()
    app.mainloop()