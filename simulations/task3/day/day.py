class Day:
    def __init__(
        self,
        day,
        cycle,
        day_within_cycle,
        beginning_inventory,
        demand_random_digit,
        lead_time_random_digit,
    ):
        self.day = day
        self.cycle = cycle
        self.day_within_cycle = day_within_cycle
        self.beginning_inventory = beginning_inventory
        self.demand_random_digit = demand_random_digit
        self.lead_time_random_digit = lead_time_random_digit
        self.demand = None
        self.ending_inventory = None
        self.shortage_quantity = None
        self.order_quantity = None
        self.lead_time = None
        self.days_until_order_arrives = None
