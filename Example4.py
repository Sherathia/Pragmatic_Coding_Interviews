from dataclasses import dataclass
from typing import Optional, List
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrderStatusService")

@dataclass
class OrderInfo:
    order_id: str
    current_status: str
    restaurant_id: str
    customer_id: str
    dasher_id: Optional[str]
    created_at: str

@dataclass
class StatusUpdate:
    order_id: str
    old_status: str
    new_status: str
    updated_by: str
    updated_at: str
    success: bool
    error_message: Optional[str]

@dataclass
class StatusHistory:
    order_id: str
    status: str
    updated_by: str
    timestamp: str

# Fixed: No space after PLACED
VALID_TRANSITIONS = {
    "PLACED": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["READY", "CANCELLED"],
    "READY": ["PICKED_UP", "CANCELLED"],
    "PICKED_UP": ["DELIVERED", "CANCELLED"],
    "DELIVERED": [],  # Can't transition from DELIVERED (except was None)
    "CANCELLED": []   # Terminal state
}

class OrderRepository:
    def get_order(self, order_id):
        # Mock data
        if order_id == "order_123":
            return [OrderInfo(
                order_id="order_123",
                current_status="PLACED",
                restaurant_id="rest_456",
                customer_id="cust_789",
                dasher_id=None,
                created_at="2026-01-29T10:00:00"
            )]
        return []

class NotificationService:
    def notify_status_change(self, order_id, new_status):
        logger.info(f"Notification sent for order {order_id}: {new_status}")

class OrderStatusService:
    def __init__(self, orderRepo: OrderRepository, notify: NotificationService):
        self.orderRepo = orderRepo
        self.notify = notify
        
        # Current status map
        self.current_status = {}  # {order_id: current_status}
        
        # History tracking (append-only)
        self.status_history = {}  # {order_id: [StatusHistory, ...]}
        
        # Reverse index for fast lookup
        self.status_index = {}  # {status: set(order_ids)}
        
        # Cache order info
        self.orders_cache = {}  # {order_id: OrderInfo}
    
    def update_status(self, order_id: str, new_status: str, updated_by: str) -> StatusUpdate:
        """Update order status with validation"""
        
        # 1. Get order
        orders = self.orderRepo.get_order(order_id)
        if not orders or len(orders) == 0:
            return StatusUpdate(
                order_id=order_id,
                old_status="",
                new_status=new_status,
                updated_by=updated_by,
                updated_at=datetime.datetime.now().isoformat(),
                success=False,
                error_message="Order not found"
            )
        
        order = orders[0]
        
        # 2. Determine current status
        if order_id in self.current_status:
            old_status = self.current_status[order_id]
        else:
            # First time seeing this order - initialize
            old_status = order.current_status
            self.current_status[order_id] = old_status
            self.orders_cache[order_id] = order
            
            # Add to status index
            if old_status not in self.status_index:
                self.status_index[old_status] = set()
            self.status_index[old_status].add(order_id)
            
            # Record initial status in history
            if order_id not in self.status_history:
                self.status_history[order_id] = []
            self.status_history[order_id].append(StatusHistory(
                order_id=order_id,
                status=old_status,
                updated_by="system",
                timestamp=order.created_at
            ))
        
        # 3. Validate transition
        if new_status not in VALID_TRANSITIONS.get(old_status, []):
            return StatusUpdate(
                order_id=order_id,
                old_status=old_status,
                new_status=new_status,
                updated_by=updated_by,
                updated_at=datetime.datetime.now().isoformat(),
                success=False,
                error_message=f"Invalid transition: {old_status} -> {new_status}"
            )
        
        # 4. Update current status
        self.current_status[order_id] = new_status
        
        # 5. Update status index (remove from old, add to new)
        if old_status in self.status_index:
            self.status_index[old_status].discard(order_id)
        if new_status not in self.status_index:
            self.status_index[new_status] = set()
        self.status_index[new_status].add(order_id)
        
        # 6. Record in history
        timestamp = datetime.datetime.now().isoformat()
        self.status_history[order_id].append(StatusHistory(
            order_id=order_id,
            status=new_status,
            updated_by=updated_by,
            timestamp=timestamp
        ))
        
        # 7. Update cached order info
        self.orders_cache[order_id].current_status = new_status
        
        # 8. Try to notify (don't fail if notification fails)
        try:
            self.notify.notify_status_change(order_id, new_status)
        except Exception as e:
            logger.error(f"Failed to notify status change: {e}")
        
        # 9. Return success
        return StatusUpdate(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            updated_by=updated_by,
            updated_at=timestamp,
            success=True,
            error_message=None
        )
    
    def getOrderStatus(self, order_id: str) -> Optional[OrderInfo]:
        """Get current order status"""
        if order_id not in self.orders_cache:
            # Try to load from repo
            orders = self.orderRepo.get_order(order_id)
            if not orders:
                return None
            return orders[0]
        
        return self.orders_cache[order_id]
    
    def getStatusHistory(self, order_id: str) -> List[StatusHistory]:
        """Get complete status history for an order"""
        if order_id not in self.status_history:
            return []
        return self.status_history[order_id]
    
    def getOrdersByStatus(self, status: str) -> List[OrderInfo]:
        """Get all orders with a specific status"""
        if status not in self.status_index:
            return []
        
        order_ids = self.status_index[status]
        return [self.orders_cache[oid] for oid in order_ids if oid in self.orders_cache]


