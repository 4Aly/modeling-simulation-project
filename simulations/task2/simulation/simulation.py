import random

import matplotlib.pyplot as plt

from ..server import Server
from ..customer import Customer


class Simulation:
    def __init__(
        self,
        num_customers,
        interarrival_probabilities,
        service_probabilities,
        num_servers=1,
        selection_method="Highest Priority",
        server_priorities=None,
    ):
        self.random = random.Random()
        self.num_customers = num_customers
        self.num_servers = num_servers
        (
            self.interarrival_times_values,
            self.interarrival_probabilities,
        ) = self.normalize_distribution(interarrival_probabilities)
        normalized_service_distributions = tuple(
            self.normalize_distribution(distribution)
            for distribution in service_probabilities
        )
        self.service_time_values_by_server = tuple(
            distribution[0] for distribution in normalized_service_distributions
        )
        self.service_probabilities = tuple(
            distribution[1] for distribution in normalized_service_distributions
        )
        self.selection_method = selection_method
        self.server_priorities = server_priorities
        self.cumulative_interarrival_probabilities = self.make_cumulative_probabilities(
            self.interarrival_probabilities
        )
        self.cumulative_service_probabilities = tuple(
            self.make_cumulative_probabilities(probabilities)
            for probabilities in self.service_probabilities
        )
        self.interarrival_random_numbers = [
            round(self.random.random(), 3) for _ in range(num_customers)
        ]
        self.service_random_numbers = [
            round(self.random.random(), 3) for _ in range(num_customers)
        ]
        self.interarrival_times = self.generate_interarrival_times()
        self.arrivals = self.build_arrival_times()
        self.customers = self.create_customers()
        self.servers = [Server(number) for number in range(1, num_servers + 1)]
        self.service_times = []
        self.service_times_by_server = [[] for _ in self.servers]
        self.total_run_time = 0
        self.total_waiting_time = 0
        self.average_waiting_time = 0
        self.customers_who_waited = 0
        self.probability_customer_waited = 0

    def make_cumulative_probabilities(self, probabilities):
        cumulative_probabilities = []
        cumulative_probability = 0
        for probability in probabilities:
            cumulative_probability += probability
            cumulative_probabilities.append(cumulative_probability)
        return cumulative_probabilities

    def generate_interarrival_times(self):
        interarrival_times = []
        for number in self.interarrival_random_numbers:
            interarrival_times.append(
                self.sample_time(
                    number,
                    self.cumulative_interarrival_probabilities,
                    self.interarrival_times_values,
                )
            )
        return interarrival_times

    def normalize_distribution(self, distribution):
        if distribution and isinstance(distribution[0], (tuple, list)):
            times, probabilities = zip(*distribution)
            return tuple(times), tuple(probabilities)
        return tuple(range(1, len(distribution) + 1)), tuple(distribution)

    def sample_time(self, number, cumulative_probabilities, times=None):
        for generated_time, probability in enumerate(cumulative_probabilities, start=1):
            if number <= probability:
                return times[generated_time - 1] if times is not None else generated_time

    def build_arrival_times(self):
        arrivals = [0]
        for interarrival_time in self.interarrival_times[: self.num_customers - 1]:
            arrivals.append(arrivals[-1] + interarrival_time)
        return arrivals

    def create_customers(self):
        customers = []
        for index, arrival_time in enumerate(self.arrivals):
            interarrival_time = (
                None if index == 0 else arrival_time - self.arrivals[index - 1]
            )
            customers.append(
                Customer(index + 1, interarrival_time, arrival_time, None)
            )
        return customers

    def select_server(self, arrival_time):
        for server in self.servers:
            server.isIdle = server.available_at <= arrival_time

        available_servers = [server for server in self.servers if server.isIdle]
        if available_servers:
            candidates = available_servers
        else:
            earliest_available = min(server.available_at for server in self.servers)
            candidates = [
                server
                for server in self.servers
                if server.available_at == earliest_available
            ]

        if self.selection_method == "Random":
            return self.random.choice(candidates)
        if self.selection_method == "Least Utilization":
            selected_server = candidates[0]
            selected_utilization = selected_server.total_service_time / max(
                selected_server.available_at,
                arrival_time,
                1,
            )
            for server in candidates[1:]:
                utilization = server.total_service_time / max(
                    server.available_at,
                    arrival_time,
                    1,
                )
                if (utilization < selected_utilization):
                    selected_server = server
                    selected_utilization = utilization
            return selected_server

        selected_server = candidates[0]
        selected_priority = self.server_priorities[selected_server.number - 1]
        for server in candidates[1:]:
            priority = self.server_priorities[server.number - 1]
            if (priority, server.number) < (
                selected_priority,
                selected_server.number,
            ):
                selected_server = server
                selected_priority = priority
        return selected_server

    def customer_arrival_sort_key(self, customer):
        return customer.arrival_time, customer.number

    def run(self):
        for customer in sorted(
            self.customers,
            key=self.customer_arrival_sort_key,
        ):
            server = self.select_server(customer.arrival_time)
            service_time = self.sample_time(
                self.service_random_numbers[customer.number - 1],
                self.cumulative_service_probabilities[server.number - 1],
                self.service_time_values_by_server[server.number - 1],
            )
            customer.service_time = service_time
            server.serve_customer(customer)
            self.service_times.append(service_time)
            self.service_times_by_server[server.number - 1].append(service_time)
        self.calculate_statistics()
        return self.customers

    def calculate_statistics(self):
        self.total_run_time = max(server.available_at for server in self.servers)
        self.total_waiting_time = sum(customer.waiting_time for customer in self.customers)
        self.average_waiting_time = self.total_waiting_time / len(self.customers)
        self.customers_who_waited = sum(
            customer.waiting_time > 0 for customer in self.customers
        )
        self.probability_customer_waited = (
            self.customers_who_waited / len(self.customers)
        )

        for server in self.servers:
            server.calculate_statistics(self.total_run_time)
            server.isIdle = True

    def create_system_population_graph(self):
        event_changes = {}
        for customer in self.customers:
            event_changes[customer.arrival_time] = (
                event_changes.get(customer.arrival_time, 0) + 1
            )
            event_changes[customer.service_ends] = (
                event_changes.get(customer.service_ends, 0) - 1
            )

        event_times = sorted(event_changes)
        customer_counts = []
        customers_in_system = 0
        for event_time in event_times:
            customers_in_system += event_changes[event_time]
            customer_counts.append(customers_in_system)

        final_time = event_times[-1]
        figure, axes = plt.subplots(figsize=(11, 6))
        axes.fill_between(
            event_times,
            customer_counts,
            step="post",
            color="#3697B5",
            alpha=0.85,
        )
        axes.step(
            event_times,
            customer_counts,
            where="post",
            color="#176B83",
            linewidth=1.5,
        )
        axes.set_title("Graph")
        axes.set_xlabel("t")
        axes.set_ylabel("Q(t)")
        axes.set_xlim(0, final_time + 1)
        axes.set_ylim(0, max(customer_counts) + 0.6)
        axes.set_xticks(range(final_time + 2))
        axes.set_yticks(range(max(customer_counts) + 1))
        axes.spines["bottom"].set_position(("data", 0))
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        axes.grid(axis="y", alpha=0.2)
        return figure, axes

    def create_server_busy_time_graph(self):
        figure, axes = plt.subplots(
            len(self.servers),
            1,
            figsize=(11, max(2.5, 2.5 * len(self.servers))),
            squeeze=False,
        )
        axes_list = axes[:, 0]
        final_time = max(self.total_run_time, 1)

        for server, server_axes in zip(self.servers, axes_list):
            intervals = [
                (customer.service_begins, customer.service_time)
                for customer in self.customers
                if customer.server_number == server.number
            ]
            server_axes.broken_barh(
                intervals,
                (0, 1),
                facecolors="#3697B5",
                edgecolors="#176B83",
            )
            server_axes.set_title(f"Server Busy Time - Server {server.number}")
            server_axes.set_xlim(0, final_time)
            server_axes.set_ylim(0, 1)
            server_axes.set_yticks((0, 1), labels=("Idle", "Busy"))
            server_axes.set_xlabel("Time")
            server_axes.set_ylabel("B(t)")
            server_axes.grid(axis="x", alpha=0.2)

        return figure, axes_list