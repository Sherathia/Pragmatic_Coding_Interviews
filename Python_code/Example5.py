from dataclasses import dataclass
import heapq
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrderStatusService")

@dataclass
class ItemStats:
    item_id: str
    item_name: str
    order_count: int
    
# class Restaurant:
#     restaurant_id:str
#     item : List[ItemStats]
    
class MenuService:
    def getItemName(self,item_id:str):
        #Mock Data
        if item_id =="1":
            return "Burger"
        elif item_id=="2":
            return "Pizza"
        elif item_id=="3":
            return "Pizza1"
        elif item_id=="4":
            return "Pizza2"
        else:
            return "Unknown Item"

class PopularityTrackerService:
    def __init__(self,menu:MenuService):
        self.menu=menu
        self.restaurant: Dict[int,ItemStats]={}
        
    
    def recordOrder(self,restaurant_id:str,item_id:str,quantity:str):
        
        item_found=False
        if restaurant_id in self.restaurant:
            item  = self.restaurant[restaurant_id]
            for i in item:
                if i.item_id ==item_id:
                    item_found=True
                    i.order_count+=quantity
            if not item_found:
                logger.info("Item not found so adding to restaurant")
                item_name = self.menu.getItemName(item_id)
                self.restaurant[restaurant_id].append(ItemStats(item_id=item_id,item_name=item_name,order_count=quantity))                                             
        else:
            item_name = self.menu.getItemName(item_id)
            self.restaurant[restaurant_id]= [ItemStats(item_id=item_id,item_name=item_name,order_count=quantity)
            ]
        
        return True

    def getTopItems(self,restaurant_id:str, limit:str):
        items = self.restaurant[restaurant_id]
        heap=[]
        for item in items:
            heapq.heappush(heap,[-item.order_count, item])
        
        top_items= []
        if len(heap)<limit:
            logger.error("Item count less than limit")
        while limit>0 and len(heap)>0:
            top_items.append(heapq.heappop(heap)[1])
            limit-=1
        
        return top_items
    
    def getItemStats(self,restaurant_id:str,item_id:str):
        if restaurant_id not in self.restaurant:
            logger.error("Restaurant not found")
            return False
        
        items = self.restaurant[restaurant_id]
        for item in items:
            if item.item_id==item_id:
                return item
        
        return None
    
def test_order_Record():
    service=PopularityTrackerService(MenuService())
    service.recordOrder("1", "1", 5)
    service.recordOrder("1", "2", 7)
    service.recordOrder("1", "3", 6)
    service.recordOrder("1", "4", 1)
    service.recordOrder("2", "1", 3)
    item= service.getItemStats("1", "1")
    assert item.item_name=="Burger"
    print("Test 1 Passed")
    items =service.getTopItems("1",3)
    assert len(items)==3
    print(items)
    
if __name__=="__main__":
    test_order_Record()