class Server:
    def __init__(self, number):
        self.number = number
        self.available_at = 0
        self.total_idle_time = 0
        self.total_service_time = 0
        self.customers_served = 0
        self.idle_time_probability = 0
        self.average_service_time = 0

    def serve_customer(self, customer):
        self.total_idle_time += max(0, customer.arrival_time - self.available_at)
        customer.service_begins = max(customer.arrival_time, self.available_at)
        customer.waiting_time = customer.service_begins - customer.arrival_time
        customer.service_ends = customer.service_begins + customer.service_time
        customer.server_number = self.number
        self.available_at = customer.service_ends
        self.total_service_time += customer.service_time
        self.customers_served += 1

    def calculate_statistics(self, total_run_time):
        self.idle_time_probability = (
            self.total_idle_time / total_run_time if total_run_time > 0 else 0
        )
        self.average_service_time = (
            self.total_service_time / self.customers_served
            if self.customers_served > 0
            else 0
        )