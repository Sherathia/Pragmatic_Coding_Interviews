from dataclasses import dataclass
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)

@dataclass
class OrderInfo:
    dasher_id: int
    order_id: int
    start: int   # minutes since shift start
    end: int
    miles: float


class OrderRepository:
    def get_orders(self, dasher_id: int) -> List[OrderInfo]:
        return [
            OrderInfo(dasher_id, 1, 0, 30, 5),
            OrderInfo(dasher_id, 2, 15, 45, 5),   # overlaps with order 1
        ]


class PaymentService:
    BASE_PAY = 5
    MILE_RATE = 0.5
    PEAK_MULTIPLIER = 1.5   # if start time >= 30

    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def calculate_payment(self, dasher_id: int) -> float:
        orders = self.repo.get_orders(dasher_id)
        if not orders:
            return 0

        events = []
        miles = 0
        peak_bonus = 0

        for o in orders:
            if o.end <= o.start:
                raise ValueError("Invalid order")

            events.append((o.start, 1))
            events.append((o.end, -1))
            miles += o.miles

            if o.start >= 30:   # pretend 30+ mins = peak
                peak_bonus += self.BASE_PAY * (self.PEAK_MULTIPLIER - 1)

        events.sort()

        active = 0
        last = events[0][0]
        paid_blocks = 0

        for time, change in events:
            if active > 0:
                paid_blocks += 1
            active += change
            last = time

        base_pay = paid_blocks * self.BASE_PAY
        total = base_pay + (miles * self.MILE_RATE) + peak_bonus

        logging.info(f"base={base_pay}, miles={miles}, peak={peak_bonus}, total={total}")
        return round(total, 2)

repo = OrderRepository()
service = PaymentService(repo)
print(service.calculate_payment(1))

def test_overlap():
    repo = OrderRepository()
    service = PaymentService(repo)
    assert service.calculate_payment(1) == 10  # 1 base (5) + miles (5)

def test_bad_order():
    class BadRepo(OrderRepository):
        def get_orders(self, dasher_id):
            return [OrderInfo(dasher_id, 1, 10, 5, 2)]

    try:
        PaymentService(BadRepo()).calculate_payment(1)
        assert False
    except ValueError:
        assert True

