import math
import random
import time

import matplotlib.pyplot as plt

from ..server import Server
from ..customer import Customer


class Simulation:
    def __init__(
        self,
        num_customers,
        interarrival_probabilities,
        service_probabilities,
    ):
        random.seed(time.time())

        self.validate_probabilities("Inter-arrival", interarrival_probabilities)
        self.validate_probabilities("Service-time", service_probabilities)

        self.num_customers = num_customers
        self.num_servers = 1
        self.interarrival_probabilities = tuple(interarrival_probabilities)
        self.service_probabilities = tuple(service_probabilities)
        self.cumulative_interarrival_probabilities = self.make_cumulative_probabilities(
            self.interarrival_probabilities
        )
        self.cumulative_service_probabilities = self.make_cumulative_probabilities(
            self.service_probabilities
        )
        self.interarrival_random_numbers = [
            round(random.random(), 3) for _ in range(num_customers)
        ]
        self.service_random_numbers = [
            round(random.random(), 3) for _ in range(num_customers)
        ]
        self.interarrival_times = self.generate_interarrival_times()
        self.service_times = self.generate_service_times()
        self.arrivals = self.build_arrival_times()
        self.customers = self.create_customers()
        self.servers = [Server(1)]
        self.total_run_time = 0
        self.total_waiting_time = 0
        self.average_waiting_time = 0
        self.customers_who_waited = 0
        self.probability_customer_waited = 0

    def validate_probabilities(self, name, probabilities):
        if not probabilities:
            raise ValueError(f"At least one {name.lower()} probability is required.")
        if any(probability < 0 or probability > 1 for probability in probabilities):
            raise ValueError(f"{name} probabilities must be between 0 and 1.")
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-6):
            raise ValueError(f"{name} probabilities must add up to 1.")

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
            for interarrival_time, probability in enumerate(
                self.cumulative_interarrival_probabilities, start=1
            ):
                if number <= probability:
                    interarrival_times.append(interarrival_time)
                    break
        return interarrival_times

    def generate_service_times(self):
        service_times = []

        for number in self.service_random_numbers:
            for service_time, probability in enumerate(
                self.cumulative_service_probabilities, start=1
            ):
                if number <= probability:
                    service_times.append(service_time)
                    break

        return service_times

    def build_arrival_times(self):
        arrivals = [0]
        for interarrival_time in self.interarrival_times[: len(self.service_times) - 1]:
            arrivals.append(arrivals[-1] + interarrival_time)
        return arrivals

    def create_customers(self):
        customers = []
        for index, (arrival_time, service_time) in enumerate(
            zip(self.arrivals, self.service_times)
        ):
            interarrival_time = (
                None if index == 0 else arrival_time - self.arrivals[index - 1]
            )
            customers.append(
                Customer(index + 1, interarrival_time, arrival_time, service_time)
            )
        return customers

    def run(self):
        for customer in sorted(
            self.customers,
            key=lambda item: (item.arrival_time, item.number),
        ):
            self.servers[0].serve_customer(customer)
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