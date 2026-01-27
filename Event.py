from dataclasses import dataclass

@dataclass
class Event:
       user_id: int
       event_type: str
       timestamp: int