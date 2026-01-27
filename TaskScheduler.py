from collections import defaultdict
import heapq
from threading import Lock


class TaskScheduler:
    
    def __init__(self):
        self.schedule=defaultdict(list)
    
    def schedule_notification(self,user_id: int, message :str, send_at:int):
        self.schedule[send_at].append([user_id,message])
        
    def get_ready(self,current_time:int):
        read_notifications=[]
        for send_at in list(self.schedule.keys()):
            if send_at <=current_time:
                read_notifications.extend(self.schedule[send_at])
                del self.schedule[send_at]
        return read_notifications

class TaskScheduler1:
    
    def __init__(self):
        self.scheduler=[]
        self.lock=Lock()
    
    def schedule_notification(self,user_id: int, message :str, send_at:int):
        heapq.heappush(self.scheduler,(send_at,user_id,message))
    
    def get_ready(self,current_time:int):
        read_notifications=[]
        with self.lock:  # prevents race conditions
            while self.scheduler and self.scheduler[0][0]<=current_time:
                send_at,user_id,message = heapq.heappop(self.scheduler)
                read_notifications.append((user_id,message))
            return read_notifications
        
        
            
if __name__=="__main__":
    schedule=TaskScheduler()
    schedule.schedule_notification(1,"Hello User 1",10)
    schedule.schedule_notification(2,"Hello User 2",5)
    schedule.schedule_notification(3,"Hello User 1",5)
    print(schedule.get_ready(5)) # [(2, 'Hello User 2'), (3, 'Hello User 1')]
    print(schedule.get_ready(10)) # [(1, 'Hello User 1')]
    print(schedule.get_ready(15)) # []          
        