from dataclasses import dataclass
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MenuAvailabilityService")

# ============= DATA MODELS =============

@dataclass
class MenuItem:
    item_id: str
    name: str
    price: float
    tags: List[str]  # e.g., ["vegetarian", "gluten-free", "meat"]

@dataclass
class Menu:
    restaurant_id: str
    items: List[MenuItem]

# ============= EXTERNAL SERVICES (MOCKED) =============

class MenuRepository:
    """Simulates database of restaurant menus"""
    def getFullMenu(self, restaurant_id: str) -> Optional[Menu]:
        # Mock data - in real world, this would query a database
        if restaurant_id == "rest_123":
            return Menu(
                restaurant_id=restaurant_id,
                items=[
                    MenuItem(item_id="item_1", name="Burger", price=10.99, tags=["meat"]),
                    MenuItem(item_id="item_2", name="Salad", price=8.99, tags=["vegetarian", "gluten-free"]),
                    MenuItem(item_id="item_3", name="Pizza", price=12.99, tags=["vegetarian"]),
                    MenuItem(item_id="item_4", name="Pasta", price=11.99, tags=["vegetarian"])
                ]
            )
        return None

class CustomerPreferenceService:
    """Simulates customer preference/profile service"""
    def getDietaryRestrictions(self, customer_id: str) -> List[str]:
        # Mock data
        if customer_id == "cust_456":
            return ["vegetarian"]
        return []

class InventoryService:
    """Simulates real-time inventory checking"""
    def checkStock(self, restaurant_id: str, item_id: str) -> bool:
        # Mock: item_4 is out of stock
        if item_id == "item_4":
            return False
        return True

# ============= MAIN SERVICE =============

class MenuAvailabilityService:
    def __init__(self, 
                 menu_repo: MenuRepository, 
                 customer_service: CustomerPreferenceService, 
                 inventory_service: InventoryService):
        self.menu_repo = menu_repo
        self.customer_service = customer_service
        self.inventory_service = inventory_service
        
        # In-memory storage for manually disabled items
        # Key: (restaurant_id, item_id), Value: reason
        self.unavailable_items = {}
    
    def getAvailableMenu(self, restaurant_id: str, customer_id: str) -> Optional[Menu]:
        """
        Returns menu with only available items based on:
        1. Manual availability status
        2. Inventory stock
        3. Customer dietary preferences
        """
        # Get full menu from repository
        full_menu = self.menu_repo.getFullMenu(restaurant_id)
        if not full_menu:
            logger.error(f"Restaurant {restaurant_id} not found")
            return None
        
        # Get customer dietary restrictions
        dietary_restrictions = []
        try:
            dietary_restrictions = self.customer_service.getDietaryRestrictions(customer_id)
            logger.info(f"Customer {customer_id} restrictions: {dietary_restrictions}")
        except Exception as e:
            logger.error(f"Failed to get dietary restrictions: {e}")
            # Continue without dietary filtering
        
        # Filter items
        available_items = []
        for item in full_menu.items:
            # Check 1: Is it manually marked unavailable?
            if (restaurant_id, item.item_id) in self.unavailable_items:
                logger.info(f"Item {item.item_id} manually disabled: {self.unavailable_items[(restaurant_id, item.item_id)]}")
                continue
            
            # Check 2: Is it in stock?
            try:
                in_stock = self.inventory_service.checkStock(restaurant_id, item.item_id)
                if not in_stock:
                    logger.info(f"Item {item.item_id} out of stock")
                    continue
            except Exception as e:
                logger.error(f"Failed to check stock for {item.item_id}: {e}")
                # Assume available if check fails
            
            # Check 3: Does it match dietary restrictions?
            if dietary_restrictions:
                # Item must have at least one tag matching restrictions
                if not any(restriction in item.tags for restriction in dietary_restrictions):
                    logger.info(f"Item {item.item_id} doesn't match dietary restrictions")
                    continue
            
            # Item passed all checks!
            available_items.append(item)
        
        return Menu(restaurant_id=restaurant_id, items=available_items)
    
    def markItemUnavailable(self, restaurant_id: str, item_id: str, reason: str) -> bool:
        """
        Mark an item as unavailable for a restaurant
        """
        # Verify restaurant and item exist
        full_menu = self.menu_repo.getFullMenu(restaurant_id)
        if not full_menu:
            logger.error(f"Restaurant {restaurant_id} not found")
            return False
        
        # Check if item exists in menu
        item_exists = any(item.item_id == item_id for item in full_menu.items)
        if not item_exists:
            logger.error(f"Item {item_id} not found in restaurant {restaurant_id}")
            return False
        
        # Mark as unavailable
        self.unavailable_items[(restaurant_id, item_id)] = reason
        logger.info(f"Item {item_id} marked unavailable at {restaurant_id}. Reason: {reason}")
        return True
    
    def markItemAvailable(self, restaurant_id: str, item_id: str) -> bool:
        """
        Mark a previously unavailable item as available
        """
        key = (restaurant_id, item_id)
        if key in self.unavailable_items:
            del self.unavailable_items[key]
            logger.info(f"Item {item_id} marked available at {restaurant_id}")
            return True
        
        logger.warning(f"Item {item_id} was not marked unavailable at {restaurant_id}")
        return False


