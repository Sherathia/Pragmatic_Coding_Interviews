from dataclasses import dataclass

@dataclass
class Orders:
    restaurant_id: int
    order_id:int
    slot_no_occupied: int
    start_time: int
    end_time: int

class Restaurant:
    restaurant_id:int
    total_slots: int

class RestaurantRepository:
    def __init__(self):
        self.restaurant={}
    
    def add(self,restaurant):
        self.restaurant[restaurant.restaurant_id]=restaurant
    
    def get(self,restaurant_id):
        return self.restaurant.get(restaurant_id)
    

class OrderRepository:
    
    def get_active_orders(self,restaurant_id):
        return [Orders(restaurant_id=restaurant_id,order_id=1,slot_no_occupied=1,start_time=2,end_time=7),
                Orders(restaurant_id=restaurant_id,order_id=2,slot_no_occupied=3,start_time=0,end_time=5)]
    

class CapacityService:
    def __init__(self, RestRepo: RestaurantRepository, OrdRepo: OrderRepository):
        self.restrepo=RestRepo
        self.ordrepo=OrdRepo
        
    def can_accept_order(self, restaurant_id: int, new_start: int, new_end: int) -> bool:
        restaurant = self.restrepo.get(restaurant_id)
        if not restaurant:
            raise Exception("Restaurant not found")

        active_orders = self.ordrepo.get_active_orders(restaurant_id)
        
        # 1. Create a list of events (Time, Change)
        # We only care about what's happening during our new order's window
        events = []
        
        for ord in active_orders:
            # Does this existing order overlap with our new one?
            # Standard overlap check: StartA < EndB and EndA > StartB
            if ord.start_time < new_end and ord.end_time > new_start:
                # Event: +1 when an order starts, -1 when it ends
                events.append((ord.start_time, 1))
                events.append((ord.end_time, -1))

        # 2. Add our new order's start as a virtual event to check initial capacity
        # This is a "Code Craft" nuance: we check the load at the exact start time.
        events.append((new_start, 0)) 

        # 3. Sort events by time
        # If times are equal, process ends (-1) before starts (+1) to be conservative
        events.sort()

        # 4. Sweep through the timeline
        current_load = 0
        for time, change in events:
            current_load += change
            
            # If the event falls within or at the start of our new order
            if time >= new_start and time < new_end:
                # Check if we are at capacity
                # We add +1 because we are trying to fit the NEW order in
                if current_load + 1 > restaurant.total_slots:
                    return False

        return True
        