from ..day import Day
from ..inventory import Inventory


class Simulation:
    def __init__(
        self,
        order_up_to_level,
        review_period,
        demand_distribution,
        lead_time_distribution,
        num_days,
        beginning_inventory=0,
        first_order_arrives_after=0,
        first_order_quantity=0,
    ):
        self.order_up_to_level = order_up_to_level
        self.review_period = review_period
        self.num_days = num_days
        self.beginning_inventory = beginning_inventory
        self.first_order_arrives_after = first_order_arrives_after
        self.first_order_quantity = first_order_quantity

        self.demand_distribution = sorted(demand_distribution)
        self.lead_time_distribution = sorted(lead_time_distribution)

        self.inventory = Inventory(
            beginning_inventory,
            order_up_to_level,
            review_period,
        )
        self.days = []

    def sample_from_distribution(self, distribution, random_digit):
        total_probability = 0

        for value, probability in distribution:
            total_probability += probability
            if random_digit < total_probability * 100:
                return value

    def run(self):
        self.days = []
        current_inventory = self.beginning_inventory
        orders_by_arrival_day = {}

        if self.first_order_quantity > 0:
            first_arrival_day = self.first_order_arrives_after + 2
            orders_by_arrival_day[first_arrival_day] = [
                self.first_order_quantity
            ]

        for day in range(1, self.num_days + 1):
            is_order_arrival_day = day in orders_by_arrival_day
            if is_order_arrival_day:
                for order_quantity in orders_by_arrival_day[day]:
                    current_inventory += order_quantity
                del orders_by_arrival_day[day]

            beginning_inventory = current_inventory
            self.inventory.ending_inventory = beginning_inventory

            day_within_cycle = ((day - 1) % self.review_period) + 1
            cycle = ((day - 1) // self.review_period) + 1
            day_result = Day(
                day,
                cycle,
                day_within_cycle,
                beginning_inventory,
            )

            demand = self.sample_from_distribution(
                self.demand_distribution, day_result.demand_random_digit
            )
            day_result.demand = demand
            self.inventory.update_inventory_after_demand(demand)

            day_result.ending_inventory = self.inventory.ending_inventory
            day_result.shortage_quantity = self.inventory.shortage_quantity
            current_inventory = day_result.ending_inventory

            if day_within_cycle == self.review_period:
                order_quantity = self.inventory.place_order()
                day_result.order_quantity = order_quantity

                if order_quantity > 0:
                    lead_time = (
                        self.sample_from_distribution(
                            self.lead_time_distribution,
                            day_result.lead_time_random_digit,
                        )
                    )
                    day_result.lead_time = lead_time

                    arrival_day = day + lead_time + 1
                    if arrival_day not in orders_by_arrival_day:
                        orders_by_arrival_day[arrival_day] = []
                    orders_by_arrival_day[arrival_day].append(order_quantity)

            days_until_arrival = None
            for arrival_day in orders_by_arrival_day:
                days_left = arrival_day - day - 1
                if days_left >= 0:
                    if (
                        days_until_arrival is None
                        or days_left < days_until_arrival
                    ):
                        days_until_arrival = days_left

            day_result.days_until_order_arrives = days_until_arrival
            self.days.append(day_result)
            print(f"Orders by arrival day after day {day}: {orders_by_arrival_day}")

        return self.days

    def statistics(self):
        ending_inventory_total = 0
        shortage_total = 0

        for day in self.days:
            ending_inventory_total += day.ending_inventory
            shortage_total += day.shortage_quantity

        ending_inventory_average = ending_inventory_total / len(
            self.days
        )
        shortage_quantity_average = shortage_total / len(self.days)

        return {
            "ending_inventory_average": ending_inventory_average,
            "shortage_quantity_average": shortage_quantity_average,
        }
