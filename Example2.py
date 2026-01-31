from dataclasses import dataclass
import datetime
import heapq
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BootstrapService")

@dataclass
class Location:
    lat: float
    lon: float

@dataclass
class Dasher:
    dasher_id:int
    dasher_name:str
    dasher_location:Location
    distance: int
    
@dataclass
class Order:
    order_id:int
    restaurant_location:Location


@dataclass
class Assignment:
    order_id:int
    dasher_id:int
    dasher_name:str
    estimated_pickup_time: datetime
    dasher_location:Location
    
    
class DasherRepository:
    def getAvailableDashers(self):
        return [Dasher(dasher_id=1,dasher_name="a",distance=2,dasher_location=Location(lat=37.7749, lon=-122.4194)),
                Dasher(dasher_id=2,dasher_name="b",distance=5,dasher_location=Location(lat=37.7749, lon=-122.4194))]
        
class OrderRepository:
    def getOrder(self,order_id):
        return Order(order_id=123, restaurant_location=Location(lat=37.7749, lon=-122.4194))
    
class NotificationService:
    def notifyDasher(self,dasher_id,order_id):
        pass
        
    
class OrderAssignmentService:
    def __init__(self, dasher:DasherRepository, order:OrderRepository, notify:NotificationService):
        self.dasher=dasher
        self.order=order
        self.notify=notify
        
    def assignOrder(self,order_id:int):
        heap=[]
        dashers = self.dasher.getAvailableDashers()
        if not dashers:
            raise Exception("No Dashers available")
        
        orders=self.order.getOrder(order_id)
        if not orders:
            raise Exception("Order not Found")
        
        for d in dashers:
            if d.distance<=5:
                heapq.heappush(heap, [d.distance,d])
        
        if not heap:
            raise Exception("No Dashers available within 5 miles")
        assigned_dasher = heapq.heappop(heap)
        pickup_time  = assigned_dasher[0]*3
        estimated_time = datetime.datetime.now() +datetime.timedelta(minutes=pickup_time)

        try:
            self.notify.notifyDasher(assigned_dasher[1].dasher_id, order_id)
            logger.info(f"Dasher {assigned_dasher[1].dasher_id} notified successfully")
        except Exception as e:
            logger.error(f"Failed to notify dasher {assigned_dasher[1].dasher_id}: {e}")
        # Continue anyway - still return the assignment
        
        return Assignment(order_id=order_id,
                            dasher_id=assigned_dasher[1].dasher_id,
                            dasher_name=assigned_dasher[1].dasher_name,
                            estimated_pickup_time=estimated_time,
                            dasher_location=assigned_dasher[1].dasher_location)

def test_successful_assignment():
    """Test normal case - dasher found and assigned"""
    dasher_repo = DasherRepository()
    order_repo = OrderRepository()
    notification_service = NotificationService()
    
    service = OrderAssignmentService(dasher_repo, order_repo, notification_service)
    result = service.assignOrder(123)
    
    assert result is not None
    assert result.order_id == 123
    assert result.dasher_id == 1  # Closest dasher
    assert result.dasher_name == "a"
    print("✓ Test successful assignment - PASSED")

def test_no_dashers_available():
    """Test when no dashers exist"""
    # Create mock that returns empty list
    class EmptyDasherRepo:
        def getAvailableDashers(self):
            return []
    
    service = OrderAssignmentService(EmptyDasherRepo(), OrderRepository(), NotificationService())
    
    try:
        service.assignOrder(123)
        print("✗ Test no dashers - FAILED (should have raised exception)")
    except Exception as e:
        assert "No Dashers available" in str(e)
        print("✓ Test no dashers available - PASSED")

def test_notification_failure():
    """Test that assignment succeeds even if notification fails"""
    class FailingNotificationService:
        def notifyDasher(self, dasher_id, order_id):
            raise Exception("Network error")
    
    service = OrderAssignmentService(
        DasherRepository(), 
        OrderRepository(), 
        FailingNotificationService()
    )
    
    result = service.assignOrder(123)
    assert result is not None  # Should still return assignment
    print("✓ Test notification failure - PASSED")

# Run tests
if __name__ == "__main__":
    test_successful_assignment()
    test_no_dashers_available()
    test_notification_failure() 
        
