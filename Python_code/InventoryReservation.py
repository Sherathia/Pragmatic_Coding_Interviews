class Item:
    def __init__(self, item_id, name, total_quantity,reserved_quantity=0):
        self.item_id = item_id
        self.name=name
        self.total_quantity =total_quantity
        self.reserved_quantity=reserved_quantity

class ItemRepository:
    def __init__(self):
        self.item_stock = {}
        
    def save(self,item):
        self.item_stock[item.item_id]=item
        return item
    
    def get(self,item_id):
        return self.item_stock[item_id]
    
    def reserve_quantity(self,item_id,quantity):
        # self.item_stock[item_id].total_quantity-=quantity
        self.item_stock[item_id].reserved_quantity+=quantity
    
    def is_available(self,item_id, quantity):
        item=self.item_stock[item_id]
        return quantity <= item.total_quantity - item.reserved_quantity
    
    def release_quantity(self,item_id,quantity):
        # self.item_stock[item_id].total_quantity+=quantity
        self.item_stock[item_id].reserved_quantity-=quantity
    
    def reduce_quantity(self,item_id,quantity):
        self.item_stock[item_id].total_quantity-=quantity

class Order:
    def __init__(self,order_id,item_id,quantity):
        self.order_id=order_id
        self.item_id=item_id
        self.quantity=quantity
        self.status="PENDING"
        
        
class OrderRepository:
    def __init__(self):
        self.orders={}
    
    def create(self,order):
        self.orders[order.order_id]=order
        return order
    
    def get(self,order_id):
        return self.orders[order_id]
        
        
class InventoryService:
    def __init__(self,item,order):
        self.item=item
        self.order=order
    
    def add_item(self,item_id,name,quantity):
        inventory = Item(item_id,name,quantity)
        self.item.save(inventory)
        return inventory
    
    def reserve_item(self,order_id,item_id,quantity):
        if not self.item.get(item_id):
            raise Exception("Item not found") 
        if not self.item.is_available(item_id,quantity):
            raise Exception("Quantity not available")

        order = Order(order_id,item_id,quantity)
        self.order.create(order)
        self.item.reserve_quantity(item_id,quantity)
    
    def release_reservation(self,order_id):
        order =self.order.get(order_id)
        if not order:
            raise Exception("Order doesn't exist")
        if order.status == "RELEASED":
            return  # 🔥 IDEMPOTENT

        if order.status == "CONFIRMED":
            raise Exception("Cannot release confirmed order")
        self.item.release_quantity(order.item_id,order.quantity)
        order.status = "RELEASED"
     
    def confirm_reservation(self,order_id):
        order =self.order.get(order_id)
        if not order:
            raise Exception("Order doesn't exist")
        if order.status == "CONFIRMED":
            return 
        if order.status == "RELEASED":
            raise Exception("Cannot confirm released order")
        
        self.item.reduce_quantity(order.item_id,order.quantity)
        order.status = "CONFIRMED"
    
    def get_item_status(self,item_id):
        item= self.item.get(item_id)
        return {"item_id":item.item_id,
                "name":item.name,
                "total_quantity":item.total_quantity,
                "reserved_quantity":item.reserved_quantity}
    
    
repo =ItemRepository()
order = OrderRepository()
service=InventoryService(repo,order)
service.add_item("I1", "Burger", 10)
service.reserve_item("O1", "I1", 3)
service.reserve_item("O2", "I1", 4)
print(service.get_item_status("I1"))
service.confirm_reservation("O1")
print(service.get_item_status("I1"))
service.release_reservation("O2")
print(service.get_item_status("I1"))
        
            
    