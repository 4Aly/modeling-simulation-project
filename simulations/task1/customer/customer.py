class Customer:
    def __init__(self, number, interarrival_time, arrival_time, service_time):
        self.number = number
        self.interarrival_time = interarrival_time
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.service_begins = None
        self.service_ends = None
        self.server_number = None