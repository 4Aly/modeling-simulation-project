import matplotlib.pyplot as plt

from .simulation import Simulation


def main():
    simulation = Simulation(num_customers=10)
    simulation.run()
    simulation.create_system_population_graph()
    plt.show()


if __name__ == "__main__":
    main()