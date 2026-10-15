import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from simulations.task1.simulation import Simulation


class Task1Page(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.graph_canvas = None
        self.graph_figure = None

        customtkinter.CTkLabel(
            self,
            text="Task 1",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 16), sticky="w")

        controls = customtkinter.CTkFrame(
            self,
            fg_color="#17232D",
            corner_radius=8,
        )
        controls.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))

        customtkinter.CTkLabel(
            controls,
            text="Customers",
            text_color="#A9B8C3",
        ).grid(row=0, column=0, padx=(14, 8), pady=12)
        self.customer_count_entry = customtkinter.CTkEntry(controls, width=76)
        self.customer_count_entry.insert(0, "6")
        self.customer_count_entry.grid(row=0, column=1, padx=(0, 18), pady=12)

        customtkinter.CTkLabel(
            controls,
            text="Servers",
            text_color="#A9B8C3",
        ).grid(row=0, column=2, padx=(0, 8), pady=12)
        customtkinter.CTkLabel(
            controls,
            text="1",
            text_color="#F4F7F9",
            width=76,
        ).grid(row=0, column=3, padx=(0, 18), pady=12)

        customtkinter.CTkButton(
            controls,
            text="Run simulation",
            command=self.run_simulation,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=0, column=4, padx=(0, 14), pady=12)

        self.status_label = customtkinter.CTkLabel(
            controls,
            text="",
            text_color="#A9B8C3",
            anchor="w",
        )
        self.status_label.grid(row=1, column=0, columnspan=5, padx=14, pady=(0, 8), sticky="ew")

        self.results = customtkinter.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.results.grid(row=2, column=0, sticky="nsew", padx=10)
        self.results.grid_columnconfigure((0, 1), weight=1)

        customtkinter.CTkLabel(
            self.results,
            text="Generated values",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=2, padx=8, pady=(4, 8), sticky="w")

        interarrival_panel = self.create_value_panel(
            self.results,
            "Inter-arrival times",
            "Random numbers: -\nGenerated times: -",
        )
        interarrival_panel.grid(row=1, column=0, padx=(0, 6), sticky="ew")
        self.interarrival_values_label = interarrival_panel.value_label

        service_panel = self.create_value_panel(
            self.results,
            "Service times",
            "Random numbers: -\nGenerated times: -",
        )
        service_panel.grid(row=1, column=1, padx=(6, 0), sticky="ew")
        self.service_values_label = service_panel.value_label

        self.interarrival_probability_editor = self.create_probability_editor(
            self.results,
            "Inter-arrival distribution",
            (0.125,) * 8,
            column=0,
            digits=3,
        )
        self.service_probability_editor = self.create_probability_editor(
            self.results,
            "Service-time distribution",
            (0.10, 0.20, 0.30, 0.25, 0.10, 0.05),
            column=1,
            digits=2,
        )
        self.probability_editors = (
            self.interarrival_probability_editor,
            self.service_probability_editor,
        )
        self.update_probability_totals()
        self.update_probability_totals()

        customtkinter.CTkLabel(
            self.results,
            text="Schedule",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=3, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        self.setup_schedule_table()

        customtkinter.CTkLabel(
            self.results,
            text="Customers in system, Q(t)",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=5, column=0, columnspan=2, padx=8, pady=(18, 8), sticky="w")

        self.graph_frame = customtkinter.CTkFrame(
            self.results,
            fg_color="#17232D",
            corner_radius=8,
        )
        self.graph_frame.grid(row=6, column=0, columnspan=2, padx=2, pady=(0, 16), sticky="ew")
        self.graph_frame.grid_columnconfigure(0, weight=1)

        self.setup_table_style()

    def create_value_panel(self, parent, title, value):
        panel = customtkinter.CTkFrame(parent, fg_color="#17232D", corner_radius=8)
        panel.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            panel,
            text=title,
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        panel.value_label = customtkinter.CTkLabel(
            panel,
            text=value,
            text_color="#A9B8C3",
            justify="left",
            anchor="w",
            wraplength=400,
        )
        panel.value_label.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="ew")
        return panel

    def create_probability_editor(self, parent, title, defaults, column, digits):
        panel = customtkinter.CTkFrame(parent, fg_color="#17232D", corner_radius=8)
        panel.grid(
            row=2,
            column=column,
            padx=(0, 6) if column == 0 else (6, 0),
            pady=(8, 18),
            sticky="nw",
        )

        editor = {
            "panel": panel,
            "digits": digits,
            "rows": [],
        }
        customtkinter.CTkLabel(
            panel,
            text=title,
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 6), sticky="w")

        customtkinter.CTkButton(
            panel,
            text="−",
            width=28,
            height=26,
            command=lambda: self.remove_probability_row(editor),
        ).grid(row=0, column=3, padx=(4, 2), pady=(8, 4))
        customtkinter.CTkButton(
            panel,
            text="+",
            width=28,
            height=26,
            command=lambda: self.add_probability_row(editor),
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=0, column=4, padx=(2, 10), pady=(8, 4))

        for index, heading in enumerate(("Time", "Probability", "Cumulative")):
            customtkinter.CTkLabel(
                panel,
                text=heading,
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color="#A9B8C3",
            ).grid(row=1, column=index, padx=12, pady=(0, 5), sticky="w")

        editor["total_label"] = customtkinter.CTkLabel(
            panel,
            text="",
            text_color="#9BC9B0",
        )
        for probability in defaults:
            self.add_probability_row(editor, probability)
        editor["total_label"].grid(
            row=len(editor["rows"]) + 2,
            column=0,
            columnspan=5,
            padx=12,
            pady=(6, 10),
            sticky="w",
        )
        self.update_probability_totals()
        return editor

    def add_probability_row(self, editor, probability=0):
        index = len(editor["rows"]) + 1
        row = index + 1
        digits = editor["digits"]
        panel = editor["panel"]

        time_label = customtkinter.CTkLabel(
            panel,
            text=str(index),
            text_color="#F4F7F9",
        )
        time_label.grid(row=row, column=0, padx=12, pady=3, sticky="w")

        probability_entry = customtkinter.CTkEntry(panel, width=90, height=28)
        probability_entry.insert(0, f"{probability:.{digits}f}")
        probability_entry.grid(row=row, column=1, padx=12, pady=3, sticky="w")
        probability_entry.bind("<KeyRelease>", self.update_probability_totals)

        cumulative_label = customtkinter.CTkLabel(
            panel,
            text="",
            text_color="#F4F7F9",
            width=80,
            anchor="w",
        )
        cumulative_label.grid(row=row, column=2, padx=12, pady=3, sticky="w")
        editor["rows"].append((time_label, probability_entry, cumulative_label))
        self.update_probability_totals()

    def remove_probability_row(self, editor):
        if len(editor["rows"]) <= 1:
            return
        for widget in editor["rows"].pop():
            widget.destroy()
        for index, (time_label, _, _) in enumerate(editor["rows"], start=1):
            time_label.configure(text=str(index))
        self.update_probability_totals()

    def read_probability_values(self, editor, name):
        try:
            probabilities = [float(row[1].get()) for row in editor["rows"]]
        except ValueError as error:
            raise ValueError(f"Enter a number in each {name} probability row.") from error

        if any(probability < 0 or probability > 1 for probability in probabilities):
            raise ValueError(f"{name.capitalize()} probabilities must be between 0 and 1.")
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-6):
            raise ValueError(f"{name.capitalize()} probabilities must add up to 1.")
        return probabilities

    def update_probability_totals(self, event=None):
        for editor in getattr(self, "probability_editors", ()):
            try:
                probabilities = [float(row[1].get()) for row in editor["rows"]]
            except ValueError:
                for _, _, cumulative_label in editor["rows"]:
                    cumulative_label.configure(text="-")
                editor["total_label"].configure(
                    text="Enter a number in each row.",
                    text_color="#E88B82",
                )
                continue

            cumulative_probability = 0
            for probability, (_, _, cumulative_label) in zip(
                probabilities, editor["rows"]
            ):
                cumulative_probability += probability
                cumulative_label.configure(
                    text=f"{cumulative_probability:.{editor['digits']}f}"
                )

            total = sum(probabilities)
            total_is_valid = math.isclose(total, 1.0, abs_tol=1e-6)
            editor["total_label"].configure(
                text=f"Total probability: {total:.{editor['digits']}f}"
                + ("" if total_is_valid else " (must equal 1)"),
                text_color="#9BC9B0" if total_is_valid else "#E88B82",
            )

    def setup_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Task1.Treeview",
            background="#17232D",
            foreground="#F4F7F9",
            fieldbackground="#17232D",
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Task1.Treeview.Heading",
            background="#244B50",
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Task1.Treeview",
            background=[("selected", "#2E5D62")],
            foreground=[("selected", "#FFFFFF")],
        )

    def setup_schedule_table(self):
        table_frame = customtkinter.CTkFrame(
            self.results,
            fg_color="#17232D",
            corner_radius=8,
        )
        table_frame.grid(row=4, column=0, columnspan=2, padx=2, sticky="ew")
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "customer",
            "interarrival",
            "arrival",
            "service_begins",
            "service_time",
            "service_ends",
        )
        self.schedule_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=6,
            style="Task1.Treeview",
        )
        headings = (
            "Customer",
            "Inter-arrival",
            "Arrival",
            "Service begins",
            "Service time",
            "Service ends",
        )
        widths = (78, 110, 92, 130, 108, 110)
        for column, heading, width in zip(columns, headings, widths):
            self.schedule_table.heading(column, text=heading)
            self.schedule_table.column(column, width=width, minwidth=65, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.schedule_table.yview,
        )
        self.schedule_table.configure(yscrollcommand=scrollbar.set)
        self.schedule_table.grid(row=0, column=0, sticky="ew", padx=(8, 0), pady=8)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)

    def run_simulation(self):
        try:
            num_customers = int(self.customer_count_entry.get())
            if num_customers < 1:
                raise ValueError("Customers must be at least 1.")
            interarrival_probabilities = self.read_probability_values(
                self.interarrival_probability_editor,
                "inter-arrival",
            )
            service_probabilities = self.read_probability_values(
                self.service_probability_editor,
                "service-time",
            )
            simulation = Simulation(
                num_customers,
                interarrival_probabilities,
                service_probabilities,
            )
            simulation.run()
        except ValueError as error:
            self.status_label.configure(text=str(error), text_color="#E88B82")
            return

        self.update_generated_values(simulation)
        self.update_schedule_table(simulation)
        self.update_graph(simulation)
        self.status_label.configure(
            text=f"Simulation complete: {num_customers} customers, 1 server",
            text_color="#9BC9B0",
        )

    def update_generated_values(self, simulation):
        interarrival_random_numbers = ", ".join(
            f"{number:.4f}" for number in simulation.interarrival_random_numbers
        )
        service_random_numbers = ", ".join(
            f"{number:.4f}" for number in simulation.service_random_numbers
        )
        self.interarrival_values_label.configure(
            text=(
                f"Random numbers: {interarrival_random_numbers}\n"
                f"Generated times: {simulation.interarrival_times}"
            )
        )
        self.service_values_label.configure(
            text=(
                f"Random numbers: {service_random_numbers}\n"
                f"Generated times: {simulation.service_times}"
            )
        )

    def update_schedule_table(self, simulation):
        for row in self.schedule_table.get_children():
            self.schedule_table.delete(row)

        for customer in simulation.customers:
            self.schedule_table.insert(
                "",
                "end",
                values=(
                    customer.number,
                    "-" if customer.interarrival_time is None else customer.interarrival_time,
                    customer.arrival_time,
                    customer.service_begins,
                    customer.service_time,
                    customer.service_ends,
                ),
            )

    def update_graph(self, simulation):
        if self.graph_canvas is not None:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_figure.clear()

        figure, axes = simulation.create_system_population_graph()
        figure.set_size_inches(8.5, 3.8)
        figure.set_facecolor("#17232D")
        axes.set_facecolor("#17232D")
        axes.title.set_color("#F4F7F9")
        axes.xaxis.label.set_color("#F4F7F9")
        axes.yaxis.label.set_color("#F4F7F9")
        axes.tick_params(colors="#A9B8C3")
        for spine in axes.spines.values():
            spine.set_color("#718492")

        self.graph_figure = figure
        self.graph_canvas = FigureCanvasTkAgg(figure, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
