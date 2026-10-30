from pathlib import Path
import sys

import customtkinter
from PIL import Image

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from simulations.task4 import rngs

if __package__:
    from .task1 import Task1Page
    from .task2 import Task2Page
    from .task3 import Task3Page
else:
    from views.task1 import Task1Page
    from views.task2 import Task2Page
    from views.task3 import Task3Page


class MainMenu(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#101820", corner_radius=0)
        rngs.initialize_variables()

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
    
        self.task2_button = customtkinter.CTkButton(
            self.sidebar,
            text="☑   Task 2",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color="#2B3C4A",
            hover_color="#1D2C39",
            text_color="#F4F7F9",
            font=customtkinter.CTkFont(size=14),
            command=self.show_task_2,
        )
        self.task2_button.grid(row=4, column=0, padx=14, pady=(8, 0), sticky="ew")

        self.task3_button = customtkinter.CTkButton(
            self.sidebar,
            text="☑   Task 3",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color="#2B3C4A",
            hover_color="#1D2C39",
            text_color="#F4F7F9",
            font=customtkinter.CTkFont(size=14),
            command=self.show_task_3,
        )
        self.task3_button.grid(row=5, column=0, padx=14, pady=(8, 0), sticky="ew")
    
        customtkinter.CTkLabel(
            self.sidebar,
            text="Faculty of Computer and\nInformation Sciences",
            font=customtkinter.CTkFont(size=12),
            text_color="#A9B8C3",
            justify="left",
        ).grid(row=6, column=0, padx=24, pady=(0, 24), sticky="sw")

        self.sidebar.grid_rowconfigure(6, weight=1)

        self.content = customtkinter.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=40, pady=32)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.main_page = customtkinter.CTkFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
        )
        self.main_page.grid(row=0, column=0, sticky="nsew")
        self.main_page.grid_columnconfigure(0, weight=1)
        self.main_page.grid_rowconfigure(0, weight=1)

        self.task1_page = Task1Page(self.content)
        self.task1_page.grid(row=0, column=0, sticky="nsew")
        self.task1_page.grid_remove()

        self.task2_page = Task2Page(self.content)
        self.task2_page.grid(row=0, column=0, sticky="nsew")
        self.task2_page.grid_remove()

        self.task3_page = Task3Page(self.content)
        self.task3_page.grid(row=0, column=0, sticky="nsew")
        self.task3_page.grid_remove()

        logo_path = Path(__file__).resolve().parents[2] / "assets" / "fcis.png"
        logo = Image.open(logo_path)
        self.logo_image = customtkinter.CTkImage(
            light_image=logo,
            dark_image=logo,
            size=(280, 185),
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

        self.create_rng_controls()

        self.show_main_menu()

    def create_rng_controls(self):
        controls = customtkinter.CTkFrame(
            self.main_page,
            fg_color="#17232D",
            corner_radius=8,
        )
        controls.grid(row=3, column=0, padx=10, pady=(0, 8), sticky="ew")
        controls.grid_columnconfigure((0, 1, 2, 3), weight=1)

        customtkinter.CTkLabel(
            controls,
            text="Random number generator",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=4, padx=14, pady=(12, 4), sticky="w")

        fields = (
            ("Generator", "generator", 0, 0),
            ("Seed", "seed", 0, 1),
            ("Number of values", "count", 0, 2),
            ("Exponential rate", "rate", 0, 3),
            ("Multiplier", "multiplier", 2, 0),
            ("Increment", "increment", 2, 1),
            ("Modulus", "modulus", 2, 2),
        )
        self.rng_entries = {}

        for label, name, row, column in fields:
            customtkinter.CTkLabel(
                controls,
                text=label,
                text_color="#A9B8C3",
                anchor="w",
            ).grid(
                row=row + 1,
                column=column,
                padx=10,
                pady=(4, 0),
                sticky="ew",
            )

            if name == "generator":
                self.generator_menu = customtkinter.CTkOptionMenu(
                    controls,
                    values=[generator.name for generator in rngs.Generator],
                    height=32,
                )
                self.generator_menu.set(rngs.generator.name)
                self.generator_menu.grid(
                    row=row + 2,
                    column=column,
                    padx=10,
                    pady=(2, 8),
                    sticky="ew",
                )
            else:
                entry = customtkinter.CTkEntry(controls, height=32)
                entry.insert(0, str(getattr(rngs, name)))
                entry.grid(
                    row=row + 2,
                    column=column,
                    padx=10,
                    pady=(2, 8),
                    sticky="ew",
                )
                self.rng_entries[name] = entry

        customtkinter.CTkButton(
            controls,
            text="Save settings",
            command=self.store_generator_variables,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=4, column=3, padx=10, pady=(16, 8), sticky="ew")

        self.rng_status_label = customtkinter.CTkLabel(
            controls,
            text="",
            text_color="#A9B8C3",
            anchor="w",
        )
        self.rng_status_label.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=14,
            pady=(0, 4),
            sticky="ew",
        )

    def store_generator_variables(self):
        try:
            generator = rngs.Generator[self.generator_menu.get()]
            multiplier = int(self.rng_entries["multiplier"].get())
            increment = int(self.rng_entries["increment"].get())
            modulus = int(self.rng_entries["modulus"].get())
            seed = int(self.rng_entries["seed"].get())
            count = int(self.rng_entries["count"].get())
            rate = float(self.rng_entries["rate"].get())

            if modulus <= 1:
                raise ValueError("Modulus must be greater than 1.")
            if not 0 <= seed < modulus:
                raise ValueError("Seed must be between 0 and modulus - 1.")
            if count < 1:
                raise ValueError("Number of values must be at least 1.")
            if generator == rngs.Generator.EXPONENTIAL and rate <= 0:
                raise ValueError("Exponential rate must be greater than 0.")

            rngs.initialize_variables(
                generator_choice=generator,
                multiplier_value=multiplier,
                increment_value=increment,
                modulus_value=modulus,
                seed_value=seed,
                count_value=count,
                rate_value=rate,
            )
        except ValueError as error:
            self.rng_status_label.configure(text=str(error), text_color="#E88B82")
            return

        self.rng_status_label.configure(
            text=f"Settings saved for {generator.name}.",
            text_color="#9BC9B0",
        )

    def show_main_menu(self):
        self.main_page.grid()
        self.task1_page.grid_remove()
        self.task2_page.grid_remove()
        self.task3_page.grid_remove()
        self.main_menu_button.configure(fg_color="#244B50")
        self.task1_button.configure(fg_color="transparent")
        self.task2_button.configure(fg_color="transparent")
        self.task3_button.configure(fg_color="transparent")

    def show_task_1(self):
        self.main_page.grid_remove()
        self.task1_page.grid()
        self.task2_page.grid_remove()
        self.task3_page.grid_remove()
        self.main_menu_button.configure(fg_color="transparent")
        self.task1_button.configure(fg_color="#244B50")
        self.task2_button.configure(fg_color="transparent")
        self.task3_button.configure(fg_color="transparent")
        
    def show_task_2(self):
        self.main_page.grid_remove()
        self.task1_page.grid_remove()
        self.task2_page.grid()
        self.task3_page.grid_remove()
        self.main_menu_button.configure(fg_color="transparent")
        self.task1_button.configure(fg_color="transparent")
        self.task2_button.configure(fg_color="#244B50")
        self.task3_button.configure(fg_color="transparent")

    def show_task_3(self):
        self.main_page.grid_remove()
        self.task1_page.grid_remove()
        self.task2_page.grid_remove()
        self.task3_page.grid()
        self.main_menu_button.configure(fg_color="transparent")
        self.task1_button.configure(fg_color="transparent")
        self.task2_button.configure(fg_color="transparent")
        self.task3_button.configure(fg_color="#244B50")