# ============= TESTS =============

def test_get_available_menu_with_dietary_restrictions():
    """Test filtering by customer dietary preferences"""
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        InventoryService()
    )
    
    menu = service.getAvailableMenu("rest_123", "cust_456")
    
    assert menu is not None
    assert len(menu.items) == 2  # Only Salad and Pizza (item_4 out of stock)
    assert all("vegetarian" in item.tags for item in menu.items)
    print("✓ Test dietary restrictions - PASSED")

def test_mark_item_unavailable():
    """Test manually marking item unavailable"""
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        InventoryService()
    )
    
    # Mark burger unavailable
    result = service.markItemUnavailable("rest_123", "item_1", "Kitchen equipment broken")
    assert result == True
    
    # Get menu - burger should not appear
    menu = service.getAvailableMenu("rest_123", "cust_no_restrictions")
    item_ids = [item.item_id for item in menu.items]
    assert "item_1" not in item_ids
    
    print("✓ Test mark unavailable - PASSED")

def test_mark_item_available_again():
    """Test re-enabling a disabled item"""
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        InventoryService()
    )
    
    # Mark unavailable then available
    service.markItemUnavailable("rest_123", "item_2", "Temporary shortage")
    result = service.markItemAvailable("rest_123", "item_2")
    
    assert result == True
    
    # Item should appear in menu now
    menu = service.getAvailableMenu("rest_123", "cust_456")
    item_ids = [item.item_id for item in menu.items]
    assert "item_2" in item_ids
    
    print("✓ Test mark available - PASSED")

def test_inventory_out_of_stock():
    """Test that out-of-stock items are filtered"""
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        InventoryService()
    )
    
    # item_4 (Pasta) is mocked as out of stock
    menu = service.getAvailableMenu("rest_123", "cust_456")
    item_ids = [item.item_id for item in menu.items]
    
    assert "item_4" not in item_ids  # Pasta should be filtered out
    print("✓ Test inventory stock - PASSED")

def test_nonexistent_restaurant():
    """Test handling of invalid restaurant ID"""
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        InventoryService()
    )
    
    menu = service.getAvailableMenu("invalid_rest", "cust_456")
    assert menu is None
    print("✓ Test invalid restaurant - PASSED")

def test_service_failure_graceful_handling():
    """Test that service failures don't crash the system"""
    class FailingInventoryService:
        def checkStock(self, restaurant_id, item_id):
            raise Exception("Service timeout")
    
    service = MenuAvailabilityService(
        MenuRepository(),
        CustomerPreferenceService(),
        FailingInventoryService()
    )
    
    # Should still return menu (assuming items available when check fails)
    menu = service.getAvailableMenu("rest_123", "cust_456")
    assert menu is not None
    assert len(menu.items) > 0
    print("✓ Test service failure handling - PASSED")


# ============= RUN TESTS =============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Running Menu Availability Service Tests")
    print("="*50 + "\n")
    
    test_get_available_menu_with_dietary_restrictions()
    test_mark_item_unavailable()
    test_mark_item_available_again()
    test_inventory_out_of_stock()
    test_nonexistent_restaurant()
    test_service_failure_graceful_handling()
    
    print("\n" + "="*50)
    print("All tests passed! ✅")
    print("="*50)