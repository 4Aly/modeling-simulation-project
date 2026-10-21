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

from simulations.task2.simulation import Simulation


class Task2Page(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.graph_canvas = None
        self.graph_figure = None
        self.server_busy_graph_canvas = None
        self.server_busy_graph_figure = None

        customtkinter.CTkLabel(
            self,
            text="Task 2",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 16), sticky="w")

        controls = customtkinter.CTkFrame(
            self,
            fg_color="#17232D",
            corner_radius=8,
        )
        controls.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))
        controls.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="task2_controls")

        customer_group = customtkinter.CTkFrame(controls, fg_color="transparent")
        customer_group.grid(row=0, column=0, sticky="ew", padx=(14, 6), pady=(12, 6))
        customer_group.grid_columnconfigure(0, weight=1)
        self.stopping_value_label = customtkinter.CTkLabel(
            customer_group,
            text="Customers",
            text_color="#A9B8C3",
            anchor="w",
        )
        self.stopping_value_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.customer_count_entry = customtkinter.CTkEntry(customer_group, width=76)
        self.customer_count_entry.insert(0, "6")
        self.customer_count_entry.grid(row=1, column=0, sticky="ew")

        server_group = customtkinter.CTkFrame(controls, fg_color="transparent")
        server_group.grid(row=0, column=1, sticky="ew", padx=6, pady=(12, 6))
        server_group.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            server_group,
            text="Servers",
            text_color="#A9B8C3",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.server_count_entry = customtkinter.CTkEntry(server_group, width=76)
        self.server_count_entry.insert(0, "2")
        self.server_count_entry.grid(row=1, column=0, sticky="ew")
        self.server_count_entry.bind("<Return>", self.refresh_service_probability_editors)
        self.server_count_entry.bind("<FocusOut>", self.refresh_service_probability_editors)

        selection_group = customtkinter.CTkFrame(controls, fg_color="transparent")
        selection_group.grid(row=0, column=2, sticky="ew", padx=6, pady=(12, 6))
        selection_group.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            selection_group,
            text="Selection Method",
            text_color="#A9B8C3",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.selection_method_menu = customtkinter.CTkOptionMenu(
            selection_group,
            values=("Highest Priority", "Random", "Least Utilization"),
            command=self.update_selection_method,
        )
        self.selection_method_menu.grid(row=1, column=0, sticky="ew")

        stopcondition_group = customtkinter.CTkFrame(controls, fg_color="transparent")
        stopcondition_group.grid(row=0, column=3, sticky="ew", padx=(6, 14), pady=(12, 6))
        stopcondition_group.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            stopcondition_group,
            text="Stopping Condition",
            text_color="#A9B8C3",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.stopcondition_method_menu = customtkinter.CTkOptionMenu(
            stopcondition_group,
            values=("No of Customers", "Time"),
            command=self.update_stopping_value_label,
        )
        self.stopcondition_method_menu.grid(row=1, column=0, sticky="ew")

        customtkinter.CTkButton(
            controls,
            text="Run simulation",
            command=self.run_simulation,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=1, column=0, padx=14, pady=(4, 12), sticky="w")

        self.status_label = customtkinter.CTkLabel(
            controls,
            text="",
            text_color="#A9B8C3",
            anchor="w",
        )
        self.status_label.grid(row=1, column=1, columnspan=3, padx=6, pady=(4, 12), sticky="ew")

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
            ((1, 0.25), (2, 0.40), (3, 0.20), (4, 0.15)),
            row=2,
            column=0,
            digits=3,
        )
        self.service_probability_container = customtkinter.CTkFrame(
            self.results,
            fg_color="transparent",
        )
        self.service_probability_container.grid(
            row=2,
            column=1,
            padx=(6, 0),
            pady=(8, 18),
            sticky="nw",
        )
        self.service_probability_container.grid_columnconfigure(0, weight=1)
        self.service_probability_editors = []
        self.refresh_service_probability_editors()
        self.probability_editors = [self.interarrival_probability_editor]
        self.probability_editors.extend(self.service_probability_editors)
        self.update_probability_totals()

        customtkinter.CTkLabel(
            self.results,
            text="Schedule",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=4, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        self.setup_statistics_panel()

        self.setup_schedule_table()

        customtkinter.CTkLabel(
            self.results,
            text="Customers in system, Q(t)",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=6, column=0, columnspan=2, padx=8, pady=(18, 8), sticky="w")

        self.graph_frame = customtkinter.CTkFrame(
            self.results,
            fg_color="#17232D",
            corner_radius=8,
        )
        self.graph_frame.grid(row=7, column=0, columnspan=2, padx=2, pady=(0, 16), sticky="ew")
        self.graph_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            self.results,
            text="Server busy time",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=8, column=0, columnspan=2, padx=8, pady=(4, 8), sticky="w")
        self.server_busy_graph_frame = customtkinter.CTkFrame(
            self.results,
            fg_color="#17232D",
            corner_radius=8,
        )
        self.server_busy_graph_frame.grid(
            row=9,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 16),
            sticky="ew",
        )
        self.server_busy_graph_frame.grid_columnconfigure(0, weight=1)

        self.setup_table_style()

    def update_stopping_value_label(self, selection):
        label = "Time" if selection == "Time" else "Customers"
        self.stopping_value_label.configure(text=label)

    def refresh_service_probability_editors(self, event=None):
        try:
            num_servers = int(self.server_count_entry.get())
        except ValueError:
            self.status_label.configure(
                text="Enter a whole number of servers.",
                text_color="#E88B82",
            )
            return
        if num_servers < 1:
            self.status_label.configure(
                text="Servers must be at least 1.",
                text_color="#E88B82",
            )
            return

        service_defaults = (
            ((2, 0.30), (3, 0.28), (4, 0.25), (5, 0.17)),
            ((3, 0.35), (4, 0.25), (5, 0.20), (6, 0.20)),
        )
        while len(self.service_probability_editors) > num_servers:
            editor = self.service_probability_editors.pop()
            editor["panel"].destroy()
        while len(self.service_probability_editors) < num_servers:
            server_number = len(self.service_probability_editors) + 1
            defaults = service_defaults[min(server_number - 1, len(service_defaults) - 1)]
            editor = self.create_probability_editor(
                self.service_probability_container,
                f"Server {server_number} service-time distribution",
                defaults,
                row=server_number - 1,
                column=0,
                digits=2,
                priority=server_number,
            )
            self.service_probability_editors.append(editor)

        self.probability_editors = [self.interarrival_probability_editor]
        self.probability_editors.extend(self.service_probability_editors)
        self.update_selection_method(self.selection_method_menu.get())
        if hasattr(self, "statistics_panel"):
            self.update_server_statistics_rows()
        self.update_probability_totals()

    def update_selection_method(self, selection):
        for editor in getattr(self, "service_probability_editors", ()):
            if selection == "Highest Priority":
                editor["priority_label"].grid()
                editor["priority_entry"].grid()
            else:
                editor["priority_label"].grid_remove()
                editor["priority_entry"].grid_remove()

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


    def setup_statistics_panel(self):
        self.statistics_panel = customtkinter.CTkFrame(
            self.results,
            fg_color="#17232D",
            corner_radius=8,
        )
        self.statistics_panel.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=2,
            pady=(0, 16),
            sticky="ew",
        )
        self.statistics_panel.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="task2_stats")

        self.statistics_heading = customtkinter.CTkLabel(
            self.statistics_panel,
            text="Simulation results",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color="#F4F7F9",
        )
        self.statistics_heading.grid(
            row=0,
            column=0,
            columnspan=4,
            padx=12,
            pady=(10, 8),
            sticky="w",
        )

        labels = (
            "Average waiting time",
            "Probability a customer waited",
        )
        self.stat_title_labels = []
        self.stat_value_labels = []
        self.stat_detail_labels = []
        for column, label_text in enumerate(labels):
            title_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text=label_text,
                text_color="#A9B8C3",
                wraplength=180,
                justify="left",
            )
            title_label.grid(row=1, column=column, padx=12, pady=(0, 4), sticky="w")
            self.stat_title_labels.append(title_label)
            value_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            value_label.grid(row=2, column=column, padx=12, pady=(0, 2), sticky="w")
            self.stat_value_labels.append(value_label)

            detail_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text="",
                text_color="#A9B8C3",
                font=customtkinter.CTkFont(size=11),
                wraplength=180,
                justify="left",
                anchor="w",
            )
            detail_label.grid(row=3, column=column, padx=12, pady=(0, 12), sticky="w")
            self.stat_detail_labels.append(detail_label)

        self.server_average_value_labels = []
        self.server_idle_probability_value_labels = []
        self.server_utilization_value_labels = []
        self.server_stats_rows = []
        self.update_server_statistics_rows()

    def update_server_statistics_rows(self):
        for widget in self.server_stats_rows:
            widget.destroy()
        self.server_stats_rows.clear()
        self.server_average_value_labels.clear()
        self.server_idle_probability_value_labels.clear()
        self.server_utilization_value_labels.clear()

        num_servers = len(self.service_probability_editors)
        section_heading = customtkinter.CTkLabel(
            self.statistics_panel,
            text="Per-server statistics",
            font=customtkinter.CTkFont(size=13, weight="bold"),
            text_color="#F4F7F9",
        )
        section_heading.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=12,
            pady=(0, 6),
            sticky="w",
        )
        self.server_stats_rows.append(section_heading)

        headings = (
            ("Server", "Server number"),
            ("Average service time", "Total service time / customers served"),
            ("Idle probability", "Total idle time / total run time"),
            ("Utilization", "Service time / total run time"),
        )
        for column, (heading, rule) in enumerate(headings):
            header = customtkinter.CTkLabel(
                self.statistics_panel,
                text=heading,
                text_color="#A9B8C3",
                font=customtkinter.CTkFont(size=12, weight="bold"),
            )
            header.grid(row=5, column=column, padx=12, pady=(0, 4), sticky="w")
            self.server_stats_rows.append(header)
            rule_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text=rule,
                text_color="#A9B8C3",
                font=customtkinter.CTkFont(size=10),
                wraplength=170,
                justify="left",
            )
            rule_label.grid(row=6, column=column, padx=12, pady=(0, 6), sticky="w")
            self.server_stats_rows.append(rule_label)

        for index in range(num_servers):
            row = index + 7
            server_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text=f"Server {index + 1}",
                text_color="#A9B8C3",
            )
            server_label.grid(row=row, column=0, padx=12, pady=(2, 6), sticky="w")
            value_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            value_label.grid(row=row, column=1, padx=12, pady=(2, 6), sticky="w")
            idle_probability_value_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            idle_probability_value_label.grid(
                row=row,
                column=2,
                padx=12,
                pady=(2, 6),
                sticky="w",
            )
            utilization_value_label = customtkinter.CTkLabel(
                self.statistics_panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            utilization_value_label.grid(
                row=row,
                column=3,
                padx=12,
                pady=(2, 6),
                sticky="w",
            )
            self.server_stats_rows.extend(
                (
                    server_label,
                    value_label,
                    idle_probability_value_label,
                    utilization_value_label,
                )
            )
            self.server_average_value_labels.append(value_label)
            self.server_idle_probability_value_labels.append(idle_probability_value_label)
            self.server_utilization_value_labels.append(utilization_value_label)

    def create_probability_editor(
        self,
        parent,
        title,
        defaults,
        row,
        column,
        digits,
        priority=None,
    ):
        panel = customtkinter.CTkFrame(parent, fg_color="#17232D", corner_radius=8)
        panel.grid(
            row=row,
            column=column,
            padx=2,
            pady=(0, 8),
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

        if priority is not None:
            editor["priority_label"] = customtkinter.CTkLabel(
                panel,
                text="Priority (lower number = higher priority)",
                text_color="#A9B8C3",
            )
            editor["priority_label"].grid(
                row=1,
                column=0,
                columnspan=3,
                padx=12,
                pady=(0, 4),
                sticky="w",
            )
            editor["priority_entry"] = customtkinter.CTkEntry(
                panel,
                width=70,
                height=28,
            )
            editor["priority_entry"].insert(0, str(priority))
            editor["priority_entry"].grid(row=1, column=3, padx=12, pady=(0, 4), sticky="w")

        for index, heading in enumerate(("Time", "Probability", "Cumulative")):
            customtkinter.CTkLabel(
                panel,
                text=heading,
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color="#A9B8C3",
            ).grid(row=2, column=index, padx=12, pady=(0, 5), sticky="w")

        editor["total_label"] = customtkinter.CTkLabel(
            panel,
            text="",
            text_color="#9BC9B0",
        )
        for time_value, probability in defaults:
            self.add_probability_row(editor, time_value, probability)
        editor["total_label"].grid(
            row=len(editor["rows"]) + 3,
            column=0,
            columnspan=5,
            padx=12,
            pady=(6, 10),
            sticky="w",
        )
        self.update_probability_totals()
        return editor

    def add_probability_row(self, editor, time_value=None, probability=0):
        row = len(editor["rows"]) + 3
        digits = editor["digits"]
        panel = editor["panel"]

        if time_value is None:
            existing_times = []
            for time_entry, _, _ in editor["rows"]:
                try:
                    existing_times.append(int(time_entry.get()))
                except ValueError:
                    continue
            time_value = max(existing_times, default=0) + 1
        time_entry = customtkinter.CTkEntry(panel, width=70, height=28)
        time_entry.insert(0, str(time_value))
        time_entry.grid(row=row, column=0, padx=12, pady=3, sticky="w")
        time_entry.bind("<KeyRelease>", self.update_probability_totals)

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
        editor["rows"].append((time_entry, probability_entry, cumulative_label))
        self.update_probability_totals()

    def remove_probability_row(self, editor):
        if len(editor["rows"]) <= 1:
            return
        for widget in editor["rows"].pop():
            widget.destroy()
        self.update_probability_totals()

    def read_probability_values(self, editor, name):
        try:
            times = [int(row[0].get()) for row in editor["rows"]]
            probabilities = [float(row[1].get()) for row in editor["rows"]]
        except ValueError as error:
            raise ValueError(f"Enter a whole time and a probability in each {name} row.") from error

        if any(time_value < 1 for time_value in times):
            raise ValueError(f"{name.capitalize()} times must be at least 1.")
        if len(set(times)) != len(times):
            raise ValueError(f"{name.capitalize()} times must be unique.")

        if any(probability < 0 or probability > 1 for probability in probabilities):
            raise ValueError(f"{name.capitalize()} probabilities must be between 0 and 1.")
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-6):
            raise ValueError(f"{name.capitalize()} probabilities must add up to 1.")
        return list(zip(times, probabilities))

    def update_probability_totals(self, event=None):
        for editor in getattr(self, "probability_editors", ()):
            try:
                times = [int(row[0].get()) for row in editor["rows"]]
                probabilities = [float(row[1].get()) for row in editor["rows"]]
            except ValueError:
                for _, _, cumulative_label in editor["rows"]:
                    cumulative_label.configure(text="-")
                editor["total_label"].configure(
                    text="Enter whole times and probabilities in each row.",
                    text_color="#E88B82",
                )
                continue

            if any(time_value < 1 for time_value in times) or len(set(times)) != len(times):
                editor["total_label"].configure(
                    text="Times must be positive and unique.",
                    text_color="#E88B82",
                )
                for _, _, cumulative_label in editor["rows"]:
                    cumulative_label.configure(text="-")
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
            font=("Segoe UI", 20),
            rowheight=40,
            borderwidth=0,
        )
        style.configure(
            "Task1.Treeview.Heading",
            background="#244B50",
            foreground="#FFFFFF",
            font=("Segoe UI", 20, "bold"),
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
            "server",
            "service_begins",
            "service_time",
            "service_ends",
            "time_in_queue",
        )
        self.schedule_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=1,
            style="Task1.Treeview",
        )
        headings = (
            "Cust. Number",
            "Inter-arrival time",
            "Arrival time",
            "Assigned server",
            "Service begin",
            "Service time",
            "Service end",
            "Time in queue",
        )
        widths = (105, 125, 105, 115, 115, 105, 105, 105)
        for column, heading, width in zip(columns, headings, widths):
            self.schedule_table.heading(column, text=heading)
            self.schedule_table.column(column, width=width, minwidth=65, anchor="center")

        self.schedule_table.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

    def run_simulation(self):
        try:
            num_customers = int(self.customer_count_entry.get())
            if num_customers < 1:
                raise ValueError("Customers must be at least 1.")
            num_servers = int(self.server_count_entry.get())
            if num_servers < 1:
                raise ValueError("Servers must be at least 1.")
            interarrival_probabilities = self.read_probability_values(
                self.interarrival_probability_editor,
                "inter-arrival",
            )
            if len(self.service_probability_editors) != num_servers:
                self.refresh_service_probability_editors()
            if len(self.service_probability_editors) != num_servers:
                raise ValueError("Enter a valid number of servers.")
            service_probabilities = [
                self.read_probability_values(editor, f"server {index} service-time")
                for index, editor in enumerate(self.service_probability_editors, start=1)
            ]
            server_priorities = None
            if self.selection_method_menu.get() == "Highest Priority":
                try:
                    server_priorities = [
                        int(editor["priority_entry"].get())
                        for editor in self.service_probability_editors
                    ]
                except ValueError as error:
                    raise ValueError("Enter a whole-number priority for each server.") from error
                if any(priority < 1 for priority in server_priorities):
                    raise ValueError("Server priorities must be at least 1.")
            simulation = Simulation(
                num_customers,
                interarrival_probabilities,
                service_probabilities,
                num_servers=num_servers,
                selection_method=self.selection_method_menu.get(),
                server_priorities=server_priorities,
            )
            simulation.run()
        except ValueError as error:
            self.status_label.configure(text=str(error), text_color="#E88B82")
            return

        self.update_generated_values(simulation)
        self.update_schedule_table(simulation)
        self.update_statistics(simulation)
        self.update_graph(simulation)
        self.update_server_busy_graph(simulation)
        self.status_label.configure(
            text=f"Simulation complete: {num_customers} customers, {num_servers} servers",
            text_color="#9BC9B0",
        )

    def update_statistics(self, simulation):
        customer_count = len(simulation.customers)
        values = (
            f"{simulation.average_waiting_time:.3f}",
            f"{simulation.probability_customer_waited:.3f}",
        )
        details = (
            f"{simulation.total_waiting_time:.3f} total wait / {customer_count} customers",
            f"{simulation.customers_who_waited} waited / {customer_count} customers",
        )
        for label, value, detail_label, detail in zip(
            self.stat_value_labels,
            values,
            self.stat_detail_labels,
            details,
        ):
            label.configure(text=value)
            detail_label.configure(text=detail)
        for label, server in zip(self.server_average_value_labels, simulation.servers):
            label.configure(text=f"{server.average_service_time:.3f}")
        for label, server in zip(
            self.server_idle_probability_value_labels,
            simulation.servers,
        ):
            label.configure(text=f"{server.idle_time_probability:.3f}")
        for label, server in zip(self.server_utilization_value_labels, simulation.servers):
            label.configure(text=f"{server.utilization:.3f}")

    def update_generated_values(self, simulation):
        interarrival_random_numbers = ", ".join(
            f"{number:.3f}" for number in simulation.interarrival_random_numbers
        )
        service_random_numbers = ", ".join(
            f"{number:.3f}" for number in simulation.service_random_numbers
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
                "Generated times by server: "
                + "; ".join(
                    f"Server {index}: {times}"
                    for index, times in enumerate(simulation.service_times_by_server, start=1)
                )
            )
        )

    def update_schedule_table(self, simulation):
        for row in self.schedule_table.get_children():
            self.schedule_table.delete(row)

        self.schedule_table.configure(height=max(1, len(simulation.customers)))
        for customer in simulation.customers:
            self.schedule_table.insert(
                "",
                "end",
                values=(
                    customer.number,
                    "-" if customer.interarrival_time is None else customer.interarrival_time,
                    customer.arrival_time,
                    customer.server_number,
                    customer.service_begins,
                    customer.service_time,
                    customer.service_ends,
                    customer.waiting_time,
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

    def update_server_busy_graph(self, simulation):
        if self.server_busy_graph_canvas is not None:
            self.server_busy_graph_canvas.get_tk_widget().destroy()
            self.server_busy_graph_figure.clear()

        figure, axes_list = simulation.create_server_busy_time_graph()
        figure.set_facecolor("#17232D")
        for axes in axes_list:
            axes.set_facecolor("#17232D")
            axes.title.set_color("#F4F7F9")
            axes.xaxis.label.set_color("#F4F7F9")
            axes.yaxis.label.set_color("#F4F7F9")
            axes.tick_params(colors="#A9B8C3")
            for spine in axes.spines.values():
                spine.set_color("#718492")

        figure.tight_layout(pad=2)
        self.server_busy_graph_figure = figure
        self.server_busy_graph_canvas = FigureCanvasTkAgg(
            figure,
            master=self.server_busy_graph_frame,
        )
        self.server_busy_graph_canvas.draw()
        self.server_busy_graph_canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=8,
        )
