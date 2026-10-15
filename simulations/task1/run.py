import matplotlib.pyplot as plt

from .simulation import Simulation


def main():
    simulation = Simulation(num_customers=10)
    print("Inter-arrival random numbers:", simulation.interarrival_random_numbers)
    print("Service random numbers:", simulation.service_random_numbers)
    print("Generated inter-arrival times:", simulation.interarrival_times)
    print("Generated service times:", simulation.service_times)
    simulation.run()
    simulation.print_table()
    simulation.create_system_population_graph()
    plt.show()


if __name__ == "__main__":
    main()