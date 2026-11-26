import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from simulations.task4 import rngs
from simulations.task5.simulation import (
    Simulation,
    STOP_AFTER_JOBS,
    STOP_AFTER_RUNTIME,
)


TERMINAL_COUNTS = (10, 20, 30, 40, 50, 60, 70, 80)
RESPONSE_TIME_LIMIT = 30.0


class Task5Page(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.expanded_table_window = None
        self.expanded_table = None

        customtkinter.CTkLabel(
            self,
            text="Task 5 — Time-Shared Computer",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 12), sticky="w")

        self.content = customtkinter.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=10)
        self.content.grid_columnconfigure((0, 1), weight=1)

        self.create_inputs_panel()
        self.create_performance_panel()
        self.create_response_table_panel()
        self.create_required_cases_panel()
        self.create_required_cases_graph_panel()
        self.setup_table_style()
        self.after_idle(self.analyze_required_cases)

    def create_inputs_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=2,
            pady=(2, 10),
            sticky="ew",
        )
        for column in range(3):
            panel.grid_columnconfigure(column, weight=1, uniform="task5_inputs")

        customtkinter.CTkLabel(
            panel,
            text="Simulation inputs",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=3, padx=14, pady=(12, 4), sticky="w")

        self.input_entries = {}
        input_fields = (
            ("Thinking time distribution mean (s)", "think_time_mean", "25"),
            ("Service time distribution mean (s)", "service_time_mean", "0.8"),
            ("Quantum time (s)", "quantum_time", "0.1"),
            ("Stopping condition", "stopping_condition", STOP_AFTER_JOBS),
            ("Stopping value", "stopping_value", "1000"),
        )
        for field_index, (label, name, default) in enumerate(input_fields):
            row = 1 + field_index // 3
            column = field_index % 3
            group = customtkinter.CTkFrame(panel, fg_color="transparent")
            group.grid(
                row=row,
                column=column,
                padx=(
                    14 if column == 0 else 6,
                    14 if column == 2 else 6,
                ),
                pady=(6, 8),
                sticky="ew",
            )
            group.grid_columnconfigure(0, weight=1)
            input_label = customtkinter.CTkLabel(
                group,
                text=label,
                text_color="#A9B8C3",
                anchor="w",
            )
            input_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

            if name == "stopping_condition":
                self.stopping_condition_menu = customtkinter.CTkOptionMenu(
                    group,
                    values=(STOP_AFTER_JOBS, STOP_AFTER_RUNTIME),
                    command=self.update_stopping_value_label,
                    height=32,
                )
                self.stopping_condition_menu.set(default)
                self.stopping_condition_menu.grid(
                    row=1,
                    column=0,
                    sticky="ew",
                )
            else:
                entry = customtkinter.CTkEntry(group, height=32)
                entry.insert(0, default)
                entry.grid(row=1, column=0, sticky="ew")
                self.input_entries[name] = entry
                if name == "stopping_value":
                    self.stopping_value_label = input_label

        customtkinter.CTkButton(
            panel,
            text="Analyze required cases",
            command=self.analyze_required_cases,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=3, column=0, padx=14, pady=(4, 8), sticky="w")
        self.update_stopping_value_label(self.stopping_condition_menu.get())

        self.status_label = customtkinter.CTkLabel(
            panel,
            text=(
                "Think/service times use the shared exponential values from Task 4. "
                "Swap time = 0.015 s."
            ),
            text_color="#A9B8C3",
            anchor="w",
        )
        self.status_label.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=(6, 14),
            pady=(4, 8),
            sticky="ew",
        )

    def update_stopping_value_label(self, stopping_condition):
        if stopping_condition == STOP_AFTER_JOBS:
            label_text = "Number of jobs"
        else:
            label_text = "CPU run time (s)"
        self.stopping_value_label.configure(text=label_text)

    def create_performance_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 10),
            sticky="ew",
        )
        for column in range(4):
            panel.grid_columnconfigure(column, weight=1)

        customtkinter.CTkLabel(
            panel,
            text=f"Simulation performance ({TERMINAL_COUNTS[0]} terminals)",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=4, padx=12, pady=(10, 6), sticky="w")

        measures = (
            "Average response time (s)",
            "Time-average queue length",
            "CPU utilization",
            "Total simulation time (s)",
        )
        self.performance_labels = []
        for column, measure in enumerate(measures):
            customtkinter.CTkLabel(
                panel,
                text=measure,
                text_color="#A9B8C3",
            ).grid(row=1, column=column, padx=12, pady=(0, 4), sticky="w")
            value_label = customtkinter.CTkLabel(
                panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            value_label.grid(
                row=2,
                column=column,
                padx=12,
                pady=(0, 12),
                sticky="w",
            )
            self.performance_labels.append(value_label)

    def create_response_table_panel(self):
        customtkinter.CTkLabel(
            self.content,
            text=f"Completed-job response times ({TERMINAL_COUNTS[0]} terminals)",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=2, column=0, padx=8, pady=(4, 8), sticky="w")

        customtkinter.CTkButton(
            self.content,
            text="Expand table",
            command=self.open_expanded_table,
            height=32,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=2, column=1, padx=8, pady=(4, 8), sticky="e")

        table_frame = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        table_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 10),
            sticky="ew",
        )
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        self.simulation_table = self.create_response_table(table_frame, height=10)

    def create_required_cases_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 14),
            sticky="ew",
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        customtkinter.CTkLabel(
            panel,
            text="Required cases",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

        self.case_table = ttk.Treeview(
            panel,
            columns=(
                "terminals",
                "response_time",
                "queue_length",
                "cpu_utilization",
            ),
            show="headings",
            height=8,
            style="Task5.Treeview",
        )
        headings = (
            ("terminals", "Terminals", 120),
            ("response_time", "Average response time (s)", 220),
            ("queue_length", "Time-average queue length", 220),
            ("cpu_utilization", "CPU utilization", 160),
        )
        for column_name, heading, width in headings:
            self.case_table.heading(column_name, text=heading)
            self.case_table.column(
                column_name,
                width=width,
                minwidth=80,
                anchor="center",
                stretch=True,
            )
        self.case_table.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")

        self.maximum_terminals_label = customtkinter.CTkLabel(
            panel,
            text="Maximum terminals at average response time <= 30 s: -",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color="#F4F7F9",
            anchor="w",
        )
        self.maximum_terminals_label.grid(
            row=2,
            column=0,
            padx=12,
            pady=(0, 10),
            sticky="ew",
        )

    def create_required_cases_graph_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 14),
            sticky="ew",
        )
        panel.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            panel,
            text="Required cases: response time by terminal count",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.case_graph_figure = Figure(
            figsize=(8.5, 3.8),
            dpi=100,
            facecolor="#17232D",
        )
        self.case_graph_axes = self.case_graph_figure.add_subplot(111)
        self.case_graph_canvas = FigureCanvasTkAgg(
            self.case_graph_figure,
            master=panel,
        )
        self.case_graph_canvas.get_tk_widget().grid(
            row=1,
            column=0,
            padx=8,
            pady=(0, 8),
            sticky="ew",
        )

    def create_response_table(self, parent, height=20):
        columns = ("job_number", "response_time")
        table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Task5.Treeview",
            height=height,
        )
        table.heading("job_number", text="Completed job")
        table.heading("response_time", text="Response time (s)")
        table.column("job_number", width=180, minwidth=100, anchor="center")
        table.column("response_time", width=220, minwidth=140, anchor="center")
        table.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        vertical_scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=table.yview,
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        table.configure(yscrollcommand=vertical_scrollbar.set)
        return table

    def setup_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Task5.Treeview",
            background="#17232D",
            foreground="#F4F7F9",
            fieldbackground="#17232D",
            font=("Segoe UI", 12),
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Task5.Treeview.Heading",
            background="#244B50",
            foreground="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
        )
        style.map(
            "Task5.Treeview",
            background=[("selected", "#2E5D62")],
            foreground=[("selected", "#FFFFFF")],
        )

    def read_inputs(self):
        try:
            values = {
                "think_time_mean": float(
                    self.input_entries["think_time_mean"].get()
                ),
                "service_time_mean": float(
                    self.input_entries["service_time_mean"].get()
                ),
                "quantum_time": float(
                    self.input_entries["quantum_time"].get()
                ),
                "stopping_condition": self.stopping_condition_menu.get(),
            }
            if values["stopping_condition"] == STOP_AFTER_JOBS:
                values["stopping_value"] = int(
                    self.input_entries["stopping_value"].get()
                )
            elif values["stopping_condition"] == STOP_AFTER_RUNTIME:
                values["stopping_value"] = float(
                    self.input_entries["stopping_value"].get()
                )
            else:
                raise ValueError("Select a valid stopping condition.")
        except ValueError as error:
            raise ValueError("Enter valid values for all simulation inputs.") from error

        for field_name in (
            "think_time_mean",
            "service_time_mean",
            "quantum_time",
            "stopping_value",
        ):
            if not math.isfinite(values[field_name]) or values[field_name] <= 0:
                raise ValueError("Simulation input values must be greater than 0.")
        if rngs.generator != rngs.Generator.EXPONENTIAL:
            raise ValueError(
                "Select the EXPONENTIAL generator in the main menu first."
            )
        if len(rngs.random_numbers) < 2:
            raise ValueError(
                "Generate at least two shared random numbers in Task 4 first."
            )
        return values

    def create_simulation(self, number_of_terminals, values):
        simulation = Simulation(
            number_of_terminals=number_of_terminals,
            think_time_mean=values["think_time_mean"],
            service_time_mean=values["service_time_mean"],
            quantum_time=values["quantum_time"],
            stopping_condition=values["stopping_condition"],
            stopping_value=values["stopping_value"],
        )
        return simulation

    def analyze_required_cases(self):
        try:
            values = self.read_inputs()
        except ValueError as error:
            self.status_label.configure(text=str(error), text_color="#E88B82")
            return

        self.status_label.configure(
            text="Analyzing required cases and terminal limit...",
            text_color="#A9B8C3",
        )
        self.update_idletasks()
        self.case_table.delete(*self.case_table.get_children())
        case_results = {}

        for number_of_terminals in TERMINAL_COUNTS:
            simulation = self.create_simulation(number_of_terminals, values)
            result = simulation.run()
            case_results[number_of_terminals] = result
            if number_of_terminals == TERMINAL_COUNTS[0]:
                measure_values = (
                    f"{result['avg_response_time']:.3f}",
                    f"{result['avg_queue_length']:.3f}",
                    f"{result['cpu_utilization']:.3f}",
                    f"{result['total_sim_time']:.3f}",
                )
                for value_label, value in zip(
                    self.performance_labels,
                    measure_values,
                ):
                    value_label.configure(text=value)
                self.display_response_times(simulation.response_times)
                self.refresh_expanded_table()
            self.case_table.insert(
                "",
                "end",
                values=(
                    number_of_terminals,
                    f"{result['avg_response_time']:.3f}",
                    f"{result['avg_queue_length']:.3f}",
                    f"{result['cpu_utilization']:.3f}",
                ),
            )

        maximum_terminals = None
        for number_of_terminals in range(1, 100):
            if number_of_terminals not in case_results:
                simulation = self.create_simulation(number_of_terminals, values)
                case_results[number_of_terminals] = simulation.run()
            if (
                case_results[number_of_terminals]["avg_response_time"]
                > RESPONSE_TIME_LIMIT
            ):
                maximum_terminals = number_of_terminals - 1
                break

        self.update_required_cases_graph(case_results)

        if maximum_terminals is None:
            result_text = "No limit found below 100 terminals."
        else:
            result_text = (
                f"Maximum terminals at average response time <= "
                f"{RESPONSE_TIME_LIMIT:.0f} s: {maximum_terminals}"
            )
        self.maximum_terminals_label.configure(text=result_text)
        self.status_label.configure(
            text="Analysis complete.",
            text_color="#9BC9B0",
        )

    def update_required_cases_graph(self, case_results):
        axes = self.case_graph_axes
        axes.clear()
        axes.set_facecolor("#17232D")
        axes.set_title(
            "Average response time by number of terminals",
            color="#F4F7F9",
        )
        axes.set_xlabel("Number of terminals", color="#F4F7F9")
        axes.set_ylabel("Average response time (s)", color="#F4F7F9")
        axes.tick_params(colors="#A9B8C3")
        axes.grid(color="#2B3C4A")
        for spine in axes.spines.values():
            spine.set_color("#718492")

        if case_results:
            response_times = [
                case_results[number_of_terminals]["avg_response_time"]
                for number_of_terminals in TERMINAL_COUNTS
            ]
            axes.plot(
                TERMINAL_COUNTS,
                response_times,
                color="#69C3BD",
                marker="o",
                label="Average response time",
            )
            axes.axhline(
                RESPONSE_TIME_LIMIT,
                color="#E88B82",
                linestyle="--",
                label=f"{RESPONSE_TIME_LIMIT:.0f} s limit",
            )
            legend = axes.legend()
            legend.get_frame().set_facecolor("#17232D")
            for label in legend.get_texts():
                label.set_color("#F4F7F9")

        self.case_graph_canvas.draw()

    def display_response_times(self, response_times):
        self.simulation_table.delete(*self.simulation_table.get_children())
        for job_number, response_time in enumerate(response_times, start=1):
            self.simulation_table.insert(
                "",
                "end",
                values=(job_number, f"{response_time:.6f}"),
            )

    def open_expanded_table(self):
        if self.expanded_table_window is not None:
            if self.expanded_table_window.winfo_exists():
                self.expanded_table_window.focus_force()
                return

        window = tk.Toplevel(self)
        window.title("Task 5 — Completed-job response times")
        window.configure(bg="#101820")
        window.attributes("-fullscreen", True)
        window.bind("<Escape>", self.close_expanded_table)
        window.protocol("WM_DELETE_WINDOW", self.close_expanded_table)
        self.expanded_table_window = window

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        header = customtkinter.CTkFrame(
            window,
            fg_color="#101820",
            corner_radius=0,
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=12)
        header.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            header,
            text="Task 5 — Completed-job response times",
            font=customtkinter.CTkFont(size=22, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, sticky="w")
        customtkinter.CTkButton(
            header,
            text="Close  (Esc)",
            command=self.close_expanded_table,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=0, column=1, sticky="e")

        table_frame = customtkinter.CTkFrame(
            window,
            fg_color="#17232D",
            corner_radius=8,
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        self.expanded_table = self.create_response_table(table_frame)
        self.refresh_expanded_table()

    def close_expanded_table(self, event=None):
        if self.expanded_table_window is not None:
            if self.expanded_table_window.winfo_exists():
                self.expanded_table_window.destroy()
        self.expanded_table_window = None
        self.expanded_table = None

    def refresh_expanded_table(self):
        if self.expanded_table is None or not self.expanded_table.winfo_exists():
            return
        self.expanded_table.delete(*self.expanded_table.get_children())
        for item in self.simulation_table.get_children():
            self.expanded_table.insert(
                "",
                "end",
                values=self.simulation_table.item(item, "values"),
            )
import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from simulations.task4 import rngs
from simulations.task5.simulation import (
    Simulation,
    STOP_AFTER_JOBS,
    STOP_AFTER_RUNTIME,
)


TERMINAL_COUNTS = (10, 20, 30, 40, 50, 60, 70, 80)
RESPONSE_TIME_LIMIT = 30.0


class Task5Page(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.expanded_table_window = None
        self.expanded_table = None

        customtkinter.CTkLabel(
            self,
            text="Task 5 — Time-Shared Computer",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 12), sticky="w")

        self.content = customtkinter.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=10)
        self.content.grid_columnconfigure((0, 1), weight=1)

        self.create_inputs_panel()
        self.create_performance_panel()
        self.create_response_table_panel()
        self.create_required_cases_panel()
        self.create_required_cases_graph_panel()
        self.setup_table_style()
        self.after_idle(self.analyze_required_cases)

    def create_inputs_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=2,
            pady=(2, 10),
            sticky="ew",
        )
        for column in range(3):
            panel.grid_columnconfigure(column, weight=1, uniform="task5_inputs")

        customtkinter.CTkLabel(
            panel,
            text="Simulation inputs",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=3, padx=14, pady=(12, 4), sticky="w")

        self.input_entries = {}
        input_fields = (
            ("Thinking time distribution mean (s)", "think_time_mean", "25"),
            ("Service time distribution mean (s)", "service_time_mean", "0.8"),
            ("Quantum time (s)", "quantum_time", "0.1"),
            ("Stopping condition", "stopping_condition", STOP_AFTER_JOBS),
            ("Stopping value", "stopping_value", "1000"),
        )
        for field_index, (label, name, default) in enumerate(input_fields):
            row = 1 + field_index // 3
            column = field_index % 3
            group = customtkinter.CTkFrame(panel, fg_color="transparent")
            group.grid(
                row=row,
                column=column,
                padx=(
                    14 if column == 0 else 6,
                    14 if column == 2 else 6,
                ),
                pady=(6, 8),
                sticky="ew",
            )
            group.grid_columnconfigure(0, weight=1)
            input_label = customtkinter.CTkLabel(
                group,
                text=label,
                text_color="#A9B8C3",
                anchor="w",
            )
            input_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

            if name == "stopping_condition":
                self.stopping_condition_menu = customtkinter.CTkOptionMenu(
                    group,
                    values=(STOP_AFTER_JOBS, STOP_AFTER_RUNTIME),
                    command=self.update_stopping_value_label,
                    height=32,
                )
                self.stopping_condition_menu.set(default)
                self.stopping_condition_menu.grid(
                    row=1,
                    column=0,
                    sticky="ew",
                )
            else:
                entry = customtkinter.CTkEntry(group, height=32)
                entry.insert(0, default)
                entry.grid(row=1, column=0, sticky="ew")
                self.input_entries[name] = entry
                if name == "stopping_value":
                    self.stopping_value_label = input_label

        customtkinter.CTkButton(
            panel,
            text="Analyze required cases",
            command=self.analyze_required_cases,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=3, column=0, padx=14, pady=(4, 8), sticky="w")
        self.update_stopping_value_label(self.stopping_condition_menu.get())

        self.status_label = customtkinter.CTkLabel(
            panel,
            text=(
                "Think/service times use the shared exponential values from Task 4. "
                "Swap time = 0.015 s."
            ),
            text_color="#A9B8C3",
            anchor="w",
        )
        self.status_label.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=(6, 14),
            pady=(4, 8),
            sticky="ew",
        )

    def update_stopping_value_label(self, stopping_condition):
        if stopping_condition == STOP_AFTER_JOBS:
            label_text = "Number of jobs"
        else:
            label_text = "CPU run time (s)"
        self.stopping_value_label.configure(text=label_text)

    def create_performance_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 10),
            sticky="ew",
        )
        for column in range(4):
            panel.grid_columnconfigure(column, weight=1)

        customtkinter.CTkLabel(
            panel,
            text=f"Simulation performance ({TERMINAL_COUNTS[0]} terminals)",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=4, padx=12, pady=(10, 6), sticky="w")

        measures = (
            "Average response time (s)",
            "Time-average queue length",
            "CPU utilization",
            "Total simulation time (s)",
        )
        self.performance_labels = []
        for column, measure in enumerate(measures):
            customtkinter.CTkLabel(
                panel,
                text=measure,
                text_color="#A9B8C3",
            ).grid(row=1, column=column, padx=12, pady=(0, 4), sticky="w")
            value_label = customtkinter.CTkLabel(
                panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            value_label.grid(
                row=2,
                column=column,
                padx=12,
                pady=(0, 12),
                sticky="w",
            )
            self.performance_labels.append(value_label)

    def create_response_table_panel(self):
        customtkinter.CTkLabel(
            self.content,
            text=f"Completed-job response times ({TERMINAL_COUNTS[0]} terminals)",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=2, column=0, padx=8, pady=(4, 8), sticky="w")

        customtkinter.CTkButton(
            self.content,
            text="Expand table",
            command=self.open_expanded_table,
            height=32,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=2, column=1, padx=8, pady=(4, 8), sticky="e")

        table_frame = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        table_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 10),
            sticky="ew",
        )
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        self.simulation_table = self.create_response_table(table_frame, height=10)

    def create_required_cases_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 14),
            sticky="ew",
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        customtkinter.CTkLabel(
            panel,
            text="Required cases",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

        self.case_table = ttk.Treeview(
            panel,
            columns=(
                "terminals",
                "response_time",
                "queue_length",
                "cpu_utilization",
            ),
            show="headings",
            height=8,
            style="Task5.Treeview",
        )
        headings = (
            ("terminals", "Terminals", 120),
            ("response_time", "Average response time (s)", 220),
            ("queue_length", "Time-average queue length", 220),
            ("cpu_utilization", "CPU utilization", 160),
        )
        for column_name, heading, width in headings:
            self.case_table.heading(column_name, text=heading)
            self.case_table.column(
                column_name,
                width=width,
                minwidth=80,
                anchor="center",
                stretch=True,
            )
        self.case_table.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")

        self.maximum_terminals_label = customtkinter.CTkLabel(
            panel,
            text="Maximum terminals at average response time <= 30 s: -",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color="#F4F7F9",
            anchor="w",
        )
        self.maximum_terminals_label.grid(
            row=2,
            column=0,
            padx=12,
            pady=(0, 10),
            sticky="ew",
        )

    def create_required_cases_graph_panel(self):
        panel = customtkinter.CTkFrame(
            self.content,
            fg_color="#17232D",
            corner_radius=8,
        )
        panel.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 14),
            sticky="ew",
        )
        panel.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            panel,
            text="Required cases: response time by terminal count",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.case_graph_figure = Figure(
            figsize=(8.5, 3.8),
            dpi=100,
            facecolor="#17232D",
        )
        self.case_graph_axes = self.case_graph_figure.add_subplot(111)
        self.case_graph_canvas = FigureCanvasTkAgg(
            self.case_graph_figure,
            master=panel,
        )
        self.case_graph_canvas.get_tk_widget().grid(
            row=1,
            column=0,
            padx=8,
            pady=(0, 8),
            sticky="ew",
        )

    def create_response_table(self, parent, height=20):
        columns = ("job_number", "response_time")
        table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Task5.Treeview",
            height=height,
        )
        table.heading("job_number", text="Completed job")
        table.heading("response_time", text="Response time (s)")
        table.column("job_number", width=180, minwidth=100, anchor="center")
        table.column("response_time", width=220, minwidth=140, anchor="center")
        table.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        vertical_scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=table.yview,
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        table.configure(yscrollcommand=vertical_scrollbar.set)
        return table

    def setup_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Task5.Treeview",
            background="#17232D",
            foreground="#F4F7F9",
            fieldbackground="#17232D",
            font=("Segoe UI", 12),
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Task5.Treeview.Heading",
            background="#244B50",
            foreground="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            relief="flat",
        )
        style.map(
            "Task5.Treeview",
            background=[("selected", "#2E5D62")],
            foreground=[("selected", "#FFFFFF")],
        )

    def read_inputs(self):
        try:
            values = {
                "think_time_mean": float(
                    self.input_entries["think_time_mean"].get()
                ),
                "service_time_mean": float(
                    self.input_entries["service_time_mean"].get()
                ),
                "quantum_time": float(
                    self.input_entries["quantum_time"].get()
                ),
                "stopping_condition": self.stopping_condition_menu.get(),
            }
            if values["stopping_condition"] == STOP_AFTER_JOBS:
                values["stopping_value"] = int(
                    self.input_entries["stopping_value"].get()
                )
            elif values["stopping_condition"] == STOP_AFTER_RUNTIME:
                values["stopping_value"] = float(
                    self.input_entries["stopping_value"].get()
                )
            else:
                raise ValueError("Select a valid stopping condition.")
        except ValueError as error:
            raise ValueError("Enter valid values for all simulation inputs.") from error

        for field_name in (
            "think_time_mean",
            "service_time_mean",
            "quantum_time",
            "stopping_value",
        ):
            if not math.isfinite(values[field_name]) or values[field_name] <= 0:
                raise ValueError("Simulation input values must be greater than 0.")
        if rngs.generator != rngs.Generator.EXPONENTIAL:
            raise ValueError(
                "Select the EXPONENTIAL generator in the main menu first."
            )
        if len(rngs.random_numbers) < 2:
            raise ValueError(
                "Generate at least two shared random numbers in Task 4 first."
            )
        return values

    def create_simulation(self, number_of_terminals, values):
        simulation = Simulation(
            number_of_terminals=number_of_terminals,
            think_time_mean=values["think_time_mean"],
            service_time_mean=values["service_time_mean"],
            quantum_time=values["quantum_time"],
            stopping_condition=values["stopping_condition"],
            stopping_value=values["stopping_value"],
        )
        return simulation

    def analyze_required_cases(self):
        try:
            values = self.read_inputs()
        except ValueError as error:
            self.status_label.configure(text=str(error), text_color="#E88B82")
            return

        self.status_label.configure(
            text="Analyzing required cases and terminal limit...",
            text_color="#A9B8C3",
        )
        self.update_idletasks()
        self.case_table.delete(*self.case_table.get_children())
        case_results = {}

        for number_of_terminals in TERMINAL_COUNTS:
            simulation = self.create_simulation(number_of_terminals, values)
            result = simulation.run()
            case_results[number_of_terminals] = result
            if number_of_terminals == TERMINAL_COUNTS[0]:
                measure_values = (
                    f"{result['avg_response_time']:.3f}",
                    f"{result['avg_queue_length']:.3f}",
                    f"{result['cpu_utilization']:.3f}",
                    f"{result['total_sim_time']:.3f}",
                )
                for value_label, value in zip(
                    self.performance_labels,
                    measure_values,
                ):
                    value_label.configure(text=value)
                self.display_response_times(simulation.response_times)
                self.refresh_expanded_table()
            self.case_table.insert(
                "",
                "end",
                values=(
                    number_of_terminals,
                    f"{result['avg_response_time']:.3f}",
                    f"{result['avg_queue_length']:.3f}",
                    f"{result['cpu_utilization']:.3f}",
                ),
            )

        maximum_terminals = None
        for number_of_terminals in range(1, 100):
            if number_of_terminals not in case_results:
                simulation = self.create_simulation(number_of_terminals, values)
                case_results[number_of_terminals] = simulation.run()
            if (
                case_results[number_of_terminals]["avg_response_time"]
                > RESPONSE_TIME_LIMIT
            ):
                maximum_terminals = number_of_terminals - 1
                break

        self.update_required_cases_graph(case_results)

        if maximum_terminals is None:
            result_text = "No limit found below 100 terminals."
        else:
            result_text = (
                f"Maximum terminals at average response time <= "
                f"{RESPONSE_TIME_LIMIT:.0f} s: {maximum_terminals}"
            )
        self.maximum_terminals_label.configure(text=result_text)
        self.status_label.configure(
            text="Analysis complete.",
            text_color="#9BC9B0",
        )

    def update_required_cases_graph(self, case_results):
        axes = self.case_graph_axes
        axes.clear()
        axes.set_facecolor("#17232D")
        axes.set_title(
            "Average response time by number of terminals",
            color="#F4F7F9",
        )
        axes.set_xlabel("Number of terminals", color="#F4F7F9")
        axes.set_ylabel("Average response time (s)", color="#F4F7F9")
        axes.tick_params(colors="#A9B8C3")
        axes.grid(color="#2B3C4A")
        for spine in axes.spines.values():
            spine.set_color("#718492")

        if case_results:
            response_times = [
                case_results[number_of_terminals]["avg_response_time"]
                for number_of_terminals in TERMINAL_COUNTS
            ]
            axes.plot(
                TERMINAL_COUNTS,
                response_times,
                color="#69C3BD",
                marker="o",
                label="Average response time",
            )
            axes.axhline(
                RESPONSE_TIME_LIMIT,
                color="#E88B82",
                linestyle="--",
                label=f"{RESPONSE_TIME_LIMIT:.0f} s limit",
            )
            legend = axes.legend()
            legend.get_frame().set_facecolor("#17232D")
            for label in legend.get_texts():
                label.set_color("#F4F7F9")

        self.case_graph_canvas.draw()

    def display_response_times(self, response_times):
        self.simulation_table.delete(*self.simulation_table.get_children())
        for job_number, response_time in enumerate(response_times, start=1):
            self.simulation_table.insert(
                "",
                "end",
                values=(job_number, f"{response_time:.6f}"),
            )

    def open_expanded_table(self):
        if self.expanded_table_window is not None:
            if self.expanded_table_window.winfo_exists():
                self.expanded_table_window.focus_force()
                return

        window = tk.Toplevel(self)
        window.title("Task 5 — Completed-job response times")
        window.configure(bg="#101820")
        window.attributes("-fullscreen", True)
        window.bind("<Escape>", self.close_expanded_table)
        window.protocol("WM_DELETE_WINDOW", self.close_expanded_table)
        self.expanded_table_window = window

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        header = customtkinter.CTkFrame(
            window,
            fg_color="#101820",
            corner_radius=0,
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=12)
        header.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            header,
            text="Task 5 — Completed-job response times",
            font=customtkinter.CTkFont(size=22, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, sticky="w")
        customtkinter.CTkButton(
            header,
            text="Close  (Esc)",
            command=self.close_expanded_table,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=0, column=1, sticky="e")

        table_frame = customtkinter.CTkFrame(
            window,
            fg_color="#17232D",
            corner_radius=8,
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        self.expanded_table = self.create_response_table(table_frame)
        self.refresh_expanded_table()

    def close_expanded_table(self, event=None):
        if self.expanded_table_window is not None:
            if self.expanded_table_window.winfo_exists():
                self.expanded_table_window.destroy()
        self.expanded_table_window = None
        self.expanded_table = None

    def refresh_expanded_table(self):
        if self.expanded_table is None or not self.expanded_table.winfo_exists():
            return
        self.expanded_table.delete(*self.expanded_table.get_children())
        for item in self.simulation_table.get_children():
            self.expanded_table.insert(
                "",
                "end",
                values=self.simulation_table.item(item, "values"),
            )
