from dataclasses import dataclass
from typing import Dict

@dataclass
class Consumer:
    user_id:int
    consumer_id:int
    consumer_name:str
    
class ConsumerService:
    def __init__(self):
        self.consumer: Dict[int,Consumer]={}
    
    def add(self,consumer):
        self.consumer[consumer.user_id]=consumer
    
    def get(self,user_id):
        return self.consumer.get(user_id)

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

class PaymentService:
    def __init__(self):
        self.payment: Dict[int,Payment]={}
        
        
    def add(self,payment):
        self.payment[payment.user_id]=payment
    
    def get(self,user_id):
        payment= self.payment.get(user_id)
        if not payment:
            return None
        return payment
    
class AddressService:
    def __init__(self):
        self.address: Dict[int,Address]={}
        
        
    def add(self,address):
        self.address[address.user_id]=address
    
    def get(self,user_id):
        address= self.address.get(user_id)
        if not address:
            return None
        return address

@dataclass
class UserProfile:
    consumerId: int
    name: str
    defaultPaymentMethod: str | None
    giftCardBalance: int | None
    address: str | None
    
        
class BootstrapService:
    def __init__(self, consumer:ConsumerService, payment:PaymentService, address:AddressService):
        self.consumer = consumer
        self.payment=payment
        self.address=address

    def get_user_profile(self,user_id):
        c = self.consumer.get(user_id)
        if not c:
            raise Exception("Consumer not found")
        p = self.payment.get(user_id)
        a = self.address.get(user_id)
        
        return UserProfile( consumerId=c.consumer_id,
                            name=c.consumer_name,
                            defaultPaymentMethod=p.default_payment if p else None,
                            giftCardBalance=p.gift_card_balance if p else None,
                            address=a.address if a else None)
    
c=ConsumerService()
p=PaymentService()
a=AddressService()
c.add(
    Consumer(user_id=1, consumer_id=101, consumer_name="Aesha")
)

p.add(
    Payment(user_id=1, payment_id=201, default_payment="CARD", gift_card_balance=50)
)

a.add(
    Address(user_id=1, address="New Jersey")
)

c.add(
    Consumer(user_id=2, consumer_id=104, consumer_name="Aesha")
)

p.add(
    Payment(user_id=2, payment_id=201, default_payment="CARD", gift_card_balance=50)
)

# a.add(
#     Address(user_id=2, address="New Jersey")
# )

service=BootstrapService(c,p,a)    
# service.create_user_profile(1,1,"Aesha",123,"card",20,"Jersey")    
# service.create_user_profile(2,2,"Deep",123,"card",50,"Jersey")   
print(service.get_user_profile(1))
print(service.get_user_profile(2))
