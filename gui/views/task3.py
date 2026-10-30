import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import customtkinter

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from simulations.task3.simulation import Simulation


class Task3Page(customtkinter.CTkFrame):
    TABLE_COLUMNS = (
        "day",
        "cycle",
        "day_within_cycle",
        "beginning_inventory",
        "demand_random_digit",
        "demand",
        "ending_inventory",
        "shortage_quantity",
        "order_quantity",
        "lead_time_random_digit",
        "lead_time",
        "days_until_order_arrives",
    )
    TABLE_HEADERS = (
        "Day",
        "Cycle",
        "Day in cycle",
        "Begin inv.",
        "Demand RNG",
        "Demand",
        "End inv.",
        "Shortage",
        "Order qty",
        "Lead RNG",
        "Lead time",
        "Days to arrival",
    )
    TABLE_COLUMN_WEIGHTS = (
        0.55,
        0.55,
        0.9,
        1.15,
        1.2,
        0.65,
        1.1,
        1.05,
        1.05,
        1.25,
        0.75,
        1.35,
    )

    def __init__(self, master):
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        customtkinter.CTkLabel(
            self,
            text="Task 3 — Inventory Simulation",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, padx=20, pady=(0, 12), sticky="w")

        self.content = customtkinter.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=10)
        self.content.grid_columnconfigure((0, 1), weight=1, uniform="task3_columns")

        self.create_inputs_panel()
        self.demand_editor = self.create_probability_editor(
            self.content,
            "Demand probability distribution",
            ((0, 0.10), (1, 0.25), (2, 0.35), (3, 0.21), (4, 0.09)),
            row=1,
            column=0,
        )
        self.lead_time_editor = self.create_probability_editor(
            self.content,
            "Lead-time probability distribution",
            ((1, 0.60), (2, 0.30), (3, 0.10)),
            row=1,
            column=1,
        )
        self.probability_editors = (self.demand_editor, self.lead_time_editor)
        self.update_probability_totals()

        self.expanded_table_window = None
        self.expanded_table = None
        self.create_results_panel()
        self.setup_table_style()

    def create_inputs_panel(self):
        panel = customtkinter.CTkFrame(self.content, fg_color="#17232D", corner_radius=8)
        panel.grid(row=0, column=0, columnspan=2, padx=2, pady=(2, 10), sticky="ew")
        for column in range(4):
            panel.grid_columnconfigure(column, weight=1, uniform="task3_inputs")

        customtkinter.CTkLabel(
            panel,
            text="System inputs",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=4, padx=14, pady=(12, 4), sticky="w")

        self.input_entries = {}
        self.input_labels = {}
        input_fields = (
            ("Order-up-to level (M)", "order_up_to_level", "11"),
            ("Review period (N)", "review_period", "5"),
            ("Number of days", "num_days", "25"),
            ("Beginning inventory", "beginning_inventory", "3"),
            ("First order arrives after (days)", "first_order_arrives_after", "2"),
            ("First order quantity", "first_order_quantity", "8"),
        )
        for index, (label, key, default) in enumerate(input_fields):
            row = 1 + index // 4
            column = index % 4
            group = customtkinter.CTkFrame(panel, fg_color="transparent")
            group.grid(
                row=row,
                column=column,
                padx=(14 if column == 0 else 6, 6 if column < 3 else 14),
                pady=(6, 8),
                sticky="ew",
            )
            group.grid_columnconfigure(0, weight=1)
            field_label = customtkinter.CTkLabel(
                group,
                text=label,
                text_color="#A9B8C3",
                anchor="w",
            )
            field_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
            entry = customtkinter.CTkEntry(group, height=32)
            entry.insert(0, default)
            entry.grid(row=1, column=0, sticky="ew")
            self.input_entries[key] = entry
            self.input_labels[key] = label

        self.run_button = customtkinter.CTkButton(
            panel,
            text="Run simulation",
            command=self.run_simulation,
            height=36,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        )
        self.run_button.grid(row=3, column=0, padx=14, pady=(4, 8), sticky="w")
        self.status_label = customtkinter.CTkLabel(
            panel,
            text="Configure the inputs and distributions, then run the simulation.",
            text_color="#A9B8C3",
            anchor="w",
        )
        self.status_label.grid(
            row=3,
            column=1,
            columnspan=3,
            padx=(6, 14),
            pady=(4, 8),
            sticky="ew",
        )

    def create_probability_editor(self, parent, title, defaults, row, column):
        panel = customtkinter.CTkFrame(parent, fg_color="#17232D", corner_radius=8)
        panel.grid(
            row=row,
            column=column,
            padx=(2, 6) if column == 0 else (6, 2),
            pady=(0, 10),
            sticky="nw",
        )
        editor = {"panel": panel, "rows": []}
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

        for index, heading in enumerate(("Value", "Probability", "Cumulative")):
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
        for value, probability in defaults:
            self.add_probability_row(editor, value, probability)
        editor["total_label"].grid(
            row=len(editor["rows"]) + 2,
            column=0,
            columnspan=5,
            padx=12,
            pady=(6, 10),
            sticky="w",
        )
        return editor

    def add_probability_row(self, editor, value=None, probability=0):
        if value is None:
            current_values = []
            for value_entry, _, _ in editor["rows"]:
                try:
                    current_values.append(int(value_entry.get()))
                except ValueError:
                    continue
            value = max(current_values, default=-1) + 1

        row = len(editor["rows"]) + 2
        value_entry = customtkinter.CTkEntry(editor["panel"], width=75, height=28)
        value_entry.insert(0, str(value))
        value_entry.grid(row=row, column=0, padx=12, pady=3, sticky="w")
        value_entry.bind("<KeyRelease>", self.update_probability_totals)

        probability_entry = customtkinter.CTkEntry(
            editor["panel"], width=90, height=28
        )
        probability_entry.insert(0, f"{probability:.2f}")
        probability_entry.grid(row=row, column=1, padx=12, pady=3, sticky="w")
        probability_entry.bind("<KeyRelease>", self.update_probability_totals)

        cumulative_label = customtkinter.CTkLabel(
            editor["panel"],
            text="",
            text_color="#F4F7F9",
            width=80,
            anchor="w",
        )
        cumulative_label.grid(row=row, column=2, padx=12, pady=3, sticky="w")
        editor["rows"].append((value_entry, probability_entry, cumulative_label))
        self.update_probability_totals()

    def remove_probability_row(self, editor):
        if len(editor["rows"]) <= 1:
            return
        for widget in editor["rows"].pop():
            widget.destroy()
        self.update_probability_totals()

    def read_probability_values(self, editor, name, minimum_value):
        try:
            entries = [
                (int(value_entry.get()), float(probability_entry.get()))
                for value_entry, probability_entry, _ in editor["rows"]
            ]
        except ValueError as error:
            raise ValueError(
                f"Enter a whole value and probability in each {name} row."
            ) from error

        values = [value for value, _ in entries]
        probabilities = [probability for _, probability in entries]
        if any(value < minimum_value for value in values):
            raise ValueError(
                f"{name.capitalize()} values must be at least {minimum_value}."
            )
        if len(values) != len(set(values)):
            raise ValueError(f"{name.capitalize()} values must be unique.")
        if any(
            not math.isfinite(probability) or probability < 0 or probability > 1
            for probability in probabilities
        ):
            raise ValueError(
                f"{name.capitalize()} probabilities must be between 0 and 1."
            )
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-6):
            raise ValueError(f"{name.capitalize()} probabilities must add up to 1.")
        return entries

    def update_probability_totals(self, event=None):
        for editor in getattr(self, "probability_editors", ()):
            try:
                values = [int(row[0].get()) for row in editor["rows"]]
                probabilities = [float(row[1].get()) for row in editor["rows"]]
            except ValueError:
                for _, _, cumulative_label in editor["rows"]:
                    cumulative_label.configure(text="-")
                editor["total_label"].configure(
                    text="Enter whole values and probabilities in each row.",
                    text_color="#E88B82",
                )
                continue

            total = 0.0
            for probability, (_, _, cumulative_label) in zip(
                probabilities, editor["rows"]
            ):
                total += probability
                cumulative_label.configure(text=f"{total:.2f}")

            valid_values = len(values) == len(set(values))
            valid_probabilities = all(
                math.isfinite(probability) and 0 <= probability <= 1
                for probability in probabilities
            )
            valid_total = math.isclose(total, 1.0, abs_tol=1e-6)
            is_valid = valid_values and valid_probabilities and valid_total
            editor["total_label"].configure(
                text=f"Total probability: {total:.2f}"
                + ("" if is_valid else " (values must be unique; total must equal 1)"),
                text_color="#9BC9B0" if is_valid else "#E88B82",
            )

    def create_results_panel(self):
        performance_panel = customtkinter.CTkFrame(
            self.content, fg_color="#17232D", corner_radius=8
        )
        performance_panel.grid(
            row=2, column=0, columnspan=2, padx=2, pady=(0, 10), sticky="ew"
        )
        performance_panel.grid_columnconfigure((0, 1), weight=1)
        customtkinter.CTkLabel(
            performance_panel,
            text="Performance measures",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        self.performance_labels = []
        measure_names = (
            "Ending inventory average",
            "Shortage quantity average",
        )
        for column, label_text in enumerate(measure_names):
            customtkinter.CTkLabel(
                performance_panel,
                text=label_text,
                text_color="#A9B8C3",
            ).grid(row=1, column=column, padx=12, pady=(0, 4), sticky="w")
            value_label = customtkinter.CTkLabel(
                performance_panel,
                text="-",
                font=customtkinter.CTkFont(size=18, weight="bold"),
                text_color="#F4F7F9",
            )
            value_label.grid(row=2, column=column, padx=12, pady=(0, 12), sticky="w")
            self.performance_labels.append(value_label)

        customtkinter.CTkLabel(
            self.content,
            text="Simulation table",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color="#F4F7F9",
        ).grid(row=3, column=0, padx=8, pady=(4, 8), sticky="w")
        customtkinter.CTkButton(
            self.content,
            text="Expand table",
            command=self.open_expanded_table,
            height=32,
            corner_radius=6,
            fg_color="#244B50",
            hover_color="#2E5D62",
        ).grid(row=3, column=1, padx=8, pady=(4, 8), sticky="e")

        table_frame = customtkinter.CTkFrame(
            self.content, fg_color="#17232D", corner_radius=8
        )
        table_frame.grid(
            row=4, column=0, columnspan=2, padx=2, pady=(0, 14), sticky="ew"
        )
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.simulation_table = ttk.Treeview(
            table_frame,
            columns=self.TABLE_COLUMNS,
            show="headings",
            height=12,
            style="Task3.Treeview",
        )
        self.configure_table_columns(self.simulation_table)
        self.simulation_table.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        vertical_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.simulation_table.yview
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.simulation_table.configure(yscrollcommand=vertical_scrollbar.set)

    def open_expanded_table(self):
        if self.expanded_table_window is not None:
            if self.expanded_table_window.winfo_exists():
                self.expanded_table_window.focus_force()
                return

        window = tk.Toplevel(self)
        window.title("Task 3 — Full Simulation Table")
        window.configure(bg="#101820")
        window.attributes("-fullscreen", True)
        window.bind("<Escape>", self.close_expanded_table)
        window.protocol("WM_DELETE_WINDOW", self.close_expanded_table)
        self.expanded_table_window = window

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        header = customtkinter.CTkFrame(window, fg_color="#101820", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=12)
        header.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            header,
            text="Task 3 — Simulation Table",
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
            window, fg_color="#17232D", corner_radius=8
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.expanded_table = ttk.Treeview(
            table_frame,
            columns=self.TABLE_COLUMNS,
            show="headings",
            style="Task3.Treeview",
        )
        self.configure_table_columns(self.expanded_table)
        self.expanded_table.grid(
            row=0, column=0, sticky="nsew", padx=(10, 0), pady=10
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.expanded_table.yview
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
        self.expanded_table.configure(yscrollcommand=vertical_scrollbar.set)
        self.refresh_expanded_table()

    def configure_table_columns(self, table):
        for column, heading in zip(self.TABLE_COLUMNS, self.TABLE_HEADERS):
            table.heading(column, text=heading)
            table.column(column, width=1, minwidth=1, anchor="center", stretch=True)
        table.bind(
            "<Configure>",
            lambda event: self.resize_table_columns(event.widget),
        )

    def resize_table_columns(self, table):
        available_width = max(1, table.winfo_width() - 4)
        total_weight = sum(self.TABLE_COLUMN_WEIGHTS)
        used_width = 0
        for index, (column, weight) in enumerate(
            zip(self.TABLE_COLUMNS, self.TABLE_COLUMN_WEIGHTS)
        ):
            if index == len(self.TABLE_COLUMNS) - 1:
                width = max(1, available_width - used_width)
            else:
                width = max(1, int(available_width * weight / total_weight))
                used_width += width
            table.column(column, width=width)

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

    def setup_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Task3.Treeview",
            background="#17232D",
            foreground="#F4F7F9",
            fieldbackground="#17232D",
            font=("Segoe UI", 12),
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Task3.Treeview.Heading",
            background="#244B50",
            foreground="#FFFFFF",
            font=("Segoe UI", 16, "bold"),
            relief="flat",
        )
        style.map(
            "Task3.Treeview",
            background=[("selected", "#2E5D62")],
            foreground=[("selected", "#FFFFFF")],
        )

    def run_simulation(self):
        try:
            values = {
                name: int(entry.get())
                for name, entry in self.input_entries.items()
            }
            for name in (
                "order_up_to_level",
                "beginning_inventory",
                "first_order_arrives_after",
                "first_order_quantity",
            ):
                if values[name] < 0:
                    raise ValueError(
                        f"{self.input_labels[name]} must be a non-negative whole number."
                    )
            for name in ("review_period", "num_days"):
                if values[name] < 1:
                    raise ValueError(
                        f"{self.input_labels[name]} must be a whole number greater than zero."
                    )
            demand_distribution = self.read_probability_values(
                self.demand_editor, "demand", minimum_value=0
            )
            lead_time_distribution = self.read_probability_values(
                self.lead_time_editor, "lead time", minimum_value=1
            )
            simulation = Simulation(
                order_up_to_level=values["order_up_to_level"],
                review_period=values["review_period"],
                demand_distribution=demand_distribution,
                lead_time_distribution=lead_time_distribution,
                num_days=values["num_days"],
                beginning_inventory=values["beginning_inventory"],
                first_order_arrives_after=values["first_order_arrives_after"],
                first_order_quantity=values["first_order_quantity"],
            )
            rows = simulation.run()
            measures = simulation.statistics()
        except ValueError as error:
            self.status_label.configure(
                text=str(error),
                text_color="#E88B82",
            )
            return

        self.performance_labels[0].configure(
            text=f"{measures['ending_inventory_average']:.3f}"
        )
        self.performance_labels[1].configure(
            text=f"{measures['shortage_quantity_average']:.3f}"
        )
        self.display_simulation_table(rows)
        self.refresh_expanded_table()
        self.status_label.configure(
            text=f"Simulation complete: {len(rows)} days.",
            text_color="#9BC9B0",
        )

    def display_simulation_table(self, days):
        self.simulation_table.delete(*self.simulation_table.get_children())
        for day in days:
            self.simulation_table.insert(
                "",
                "end",
                values=tuple(
                    "-"
                    if getattr(day, column) is None
                    or (
                        column == "lead_time_random_digit"
                        and not day.order_quantity
                    )
                    else getattr(day, column)
                    for column in self.TABLE_COLUMNS
                ),
            )
