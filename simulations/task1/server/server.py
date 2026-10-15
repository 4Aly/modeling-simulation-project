class Server:
    def __init__(self, number):
        self.number = number
        self.available_at = 0

    def serve_customer(self, customer):
        customer.service_begins = max(customer.arrival_time, self.available_at)
        customer.service_ends = customer.service_begins + customer.service_time
        customer.server_number = self.number
        self.available_at = customer.service_ends