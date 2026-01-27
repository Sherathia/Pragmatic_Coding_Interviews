from typing import DefaultDict
import unittest


class Slot:
    def __init__(self, slot_id,start_time,capacity):
        self.id=slot_id
        self.start_time=start_time
        self.capacity = capacity
        self.booked_users=set()
    
    def get_capacity(self):
        return self.capacity-len(self.booked_users)
    
    def is_full(self):
        return self.capacity==len(self.booked_users)
        
    
class User:
    def __init__(self, user_id):
        self.user_id=user_id
    
class BookingService:
    def __init__(self):
        self.slots={}
        self.users={}
        
    def add_slot(self,slot):
        self.slots[slot.id]=slot
    
    def add_user(self,user):
        if user.user_id in self.users:
            raise Exception("User Already Exists")
        self.users[user.user_id]=user
        
    
    def book_slot(self,user_id,slot_id):
        if user_id not in self.users:
            raise Exception("User Doesn't Exists")
    
        if slot_id not in self.slots:
            raise Exception("Slot Doesn't Exists")

        if user_id in self.slots[slot_id].booked_users:
            raise Exception("Slot Already Booked")
        elif self.slots[slot_id].is_full():
            raise Exception("Slot Already Full")
        else:
            self.slots[slot_id].booked_users.add(user_id)
        
        return f"User {user_id} booked slot {slot_id} successfully"
    
    
    def cancel_booking(self,user_id,slot_id):
        if user_id not in self.users:
            raise Exception("User Doesn't Exists")
    
        if slot_id not in self.slots:
            raise Exception("Slot Doesn't Exists")
        
        if user_id not in self.slots[slot_id].booked_users:
            raise Exception("Booking doesn't exist")
        else:
            self.slots[slot_id].booked_users.remove(user_id)
        
        return f"User {user_id} cancelled booking for slot {slot_id}"
    
    def get_slot_status(self,slot_id):
        if slot_id not in self.slots:
            raise Exception("Slot Doesn't Exists")
        
        slot= self.slots[slot_id]
        return {
            "slot_id": slot.id,
            "start_time": slot.start_time,
            "capacity": slot.capacity,
            "booked_count": len(slot.booked_users),
            "booked_users": list(slot.booked_users)
        }
        
service=BookingService()
service.add_slot(Slot(1,"12",3))
service.add_slot(Slot(2,"13",1))

service.add_user(User(101))
service.add_user(User(102))
service.add_user(User(103))

print(service.book_slot(101, 1))  # OK
print(service.book_slot(102, 1))  # OK

print(service.cancel_booking(101, 1))  # OK

print(service.get_slot_status(1))

def run_Tests():
    service=BookingService()
    service.add_slot(Slot(1, "12:00", 2))
    service.add_slot(Slot(2, "13:00", 1))
    service.add_user(User(101))
    service.add_user(User(102))
    service.add_user(User(103))

    # Test 1: successful booking
    result = service.book_slot(101, 1)
    assert result == "User 101 booked slot 1 successfully"
    
    status = service.get_slot_status(1)
    assert status["booked_count"] == 1
    assert 101 in status["booked_users"]

    # Test 2: duplicate booking
    try:
        service.book_slot(101, 1)
        assert False, "Expected duplicate booking error"
    except Exception as e:
        assert str(e) == "Slot Already Booked"

    # Test 3: slot full
    service.book_slot(102, 2)
    try:
        service.book_slot(103, 2)
        assert False, "Expected slot full error"
    except Exception as e:
        assert str(e) == "Slot Already Full"

    # Test 4: cancel booking
    result = service.cancel_booking(101, 1)
    assert result == "User 101 cancelled booking for slot 1"

    status = service.get_slot_status(1)
    assert status["booked_count"] == 0

    # Test 5: invalid user
    try:
        service.book_slot(999, 1)
        assert False, "Expected invalid user error"
    except Exception as e:
        assert str(e) == "User Doesn't Exists"

    print("ALL TESTS PASSED ✅")
    
if __name__ == "__main__":
    run_Tests()
    