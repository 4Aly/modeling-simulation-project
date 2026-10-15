import customtkinter


class Task1Page(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        customtkinter.CTkLabel(
            self,
            text="Task 1",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 20), sticky="w")

        task_panel = customtkinter.CTkFrame(
            self,
            fg_color="#1A2A35",
            corner_radius=12,
            border_width=1,
            border_color="#30475E",
        )
        task_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        task_panel.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            task_panel,
            text="Task 1 content",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        customtkinter.CTkLabel(
            task_panel,
            text=(
                "This is the dedicated space for Task 1.\n"
                "You can add the required calculations, simulations, or UI elements here."
            ),
            justify="left",
            wraplength=700,
            text_color="#A9B8C3",
            font=customtkinter.CTkFont(size=15),
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
