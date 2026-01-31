#service health aggregator
from typing import DefaultDict, Dict


class Service:
    def __init__(self, data:Dict ):
        self.name = data.get("service", "unknown")
        self.status = data.get("status", "unknown")
        self.latency = data.get("latency_ms", 0)
        self.timestamp = data.get("timestamp", 0)

class HeathCheck:
    def __init__(self):
        self.heartbeats: Dict[str, Service] = {}
        self.at_risk=set()
        self.down=set()
    
    def add_heartbeat(self,service:Service):
        current = self.heartbeats.get(service.name)
        if not current or service.timestamp > current.timestamp:
            self.heartbeats[service.name] = service
    
    def get_aggregated_health(self):
        self.at_risk=set()
        self.down=set()
        for service_name in self.heartbeats:
            self.evaluate_service(service_name)

    def evaluate_service(self, service_name):
        service = self.heartbeats[service_name]
        
        is_unhealthy = service.status == "unhealthy"
        is_slow = service.latency > 500
        is_critical = service.status == "critical"

        # Check Down first (Highest priority)
        if is_critical or (is_unhealthy and is_slow):
            self.down.add(service_name)
        # Only if NOT down, check if it is At Risk
        elif is_unhealthy or is_slow:
            self.at_risk.add(service_name)
    
if __name__ == "__main__":
    import json

    health_check = HeathCheck()

    # Simulating incoming heartbeats
    heartbeats = [
        '{"service": "auth", "status": "healthy", "latency_ms": 120, "timestamp": 1625247600}',
        '{"service": "payment", "status": "unhealthy", "latency_ms": 600, "timestamp": 1625247601}',
        '{"service": "search", "status": "critical", "latency_ms": 300, "timestamp": 1625247602}',
        '{"service": "auth", "status": "healthy", "latency_ms": 700, "timestamp": 1625247603}',
        '{"service": "payment", "status": "healthy", "latency_ms": 200, "timestamp": 1625247604}'
    ]

    for hb in heartbeats:
        data = json.loads(hb)
        service = Service(data)
        health_check.add_heartbeat(service)

    health_check.get_aggregated_health()

    print("At Risk Services:", health_check.at_risk)
    print("Down Services:", health_check.down)
    
        