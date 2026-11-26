from simulations.task4 import rngs
from ..job import Job
from ..event import Event
from ..cpu import CPU


QUANTUM = 0.1
SWAP_TIME = 0.015
MEAN_THINK_TIME = 25.0
MEAN_SERVICE_TIME = 0.8
DEFAULT_STOP_VALUE = 1000
STOP_AFTER_JOBS = "Number of jobs"
STOP_AFTER_RUNTIME = "CPU run time"

EVENT_ARRIVAL = 1
EVENT_END_CPU_RUN = 2
EVENT_END_SIMULATION = 3


class Simulation:
    def __init__(
        self,
        number_of_terminals,
        think_time_mean=MEAN_THINK_TIME,
        service_time_mean=MEAN_SERVICE_TIME,
        quantum_time=QUANTUM,
        stopping_condition=STOP_AFTER_JOBS,
        stopping_value=DEFAULT_STOP_VALUE,
    ):
        self.number_of_terminals = number_of_terminals
        self.think_time_mean = think_time_mean
        self.service_time_mean = service_time_mean
        self.quantum_time = quantum_time
        self.stopping_condition = stopping_condition
        self.stopping_value = stopping_value

        self.initialize()

    def initialize(self):
        self.clock = 0.0
        self.last_event_time = 0.0
        self.queue = []
        self.cpu = CPU()
        self.event_list = []
        self.response_times = []
        self.completed_jobs = 0
        self.queue_lengths = []
        self.cpu_states = []
        self.durations = []
        self.think_index = 0
        self.service_index = 0

        for i in range(self.number_of_terminals):
            self.event_list.append(Event(self.get_think_time(), EVENT_ARRIVAL))

        if self.stopping_condition == STOP_AFTER_RUNTIME:
            self.event_list.append(Event(self.stopping_value, EVENT_END_SIMULATION))

    def get_think_time(self):
        half = len(rngs.random_numbers) // 2
        number = rngs.random_numbers[self.think_index % half]
        self.think_index += 1
        return number * rngs.rate * self.think_time_mean

    def get_service_time(self):
        half = len(rngs.random_numbers) // 2
        number = rngs.random_numbers[half + self.service_index % half]
        self.service_index += 1
        return number * rngs.rate * self.service_time_mean

    def update_stats(self):
        elapsed = self.clock - self.last_event_time
        self.queue_lengths.append(len(self.queue))
        if self.cpu.is_free():
            self.cpu_states.append(0)
        else:
            self.cpu_states.append(1)
        self.durations.append(elapsed)
        self.last_event_time = self.clock

    def arrive(self):
        job = Job(self.clock, self.get_service_time())
        self.queue.append(job)
        if self.cpu.is_free():
            self.start_cpu_run()

    def start_cpu_run(self):
        job = self.queue.pop(0)
        if job.remaining_service_time <= self.quantum_time:
            run_time = job.remaining_service_time + SWAP_TIME
            job.remaining_service_time = 0.0
        else:
            run_time = self.quantum_time + SWAP_TIME
            job.remaining_service_time = job.remaining_service_time - self.quantum_time
        self.cpu.add_job(job)
        self.event_list.append(Event(self.clock + run_time, EVENT_END_CPU_RUN))

    def end_cpu_run(self):
        job = self.cpu.remove_job()

        if job.remaining_service_time > 0:
            self.queue.append(job)
        else:
            self.response_times.append(self.clock - job.arrival_time)
            self.completed_jobs += 1
            if (
                self.stopping_condition == STOP_AFTER_JOBS
                and self.completed_jobs >= self.stopping_value
            ):
                self.event_list.append(Event(self.clock, EVENT_END_SIMULATION))
            else:
                self.event_list.append(
                    Event(self.clock + self.get_think_time(), EVENT_ARRIVAL)
                )

        if len(self.queue) > 0:
            self.start_cpu_run()

    def report(self):
        total = self.clock
        if total == 0:
            total = 1.0
        average = 0.0
        if len(self.response_times) > 0:
            average = sum(self.response_times) / len(self.response_times)
        area_queue = 0.0
        area_busy = 0.0
        for i in range(len(self.durations)):
            area_queue = area_queue + self.queue_lengths[i] * self.durations[i]
            area_busy = area_busy + self.cpu_states[i] * self.durations[i]
        return {
            "n": self.number_of_terminals,
            "avg_response_time": average,
            "avg_queue_length": area_queue / total,
            "cpu_utilization": area_busy / total,
            "total_sim_time": total,
        }

    def run(self):
        self.initialize()
        while True:
            next_index = 0
            for i in range(len(self.event_list)):
                if self.event_list[i].time < self.event_list[next_index].time:
                    next_index = i
            event = self.event_list.pop(next_index)
            self.clock = event.time
            self.update_stats()

            if event.event_type == EVENT_ARRIVAL:
                self.arrive()
            elif event.event_type == EVENT_END_CPU_RUN:
                self.end_cpu_run()
            else:
                return self.report()