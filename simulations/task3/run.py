from simulations.task3.simulation import Simulation


if __name__ == "__main__":
    example = Simulation(
        order_up_to_level=11,
        review_period=5,
        demand_distribution=((0, 0.10), (1, 0.20), (2, 0.35), (3, 0.25), (4, 0.10)),
        lead_time_distribution=((1, 0.30), (2, 0.50), (3, 0.20)),
        num_days=15,
        beginning_inventory=3,
        first_order_arrives_after=2,
        first_order_quantity=8,
    )
    rows = example.run()
    print(example.statistics())
    for row in rows:
        print(row)
