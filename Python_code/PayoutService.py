import logging
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict

# 1. Setup Logging & Exceptions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PayoutService")

class PayoutError(Exception): pass

# 2. Domain Models
@dataclass
class OrderEvent:
    order_id: int
    dasher_id: int
    start_min: int
    end_min: int

# 3. External Service Mock (Upstream Dependency)
class OrderClient:
    """Simulates the upstream microservice providing delivery data."""
    def get_orders_by_dasher(self, dasher_id: int) -> List[OrderEvent]:
        # Mock data provided by the requirements
        return [
            OrderEvent(order_id=1, dasher_id=dasher_id, start_min=0, end_min=10),
            OrderEvent(order_id=2, dasher_id=dasher_id, start_min=5, end_min=15),
        ]

# 4. The Payment Service
class PayoutService:
    BASE_RATE = 0.3  # $0.3 per minute

    def __init__(self, order_client: OrderClient):
        self.order_client = order_client

    def calculate_payout(self, dasher_id: int) -> float:
        """
        Calculates pay based on concurrent orders per minute.
        """
        logger.info(f"Calculating payout for Dasher: {dasher_id}")
        
        try:
            orders = self.order_client.get_orders_by_dasher(dasher_id)
            if not orders:
                logger.warning(f"No orders found for dasher {dasher_id}")
                return 0.0

            # Step 1: Map out activity per minute
            # Key: minute, Value: number of active orders in that minute
            minute_activity = defaultdict(int)
            
            for order in orders:
                # We assume the 'end_min' is the moment they finish, 
                # so they are paid for every minute from start until end.
                for m in range(order.start_min, order.end_min):
                    minute_activity[m] += 1

            # Step 2: Calculate total pay
            total_pay = 0.0
            for minute, count in minute_activity.items():
                # Rule: # ongoing deliveries * base pay rate
                pay_for_this_minute = count * self.BASE_RATE
                total_pay += pay_for_this_minute

            logger.info(f"Payout for {dasher_id} calculated: ${total_pay:.2f}")
            return round(total_pay, 2)

        except Exception as e:
            logger.error(f"Failed to calculate payout for {dasher_id}: {str(e)}")
            raise PayoutError("Internal service error during payout calculation")

# --- 5. Execution & Test Coverage ---
if __name__ == "__main__":
    # Dependency Injection
    client = OrderClient()
    service = PayoutService(client)
    
    # Test Case 1: Overlapping Orders
    # Order 1 (0-10), Order 2 (5-15)
    # Min 0-4: 1 order (5 mins * 0.3 = 1.5)
    # Min 5-9: 2 orders (5 mins * 0.6 = 3.0)
    # Min 10-14: 1 order (5 mins * 0.3 = 1.5)
    # Expected: 1.5 + 3.0 + 1.5 = 6.0
    
    dasher_id = 101
    amount = service.calculate_payout(dasher_id)
    print(f"Final Payout: ${amount}")
    
    assert amount == 6.0, f"Expected 6.0, got {amount}"
    print("✅ Test Passed!")