# ============= TESTS =============

def test_valid_status_transition():
    """Test valid status transition"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    # Initialize order
    result = service.update_status("order_123", "CONFIRMED", "restaurant_service")
    
    assert result.success == True
    assert result.old_status == "PLACED"
    assert result.new_status == "CONFIRMED"
    print("✓ Test valid transition - PASSED")

def test_invalid_status_transition():
    """Test invalid status transition (skipping steps)"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    # Try to skip from PLACED to READY
    result = service.update_status("order_123", "READY", "restaurant_service")
    
    assert result.success == False
    assert "Invalid transition" in result.error_message
    print("✓ Test invalid transition - PASSED")

def test_status_history_tracking():
    """Test that history is correctly tracked"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    # Make several transitions
    service.update_status("order_123", "CONFIRMED", "restaurant")
    service.update_status("order_123", "PREPARING", "restaurant")
    service.update_status("order_123", "READY", "restaurant")
    
    history = service.getStatusHistory("order_123")
    
    assert len(history) == 4  # PLACED (initial) + 3 updates
    assert history[0].status == "PLACED"
    assert history[1].status == "CONFIRMED"
    assert history[2].status == "PREPARING"
    assert history[3].status == "READY"
    print("✓ Test status history - PASSED")

def test_get_orders_by_status():
    """Test getting all orders by status"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    # Update order to CONFIRMED
    service.update_status("order_123", "CONFIRMED", "restaurant")
    
    # Get all CONFIRMED orders
    confirmed_orders = service.getOrdersByStatus("CONFIRMED")
    
    assert len(confirmed_orders) == 1
    assert confirmed_orders[0].order_id == "order_123"
    
    # Should not be in PLACED anymore
    placed_orders = service.getOrdersByStatus("PLACED")
    assert len(placed_orders) == 0
    
    print("✓ Test get orders by status - PASSED")

def test_cancelled_from_any_status():
    """Test that CANCELLED can be reached from any status"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    # Go to PREPARING
    service.update_status("order_123", "CONFIRMED", "restaurant")
    service.update_status("order_123", "PREPARING", "restaurant")
    
    # Cancel from PREPARING
    result = service.update_status("order_123", "CANCELLED", "customer_service")
    
    assert result.success == True
    assert result.new_status == "CANCELLED"
    print("✓ Test cancel from any status - PASSED")

def test_order_not_found():
    """Test handling of non-existent order"""
    service = OrderStatusService(OrderRepository(), NotificationService())
    
    result = service.update_status("invalid_order", "CONFIRMED", "system")
    
    assert result.success == False
    assert "not found" in result.error_message.lower()
    print("✓ Test order not found - PASSED")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running Order Status Service Tests")
    print("="*60 + "\n")
    
    test_valid_status_transition()
    test_invalid_status_transition()
    test_status_history_tracking()
    test_get_orders_by_status()
    test_cancelled_from_any_status()
    test_order_not_found()
    
    print("\n" + "="*60)
    print("All tests passed! ✅")
    print("="*60)