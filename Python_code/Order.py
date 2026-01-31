# Define Model
class Order:
    def __init__(self,order_id,item,status="CREATED"):
        self.id = order_id
        self.item = item
        self.status = status
        
    def __repr__(self):
        return f"Order(id={self.id}, item={self.item}, status={self.status})"

#Repository Pattern
class OrderRepository:
    def __init__(self):
        self.store={}
    
    def save(self,order):
        self.store[order.id]=order
    
    def get(self,order_id):
        return self.store[order_id]

    def exists(self,order_id):
        return order_id in self.store
    
VALID_TRANSITIONS = {
    "CREATED": ["CONFIRMED"],
    "CONFIRMED": ["DELIVERED"]
}   

class OrderService:
    def __init__(self,repo):
        self.repo=repo
    
    def create_order(self,order_id,item):
        if self.repo.exists(order_id):
            raise Exception("Order already exists")
        order=Order(order_id,item)
        self.repo.save(order)
        return order
    
    def get_order(self,order_id):
        if not self.repo.exists(order_id):
            raise Exception("Order doesn't exist")
        return self.repo.get(order_id)

    def update_status(self,order_id,new_status):
        order=self.get_order(order_id)
        allowed = VALID_TRANSITIONS.get(order.status,[])
        if new_status not in allowed:
            raise Exception("Invalid status")
        order.status=new_status
        return order
    
#API Layer

if __name__=="__main__":
    repo=OrderRepository()
    service=OrderService(repo)
    
    def api_create_order(order_id,item):
        return service.create_order(order_id,item)
    
    def api_get_order(order_id):
        return service.get_order(order_id)

    def api_update_order_status(order_id, new_status):
        return service.update_status(order_id, new_status)
    
    
    print(api_create_order(1, "Pizza"))
    print(api_create_order(2, "Burger"))

    # Fetch order
    print(api_get_order(1))

    # Update status
    print(api_update_order_status(1, "CONFIRMED"))

    # Try invalid update (should raise exception)
    try:
        api_update_order_status(1, "DELIVEREDs")  # Cannot jump from CREATED to DELIVERED
    except Exception as e:
        print(e)