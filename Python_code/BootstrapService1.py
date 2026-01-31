import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict

# --- 1. Data Models ---
# Using dataclasses for clean, idiomatic data containers

@dataclass
class Consumer:
    user_id: int
    consumer_id: int
    consumer_name: str

@dataclass
class Payment:
    user_id: int
    payment_id: int
    default_payment: str
    gift_card_balance: int

@dataclass
class Address:
    user_id: int
    address: str

@dataclass
class UserProfile:
    consumer_id: int
    name: str
    default_payment_method: Optional[str] = None
    gift_card_balance: Optional[int] = None
    address: Optional[str] = None

# --- 2. Interfaces (ABCs) ---
# Defines the "Contract". This makes the BootstrapService testable and decoupled.

class IConsumerService(ABC):
    @abstractmethod
    def get(self, user_id: int) -> Optional[Consumer]:
        pass

class IPaymentService(ABC):
    @abstractmethod
    def get(self, user_id: int) -> Optional[Payment]:
        pass

class IAddressService(ABC):
    @abstractmethod
    def get(self, user_id: int) -> Optional[Address]:
        pass

# --- 3. Concrete Implementations ---
# In-memory versions for the HackerRank environment.

class InMemoryConsumerService(IConsumerService):
    def __init__(self):
        self._store: Dict[int, Consumer] = {}
    
    def add(self, consumer: Consumer):
        self._store[consumer.user_id] = consumer
        
    def get(self, user_id: int) -> Optional[Consumer]:
        return self._store.get(user_id)

class InMemoryPaymentService(IPaymentService):
    def __init__(self):
        self._store: Dict[int, Payment] = {}
        
    def add(self, payment: Payment):
        self._store[payment.user_id] = payment
        
    def get(self, user_id: int) -> Optional[Payment]:
        # Simulating potential service logic/errors
        return self._store.get(user_id)

class InMemoryAddressService(IAddressService):
    def __init__(self):
        self._store: Dict[int, Address] = {}
        
    def add(self, address: Address):
        self._store[address.user_id] = address
        
    def get(self, user_id: int) -> Optional[Address]:
        return self._store.get(user_id)

# --- 4. The Core BootstrapService ---

# Configure logging to satisfy the "monitoring/debugging" requirement
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BootstrapService")

class BootstrapService:
    def __init__(self, 
                 consumer_service: IConsumerService, 
                 payment_service: IPaymentService, 
                 address_service: IAddressService):
        """Dependency Injection: Coding to interfaces, not concrete classes."""
        self.consumer_service = consumer_service
        self.payment_service = payment_service
        self.address_service = address_service

    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Aggregates data. Mandatory: Consumer. Optional: Payment, Address."""
        
        # 1. Fetch Mandatory Consumer Data
        try:
            consumer = self.consumer_service.get(user_id)
            if not consumer:
                logger.error(f"User {user_id} not found in ConsumerService.")
                return None # Or raise Exception based on interviewer preference
        except Exception as e:
            logger.critical(f"ConsumerService failure for user {user_id}: {e}")
            raise

        # 2. Fetch Optional Data Gracefully
        # We wrap these in a 'safe' check so one service failure doesn't break the whole API
        payment = self._safe_fetch(self.payment_service.get, user_id, "PaymentService")
        address_obj = self._safe_fetch(self.address_service.get, user_id, "AddressService")

        return UserProfile(
            consumer_id=consumer.consumer_id,
            name=consumer.consumer_name,
            default_payment_method=payment.default_payment if payment else None,
            gift_card_balance=payment.gift_card_balance if payment else None,
            address=address_obj.address if address_obj else None
        )

    def _safe_fetch(self, fetch_func, user_id, service_name):
        """Helper to ensure partial profile returns if non-core services fail."""
        try:
            return fetch_func(user_id)
        except Exception as e:
            logger.warning(f"Graceful degradation: {service_name} failed for {user_id}. Error: {e}")
            return None

# --- 5. Execution / Example Usage ---

if __name__ == "__main__":
    # Setup Services
    c_svc = InMemoryConsumerService()
    p_svc = InMemoryPaymentService()
    a_svc = InMemoryAddressService()

    # Seed Data
    c_svc.add(Consumer(user_id=1, consumer_id=101, consumer_name="Aesha"))
    p_svc.add(Payment(user_id=1, payment_id=201, default_payment="CARD", gift_card_balance=50))
    a_svc.add(Address(user_id=1, address="New Jersey"))

    # Instantiate BootstrapService with injected dependencies
    service = BootstrapService(c_svc, p_svc, a_svc)

    # Test Case 1: Full Profile
    print(f"Full Profile: {service.get_user_profile(1)}")

    # Test Case 2: Partial Profile (Missing Address)
    c_svc.add(Consumer(user_id=2, consumer_id=102, consumer_name="Deep"))
    print(f"Partial Profile: {service.get_user_profile(2)}")