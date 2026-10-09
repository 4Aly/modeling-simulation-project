import customtkinter

if __package__:
    from .views.mainmenu import MainMenu
else:
    from views.mainmenu import MainMenu


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modeling and Simulation")
        self.geometry("1280x720")
        self.minsize(900, 600)

        self.main_menu = MainMenu(self)
        self.main_menu.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()