class Order:
    def __init__(self,user_id,items,order_id,status='CREATED'):
        self.user_id=user_id
        self.items=items
        self.status=status
        self.order_id=order_id

VALID_TRANSITIONS = {
    "CREATED": ["CONFIRMED"],
    "CONFIRMED": ["PREPARING"],
    "PREPARING": ["OUT_FOR_DELIVERY"],
    "OUT_FOR_DELIVERY": ["DELIVERED"],
    "DELIVERED": None,
}   

class OrderRepository:
    def __init__(self):
        self.store={}   
    
    def save(self,order):
        self.store[order.order_id]=order    
    
    def get(self,order_id):
        return self.store[order_id] 
           
class OrderService:
    def __init__(self,orders):
        self.orders=orders
        self.sequence=0
        
    def create_order(self,user_id,items):
        self.sequence+=1
        order_id=self.sequence
        order = Order(user_id,items,order_id)
        self.orders.save(order)
        return order_id
    
    def confirm_order(self,order_id):
        self.state_validation(order_id,"CONFIRMED")
    
    def start_preparing(self,order_id):
        self.state_validation(order_id,"PREPARING")
    
    def dispatch_order(self,order_id):
        self.state_validation(order_id,"OUT_FOR_DELIVERY")
    
    def deliver_order(self,order_id):
        self.state_validation(order_id,"DELIVERED")
    
    def state_validation(self,order_id,next_state):
        order = self.orders.get(order_id)
        if not order:
            raise Exception("Order not found")
        allowed = VALID_TRANSITIONS.get(order.status,[])
        if next_state not in allowed:
            raise Exception("Invalid status")
        order.status=next_state
        return order
    
    def get_order_status(self,order_id):
        order = self.orders.get(order_id)
        if not order:
            raise Exception("Order not found")
        return order.status
    
    
if __name__=="__main__":
    repo=OrderRepository()
    service=OrderService(repo)
    order_id = service.create_order(1, ["burger", "fries"])
    service.confirm_order(order_id)
    service.start_preparing(order_id)
    service.dispatch_order(order_id)
    service.deliver_order(order_id)

    assert "DELIVERED" ==service.get_order_status(order_id)
    
    
        
            
        