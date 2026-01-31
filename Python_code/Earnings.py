from dataclasses import dataclass
from typing import DefaultDict, Dict

@dataclass
class OrderInfo:
    dasher_id: int
    order_id:int
    start_time:int
    end_time:int
    
class OrderRepository:
    def __init__(self):
        self.dasher: Dict[int,OrderInfo]={}
    
    def get_orders(self,dasher_id):
        return [OrderInfo(dasher_id=dasher_id,order_id=12,start_time=2,end_time=3),
                OrderInfo(dasher_id=dasher_id,order_id=13,start_time=1,end_time=2)]
        
class PaymentService:
    def __init__(self,orderRepo:OrderRepository):
        self.orderRepo=orderRepo
        
    def calculate_payment(self,dasher_id):
        order = self.orderRepo.get_orders(dasher_id)
        if not order:
            return 0
        
        # OrderTime = DefaultDict(int)
        events=[]
        for ord in order:
            events.append((ord.start_time, 1))
            events.append((ord.end_time, -1))
        
        events.sort()
        
        total_amount = 0
        current_multiplier = 0
        last_time = events[0][0]
        
        for time, change in events:
            duration = time - last_time
            
            total_amount += duration * current_multiplier

            current_multiplier += change
            last_time = time
            
        return total_amount

if __name__ == "__main__":
    repo = OrderRepository()
    service = PaymentService(repo)
    print(service.calculate_payment(1))

def test_overlap():
    class FakeRepo:
        def get_orders(self, dasher_id):
            return [
                OrderInfo(dasher_id, 1, 1, 3),
                OrderInfo(dasher_id, 2, 2, 4),
            ]

    service = PaymentService(FakeRepo())
    assert service.calculate_payment(1) == 4


def test_no_orders():
    class EmptyRepo:
        def get_orders(self, dasher_id):
            return []

    service = PaymentService(EmptyRepo())
    assert service.calculate_payment(1) == 0
