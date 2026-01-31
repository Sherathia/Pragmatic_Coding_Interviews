from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List
from datetime import datetime
import logging

# --- 1. Domain Models ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("InventoryService")

class OrderStatus:
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    RELEASED = "RELEASED"

@dataclass
class Item:
    item_id: str
    name: str
    total_qty: int
    reserved_qty: int = 0
    
    @property
    def available_qty(self) -> int:
        return self.total_qty - self.reserved_qty

@dataclass
class Order:
    order_id: str
    item_id: str
    quantity: int
    status: str = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)

# --- 2. Custom Exceptions ---

class InventoryError(Exception): pass
class InsufficientStockError(InventoryError): pass
class OrderError(Exception): pass

# --- 3. Repositories ---

class ItemRepository:
    def __init__(self):
        self._items: Dict[str, Item] = {}
        self._lock = Lock() 

    def get_item(self, item_id: str) -> Item:
        if item_id not in self._items:
            raise InventoryError(f"Item {item_id} not found")
        return self._items[item_id]

    def save(self, item: Item):
        self._items[item.item_id] = item

class OrderRepository:
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def create(self, order: Order) -> Order:
        self._orders[order.order_id] = order
        return order

    def get(self, order_id: str) -> Order:
        if order_id not in self._orders:
            logger.error(f"Repository: Order {order_id} not found")
            raise OrderError(f"Order {order_id} not found")
        return self._orders[order_id]

# --- 4. The Service (The Core Logic) ---

class InventoryService:
    def __init__(self, item_repo: ItemRepository, order_repo: OrderRepository):
        self.item_repo = item_repo
        self.order_repo = order_repo

    def add_item(self, item_id: str, name: str, quantity: int):
        """Helper to seed data"""
        new_item = Item(item_id, name, quantity)
        self.item_repo.save(new_item)
        logger.info(f"Inventory: Added item {item_id} ({name}) with quantity {quantity}")

    def reserve_item(self, order_id: str, item_id: str, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        logger.info(f"Reserve: Attempting to reserve {quantity} of {item_id} for Order {order_id}")
        with self.item_repo._lock:
            item = self.item_repo.get_item(item_id)
            
            if item.available_qty < quantity:
                raise InsufficientStockError(f"Requested {quantity}, but only {item.available_qty} available")

            # Update Item State
            item.reserved_qty += quantity
            
            # Create Order Record
            new_order = Order(order_id, item_id, quantity)
            self.order_repo.create(new_order)
            logger.info(f"Reserve Success: Order {order_id} created")

    def confirm_reservation(self, order_id: str):
        order = self.order_repo.get(order_id)
        
        # Idempotency check
        if order.status == OrderStatus.CONFIRMED:
            logger.info(f"Confirm: Order {order_id} is already confirmed (Idempotent call)")
            return

        with self.item_repo._lock:
            item = self.item_repo.get_item(order.item_id)
            
            # Transition Logic
            item.total_qty -= order.quantity
            item.reserved_qty -= order.quantity
            order.status = OrderStatus.CONFIRMED
            print(f"DEBUG: Confirmed Order {order_id}. New Total: {item.total_qty}")

    def release_reservation(self, order_id: str):
        order = self.order_repo.get(order_id)
        
        if order.status == OrderStatus.RELEASED:
            return
        if order.status == OrderStatus.CONFIRMED:
            raise OrderError("Cannot release an order that has already been confirmed")

        with self.item_repo._lock:
            item = self.item_repo.get_item(order.item_id)
            item.reserved_qty -= order.quantity
            order.status = OrderStatus.RELEASED
            print(f"DEBUG: Released Order {order_id}. Reserved Qty is now {item.reserved_qty}")

# --- 5. Quick Test to Verify ---

if __name__ == "__main__":
    # Setup
    i_repo = ItemRepository()
    o_repo = OrderRepository()
    service = InventoryService(i_repo, o_repo)
    
    # 1. Add Stock
    service.add_item("BURGER_01", "Cheeseburger", 10)
    
    # 2. Reserve Stock
    service.reserve_item("ORD_101", "BURGER_01", 3)
    
    # 3. Confirm (Stock should go down from 10 to 7)
    service.confirm_reservation("ORD_101")
    
    # 4. Try to reserve more than available (7 left)
    try:
        service.reserve_item("ORD_102", "BURGER_01", 10)
    except InsufficientStockError as e:
        print(f"Caught Expected Error: {e}")