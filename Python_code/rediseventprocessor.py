import json
from threading import Lock
from redis import Redis

#redis used so it is concurrent by default
# data survives process restarts as it is stored in redis server
# Multiple backend can read and write to the same redis server
# O(1) time complexity for read and write operations

class rediseventprocessor:

    def __init__(self):
        self.r = Redis(host=redis_host, port=redis_port, decode_responses=True)

    def register_event(self,user_id: int, event_type: str, timestamp: int):
        event = json.dumps({"event_type": event_type, "timestamp": timestamp})
        self.r.rpush(f"user:{user_id}:events", event) # Store event in Redis list, rpush appends to the right of the list
        self.r.hincrby("event_counts", event_type, 1) # Hash Increment By , event_counts is hashname Increment event count in Redis hash
        
            
    def get_all_events(self,user_id : int):
        events = self.r.lrange(f"user:{user_id}:events", 0, -1)
        return [json.loads(event) for event in events]
            
    
    def get_events_by_type(self,user_id: int,event_type: str):
        events = self.get_all_events(user_id)
        return [json.loads(event) for event in events if json.loads(event)["event_type"] == event_type]

    def get_event_counts(self):
        counts = self.r.hgetall("event_counts") # Get all event counts from Redis hash
        # Convert counts from string to int
        return {k: int(v) for k, v in counts.items()}
    
    
if __name__=='__main__':
    ep = eventprocessor()
    ep.register_event(1,"Click",12)
    ep.register_event(1,"View",15)
    ep.register_event(2,"Click",20)
    print(ep.get_all_events(1))  # [(Click,12),(View,15)]
    print(ep.get_events_by_type(1,"Click"))  # [(Click,12)] 
    print(ep.get_event_counts())  # {Click:2, View:1}