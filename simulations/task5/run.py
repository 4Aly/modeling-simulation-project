from simulations.task5.simulation import Simulation


TERMINAL_COUNTS = (10, 20, 30, 40, 50, 60, 70, 80)
RESPONSE_TIME_LIMIT = 30.0


if __name__ == "__main__":
    print("=== Required Cases ===")
    for number_of_terminals in TERMINAL_COUNTS:
        results = Simulation(number_of_terminals).run()
        print(
            f"n = {number_of_terminals:2d} | "
            f"Avg Response Time = {results['avg_response_time']:6.2f}s | "
            f"Time-Avg Queue = {results['avg_queue_length']:5.2f} | "
            f"CPU Utilization = {results['cpu_utilization']:.3f}"
        )

    print(
        "\n=== Finding maximum terminals for average response time "
        f"<= {RESPONSE_TIME_LIMIT:.1f}s ==="
    )
    for number_of_terminals in range(1, 100):
        results = Simulation(number_of_terminals).run()
        if results["avg_response_time"] > RESPONSE_TIME_LIMIT:
            maximum_terminals = number_of_terminals - 1
            print(
                f"{maximum_terminals} is the maximum number of terminals "
                f"(at n = {number_of_terminals}, average response time = "
                f"{results['avg_response_time']:.2f}s)."
            )
            break
