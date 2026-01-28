# --------------------------
# Domain Models
# --------------------------
class Item:
    def __init__(self, item_id, name, total_quantity):
        self.item_id = item_id
        self.name = name
        self.total_quantity = total_quantity
        self.reserved_quantity = 0  # currently reserved stock


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.items = {}  # dict: item_id -> quantity
        self.status = "PENDING"  # PENDING, CONFIRMED, RELEASED


# --------------------------
# Repositories
# --------------------------
class ItemRepository:
    def __init__(self):
        self.items = {}  # item_id -> Item

    def save(self, item):
        self.items[item.item_id] = item
        return item

    def get(self, item_id):
        return self.items.get(item_id)

    def reserve_quantity(self, item_id, quantity):
        self.items[item_id].reserved_quantity += quantity

    def release_quantity(self, item_id, quantity):
        self.items[item_id].reserved_quantity -= quantity

    def reduce_quantity(self, item_id, quantity):
        self.items[item_id].total_quantity -= quantity

    def is_available(self, item_id, quantity):
        item = self.items.get(item_id)
        return item and quantity <= item.total_quantity - item.reserved_quantity


class OrderRepository:
    def __init__(self):
        self.orders = {}  # order_id -> Order

    def save(self, order):
        self.orders[order.order_id] = order
        return order

    def get(self, order_id):
        return self.orders.get(order_id)


# --------------------------
# Inventory Service
# --------------------------
class InventoryService:
    def __init__(self, item_repo, order_repo):
        self.item_repo = item_repo
        self.order_repo = order_repo

    # Add a new item to inventory
    def add_item(self, item_id, name, quantity):
        item = Item(item_id, name, quantity)
        self.item_repo.save(item)
        return item

    # Reserve multiple items in a single order
    def reserve_items(self, order_id, items_dict):
        """
        items_dict: {item_id: quantity, ...}
        """
        # 1. Validate all items exist and have enough stock
        for item_id, qty in items_dict.items():
            item = self.item_repo.get(item_id)
            if not item:
                raise Exception(f"Item {item_id} not found")
            if qty > item.total_quantity - item.reserved_quantity:
                raise Exception(f"Insufficient stock for {item_id}")

        # 2. Create or get order
        order = self.order_repo.get(order_id)
        if not order:
            order = Order(order_id)
            self.order_repo.save(order)
        elif order.status != "PENDING":
            raise Exception("Cannot modify finalized order")

        # 3. Reserve stock and add to order
        for item_id, qty in items_dict.items():
            self.item_repo.reserve_quantity(item_id, qty)
            order.items[item_id] = order.items.get(item_id, 0) + qty

    # Confirm all reserved items
    def confirm_reservation(self, order_id):
        order = self.order_repo.get(order_id)
        if not order:
            raise Exception("Order not found")

        if order.status == "CONFIRMED":  # idempotent
            return
        if order.status == "RELEASED":
            raise Exception("Cannot confirm released order")

        for item_id, qty in order.items.items():
            self.item_repo.reduce_quantity(item_id, qty)
            self.item_repo.release_quantity(item_id, qty)

        order.status = "CONFIRMED"

    # Release all reserved items
    def release_reservation(self, order_id):
        order = self.order_repo.get(order_id)
        if not order:
            raise Exception("Order not found")

        if order.status == "RELEASED":  # idempotent
            return
        if order.status == "CONFIRMED":
            raise Exception("Cannot release confirmed order")

        for item_id, qty in order.items.items():
            self.item_repo.release_quantity(item_id, qty)

        order.status = "RELEASED"

    # Get stock status of a single item
    def get_item_status(self, item_id):
        item = self.item_repo.get(item_id)
        if not item:
            raise Exception("Item not found")
        return {
            "item_id": item.item_id,
            "name": item.name,
            "total_quantity": item.total_quantity,
            "reserved_quantity": item.reserved_quantity,
            "available_quantity": item.total_quantity - item.reserved_quantity
        }


# --------------------------
# Manual Tests
# --------------------------
def run_tests():
    # Setup
    item_repo = ItemRepository()
    order_repo = OrderRepository()
    service = InventoryService(item_repo, order_repo)

    # Add items
    service.add_item("I1", "Burger", 10)
    service.add_item("I2", "Fries", 5)
    service.add_item("I3", "Coke", 2)

    # Reserve multiple items
    service.reserve_items("O1", {"I1": 3, "I2": 2})
    status = service.get_item_status("I1")
    assert status["reserved_quantity"] == 3
    status = service.get_item_status("I2")
    assert status["reserved_quantity"] == 2

    # Confirm reservation
    service.confirm_reservation("O1")
    status = service.get_item_status("I1")
    assert status["reserved_quantity"] == 0
    assert status["total_quantity"] == 7
    status = service.get_item_status("I2")
    assert status["reserved_quantity"] == 0
    assert status["total_quantity"] == 3

    # Release a PENDING reservation
    service.reserve_items("O2", {"I1": 2, "I3": 1})
    service.release_reservation("O2")
    status = service.get_item_status("I1")
    assert status["reserved_quantity"] == 0
    status = service.get_item_status("I3")
    assert status["reserved_quantity"] == 0

    print("All tests passed ✅")


if __name__ == "__main__":
    run_tests()
