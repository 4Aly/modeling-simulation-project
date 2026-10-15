from pathlib import Path

import customtkinter
from PIL import Image

if __package__:
    from .task1 import Task1Page
else:
    from views.task1 import Task1Page


class MainMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#101820", corner_radius=0)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = customtkinter.CTkFrame(
            self,
            width=250,
            fg_color="#17232D",
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            self.sidebar,
            text="MODELING\n& SIMULATION",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color="#F4F7F9",
            justify="left",
        ).grid(row=0, column=0, padx=24, pady=(32, 40), sticky="w")

        customtkinter.CTkLabel(
            self.sidebar,
            text="MENU",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color="#8EA2B2",
        ).grid(row=1, column=0, padx=24, pady=(0, 10), sticky="w")

        self.main_menu_button = customtkinter.CTkButton(
            self.sidebar,
            text="⌂   Main menu",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="#244B50",
            hover_color="#2E5D62",
            text_color="#FFFFFF",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=self.show_main_menu,
        )
        self.main_menu_button.grid(row=2, column=0, padx=14, sticky="ew")

        self.task1_button = customtkinter.CTkButton(
            self.sidebar,
            text="☑   Task 1",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color="#2B3C4A",
            hover_color="#1D2C39",
            text_color="#F4F7F9",
            font=customtkinter.CTkFont(size=14),
            command=self.show_task_1,
        )
        self.task1_button.grid(row=3, column=0, padx=14, pady=(8, 0), sticky="ew")

        customtkinter.CTkLabel(
            self.sidebar,
            text="Faculty of Computer and\nInformation Sciences",
            font=customtkinter.CTkFont(size=12),
            text_color="#A9B8C3",
            justify="left",
        ).grid(row=4, column=0, padx=24, pady=(0, 24), sticky="sw")

        self.sidebar.grid_rowconfigure(4, weight=1)

        self.content = customtkinter.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=40, pady=32)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure((0, 1, 2), weight=1)

        self.main_page = customtkinter.CTkFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
        )
        self.main_page.grid(row=0, column=0, sticky="nsew")
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.grid_rowconfigure((0, 1, 2), weight=1)

        self.task1_page = Task1Page(self.content)
        self.task1_page.grid(row=0, column=0, sticky="nsew")
        self.task1_page.grid_remove()

        logo_path = Path(__file__).resolve().parents[2] / "assets" / "fcis.png"
        logo = Image.open(logo_path)
        self.logo_image = customtkinter.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(360, 240),
        )

        customtkinter.CTkLabel(
            self.main_page,
            text="",
            image=self.logo_image,
        ).grid(row=0, column=0, sticky="s")

        customtkinter.CTkLabel(
            self.main_page,
            text="Faculty of Computer and Information Sciences",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
            wraplength=700,
        ).grid(row=1, column=0, padx=20, pady=(8, 8), sticky="n")

        customtkinter.CTkLabel(
            self.main_page,
            text="Modeling and Simulation Project",
            font=customtkinter.CTkFont(size=17),
            text_color="#9FB0BC",
        ).grid(row=2, column=0, padx=20, pady=(0, 30), sticky="n")

        self.show_main_menu()

    def show_main_menu(self):
        self.main_page.grid()
        self.task1_page.grid_remove()
        self.main_menu_button.configure(fg_color="#244B50")
        self.task1_button.configure(fg_color="transparent")

    def show_task_1(self):
        self.main_page.grid_remove()
        self.task1_page.grid()
        self.main_menu_button.configure(fg_color="transparent")
        self.task1_button.configure(fg_color="#244B50")
