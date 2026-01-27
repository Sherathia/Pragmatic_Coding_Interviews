from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    
    def __init__(self, limit: int, time: int):
        self.user_request=defaultdict(deque) # deque is in memory so multiple servers handling request each server will have its own counts
        self.request_limit=limit
        self.time_window=time
        self.lock=Lock()
    

    def add_request(self, user_id, timestamp):
        while self.lock:
            self.user_request[user_id].append(timestamp)
            while self.user_request[user_id] and self.user_request[user_id][0]+self.time_window < timestamp:
                self.user_request[user_id].popleft()
            
            if len(self.user_request[user_id]) > self.request_limit:
                return False
            return True

if __name__ == "__main__":
    rl=RateLimiter(3,10)
    # print(rl.add_request(1, 1)) #True
    # print(rl.add_request(2, 2)) #True
    # print(rl.add_request(3, 3)) #True
    # print(rl.add_request(4, 4))
    print(rl.add_request(11, 11)) #True
    print(rl.add_request(11, 10)) #True
    print(rl.add_request(11, 12))
    print(rl.add_request(11, 13))
    print(rl.add_request(11, 15)) #True
    print(rl.add_request(11, 14)) #False
