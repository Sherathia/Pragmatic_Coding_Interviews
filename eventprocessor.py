from Event import Event
from threading import Lock


class eventprocessor:

    def __init__(self):
        self.event_processor={}
        self.counts={}
        self.lock=Lock()
        
    def register_event(self,event:Event):
        with self.lock: ## Ensure thread safety, only one thread can modify at a time, No race conditions
            if not event.user_id or not event.event_type:
                raise ValueError("Invalid input")
            if event.user_id not in self.event_processor:
                self.event_processor[event.user_id]=[[event.event_type,event.timestamp]]
            else:
                self.event_processor[event.user_id].append([event.event_type,event.timestamp])
            self.counts[event.event_type]=self.counts.get(event.event_type,0)+1
            
    def get_all_events(self,user_id : int):
        if user_id in self.event_processor:
            events= self.event_processor[user_id]
            return sorted(events,key=lambda x:x[1])
        else:
            return []
    
    def get_events_by_type(self,user_id: int,event_type: str):
        if user_id in self.event_processor:
            return [event for event in self.event_processor[user_id] if event[0]==event_type]
        else:
            return []
        
    def get_event_counts(self):
        event_counts={}
        for event in self.event_processor.values():
            for event_type,timestamp in event:
                if event_type in event_counts:
                    event_counts[event_type]+=1
                else:
                    event_counts[event_type]=1
        return event_counts
    
    
if __name__=='__main__':
    ep = eventprocessor()
    ep.register_event(1,"Click",12)
    ep.register_event(1,"View",15)
    ep.register_event(2,"Click",20)
    print(ep.get_all_events(1))  # [(Click,12),(View,15)]
    print(ep.get_events_by_type(1,"Click"))  # [(Click,12)] 
    print(ep.get_event_counts())  # {Click:2, View:1}