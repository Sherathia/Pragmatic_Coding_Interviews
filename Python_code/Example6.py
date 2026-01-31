from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ShiftInfoService")

@dataclass
class ShiftInfo:
    dasher_id: str
    shift_id: str  # Generate unique ID like "shift_123"
    start_time: str  # ISO timestamp
    is_active: bool
    error_message: Optional[str]  # If there was an error

@dataclass
class ShiftSummary:
    dasher_id: str
    shift_id: str
    start_time: str
    end_time: str
    duration_minutes: int
    earnings_eligible: bool  # True if shift >= 30 minutes



class DasherShiftService:
    def __init__(self):
        self.active_shifts={}
        self.completed_shifts={}
        
    def get_active_shift(self,dasher_id:str):
        if dasher_id not in self.active_shifts:
            logger.info("No active shifts for dasher ID")
            return None
        return self.active_shifts[dasher_id]
    
    def get_active_dashers(self):
        active_dashers=[]
        for dasher,shifts in self.active_shifts.items():
            active_dashers.append(dasher)
        return active_dashers
    
    def end_shift(self,dasher_id:str):
        current_shift =self.active_shifts[dasher_id]
        if not current_shift:
            logger.error("No active shifts for dasher ID to end")
            return None
        shift_summary = ShiftSummary( dasher_id=dasher_id,
                                                            shift_id=current_shift.shift_id,
                                                            start_time=current_shift.start_time,
                                                            end_time=datetime.now(),
                                                            duration_minutes=datetime.now()-current_shift.start_time,
                                                            earnings_eligible=True if datetime.now()-current_shift.start_time>=timedelta(minutes=30) else False)
        if dasher_id not in self.completed_shifts:
            self.completed_shifts[dasher_id]=[shift_summary]
        else:
            self.completed_shifts[dasher_id].append(shift_summary)
        del self.active_shifts[dasher_id]
        logger.info("Active shift removed")
            
    def start_shift(self,dasher_id:str):
        if dasher_id in self.active_shifts:
            logger.error("Active shifts already present for dasher ID")
            return None
        new_shift =ShiftInfo(dasher_id=dasher_id,
                             shift_id = uuid.uuid4(),
                             start_time=datetime.now(),
                             is_active=True,
                             error_message=None)
        self.active_shifts[dasher_id]=new_shift
        
def test_failure_flow():
    service=DasherShiftService()
    dasher=service.get_active_dashers()
    assert len(dasher)==0
    
def test_actual_flow():
    service=DasherShiftService()
    service.start_shift("1")
    service.start_shift("2")
    dasher=service.get_active_dashers()
    assert len(dasher)==2
    shift =service.get_active_shift("1")
    assert shift.is_active==True
    service.end_shift("2")
    dasher=service.get_active_dashers()
    assert len(dasher)==1
    
if __name__=="__main__":
    test_actual_flow()
    test_failure_flow()
    print("Tests Passed")
    
        
            