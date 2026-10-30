class Inventory:
    def __init__(
        self,
        beginning_inventory=0,
        order_up_to_level=0,
        review_period=0,
    ):
        self.beginning_inventory = beginning_inventory
        self.order_up_to_level = order_up_to_level
        self.review_period = review_period
        self.ending_inventory = beginning_inventory
        self.shortage_quantity = 0
        self.order_quantity = 0
        self.days_until_order_arrives = 0

    def update_inventory_after_demand(self, demand):
        ending_inventory = self.ending_inventory - demand
        if ending_inventory >= 0:
            self.ending_inventory = ending_inventory
            self.shortage_quantity = 0
        else:
            self.shortage_quantity = abs(ending_inventory)
            self.ending_inventory = 0

    def place_order(self):
        self.order_quantity = max((
            self.order_up_to_level - self.ending_inventory + self.shortage_quantity
        ),0)
        return self.order_quantity
