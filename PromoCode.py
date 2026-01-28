from threading import Lock

class PromoCode:
    def __init__(self, code_id,discount_amount,user_count,expiry_date,discount_type="FLAT"):
        self.code_id=code_id
        self.discount_amount=discount_amount
        self.user_count=user_count
        self.expiry_date=expiry_date
        self.discount_type=discount_type
        self.used_by=set()
        

class PromoCodeRepo:
    def __init__(self):
        self.promo={}
        self.locks={}
    
    
    def add(self,promo):
        self.promo[promo.code_id]=promo
        self.locks[promo.code_id]=Lock()
    
    def get(self,code_id):
        promo = self.promo.get(code_id)
        if not promo:
            raise Exception(f"Promo code '{code_id}' does not exist")  # 🔥 friendly error
        return promo
    
    def is_promo_valid(self,code_id):
        p =self.promo.get(code_id)
        if not p:
            return False
        if p.user_count<=0:
            return False
        if datetime.now() > p.expiry_date:   # NEW
            return False
        return True
    
    def promo_used(self,code_id,user_id):
        lock = self.locks[code_id]
        with lock:
            p = self.promo.get(code_id)
            if p.user_count <= 0:
                raise Exception("Promo fully used")
            p.used_by.add(user_id)
            p.user_count-=1
        
    def get_discount(self,code_id,order_amount):
        p=self.promo.get(code_id)
        if p.discount_type=='FLAT':
            return p.discount_amount
        elif p.discount_type=='PERCENT':
            if order_amount is None:
                raise Exception("Order amount required for percentage discount")
            return order_amount * p.discount_amount / 100
        else:
            raise Exception("Unknown discount type")

class User:
    def __init__(self,user_id,code_id,order_amount):
        self.user_id=user_id
        self.code_id=code_id
        self.usage_status = "ISSUED"
        self.order_amount=order_amount
        
        
class UserRepo:
    def __init__(self):
        self.user={}
        
    def add(self,user):
        self.user[user.user_id]=user
    
    def get(self,user_id):
        return self.user.get(user_id) 
        
            
class PromoCodeService:
    def __init__(self, promo,user):
        self.promo=promo
        self.user=user
    
    def add_promo(self,code_id,discount_amount,user_count,expiry_date,discount_type):
        promo_code = PromoCode(code_id,discount_amount,user_count,expiry_date,discount_type)
        self.promo.add(promo_code)
        
    
    def apply_promo(self,user_id,code_id,order_amount=None):
        p=self.promo.get(code_id)
        if not self.promo.is_promo_valid(code_id):
            raise Exception("Promo not Valid")
        
        if user_id in p.used_by:
            raise Exception("Promo already used by this user")
        
        user = User(user_id,code_id,order_amount)
        self.user.add(user)
        self.promo.promo_used(code_id,user_id)
        return self.promo.get_discount(code_id, order_amount)
    
    def get_promo_status(self,code_id):
        p=self.promo.get(code_id)
        if not p:
            raise Exception("Promo doesn't Exist")
        return {"code_id":p.code_id,
                "discount_amount":p.discount_amount,
                "user_count":p.user_count,
                "expiry_date":p.expiry_date}

from datetime import datetime, time

expiry1 = datetime(2026, 10, 10)
expiry2 = datetime(2026, 5, 5)

pRepo= PromoCodeRepo()
uRepo=UserRepo()
service=PromoCodeService(pRepo,uRepo)
service.add_promo(1,50,10,expiry1,"FLAT")
service.add_promo(2,50,2,expiry2,"PERCENT")
print(service.apply_promo(1,1))
print(service.apply_promo(2,2,10))
# service.apply_promo(1,1)
print(service.get_promo_status(1))
print(service.get_promo_status(2))
        
    
    
        