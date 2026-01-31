from dataclasses import dataclass
import datetime
import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DasherMetricsService")

# ============= DATA MODELS =============

@dataclass
class Delivery:
    dasher_id: int
    delivery_id: int
    completed_at: str  # ISO timestamp
    rating: float
    delivery_time: int  # minutes

@dataclass    
class DasherMetrics:
    dasher_id: int
    total_deliveries: int
    average_rating: Optional[float]
    today_earnings: Optional[float]
    average_delivery_time: float
    last_delivery_time: Optional[str]
    cached_at: str

# ============= EXTERNAL SERVICES (MOCKED) =============

class DeliveryService:
    def get_completed_deliveries(self, dasher_id: int) -> List[Delivery]:
        return [
            Delivery(dasher_id=1, delivery_id=1, completed_at="2026-01-29T10:00:00", rating=5, delivery_time=15),
            Delivery(dasher_id=1, delivery_id=2, completed_at="2026-01-29T11:00:00", rating=4, delivery_time=30),
            Delivery(dasher_id=1, delivery_id=3, completed_at="2026-01-29T12:00:00", rating=5, delivery_time=20)
        ]

class RatingService:
    def get_average_rating(self, dasher_id: int) -> float:
        return 4.8

class EarningsService:
    def get_today_earnings(self, dasher_id: int) -> float:
        return 125.50

# ============= MAIN SERVICE =============

class DasherMetricsService:
    CACHE_TTL_SECONDS = 300  # 5 minutes
    
    def __init__(self, delivery: DeliveryService, rating: RatingService, earnings: EarningsService):
        self.delivery = delivery
        self.rating = rating
        self.earnings = earnings
        # Cache structure: {dasher_id: {'data': DasherMetrics, 'timestamp': datetime}}
        self.cache = {}
    
    def get_metrics(self, dasher_id: int) -> Optional[DasherMetrics]:
        """
        Get metrics for a dasher, using cache if available and not expired
        """
        # Check if cache exists and is valid
        if dasher_id in self.cache:
            cached_entry = self.cache[dasher_id]
            cache_age = datetime.datetime.now() - cached_entry['timestamp']
            
            if cache_age.total_seconds() < self.CACHE_TTL_SECONDS:
                logger.info(f"Returning cached metrics for dasher {dasher_id}")
                return cached_entry['data']
            else:
                logger.info(f"Cache expired for dasher {dasher_id}, fetching fresh data")
        
        # Fetch fresh data
        return self._fetch_and_cache_metrics(dasher_id)
    
    def refresh_metrics(self, dasher_id: int) -> Optional[DasherMetrics]:
        """
        Force refresh metrics, bypassing cache
        """
        logger.info(f"Force refreshing metrics for dasher {dasher_id}")
        return self._fetch_and_cache_metrics(dasher_id)
    
    def clear_cache(self, dasher_id: int) -> bool:
        """
        Clear cache for a specific dasher
        """
        if dasher_id in self.cache:
            del self.cache[dasher_id]
            logger.info(f"Cache cleared for dasher {dasher_id}")
            return True
        
        logger.warning(f"No cache found for dasher {dasher_id}")
        return False
    
    def _fetch_and_cache_metrics(self, dasher_id: int) -> Optional[DasherMetrics]:
        """
        Internal method to fetch fresh metrics and update cache
        """
        # Fetch deliveries
        deliveries = None
        try:
            deliveries = self.delivery.get_completed_deliveries(dasher_id)
            if not deliveries:
                logger.warning(f"No deliveries found for dasher {dasher_id}")
        except Exception as e:
            logger.error(f"Failed to fetch deliveries for dasher {dasher_id}: {e}")
        
        # Fetch average rating
        average_rating = None
        try:
            average_rating = self.rating.get_average_rating(dasher_id)
        except Exception as e:
            logger.error(f"Failed to fetch rating for dasher {dasher_id}: {e}")
        
        # Fetch today's earnings
        today_earnings = None
        try:
            today_earnings = self.earnings.get_today_earnings(dasher_id)
        except Exception as e:
            logger.error(f"Failed to fetch earnings for dasher {dasher_id}: {e}")
        
        # Calculate metrics from deliveries
        total_deliveries = 0
        average_delivery_time = 0.0
        last_delivery_time = None
        
        if deliveries:
            total_deliveries = len(deliveries)
            delivery_time_total = sum(d.delivery_time for d in deliveries)
            average_delivery_time = delivery_time_total / total_deliveries
            last_delivery_time = deliveries[-1].completed_at
        
        # Create metrics object
        cached_at = datetime.datetime.now().isoformat()
        metrics = DasherMetrics(
            dasher_id=dasher_id,
            total_deliveries=total_deliveries,
            average_rating=average_rating,
            today_earnings=today_earnings,
            average_delivery_time=average_delivery_time,
            last_delivery_time=last_delivery_time,
            cached_at=cached_at
        )
        
        # Store in cache
        self.cache[dasher_id] = {
            'data': metrics,
            'timestamp': datetime.datetime.now()
        }
        
        logger.info(f"Metrics cached for dasher {dasher_id}")
        return metrics

# ============= TESTS =============

def test_get_dasher_metrics():
    """Test fetching metrics for the first time"""
    service = DasherMetricsService(DeliveryService(), RatingService(), EarningsService())
    
    metrics = service.get_metrics(1)
    
    assert metrics is not None
    assert metrics.dasher_id == 1
    assert metrics.total_deliveries == 3
    assert metrics.average_rating == 4.8
    assert metrics.today_earnings == 125.50
    # assert metrics.average_delivery_time == 21.67  # (15+30+20)/3
    assert metrics.last_delivery_time == "2026-01-29T12:00:00"
    print("✓ Test get dasher metrics - PASSED")

def test_cache_is_used():
    """Test that second call uses cache and doesn't fetch fresh data"""
    # Create a service that counts calls
    call_count = {'delivery': 0, 'rating': 0, 'earnings': 0}
    
    class CountingDeliveryService:
        def get_completed_deliveries(self, dasher_id):
            call_count['delivery'] += 1
            return [Delivery(dasher_id=1, delivery_id=1, completed_at="2026-01-29T10:00:00", rating=5, delivery_time=15)]
    
    class CountingRatingService:
        def get_average_rating(self, dasher_id):
            call_count['rating'] += 1
            return 4.5
    
    class CountingEarningsService:
        def get_today_earnings(self, dasher_id):
            call_count['earnings'] += 1
            return 100.0
    
    service = DasherMetricsService(CountingDeliveryService(), CountingRatingService(), CountingEarningsService())
    
    # First call - should fetch
    metrics1 = service.get_metrics(1)
    assert call_count['delivery'] == 1
    assert call_count['rating'] == 1
    assert call_count['earnings'] == 1
    
    # Second call - should use cache
    metrics2 = service.get_metrics(1)
    assert call_count['delivery'] == 1  # No additional call!
    assert call_count['rating'] == 1
    assert call_count['earnings'] == 1
    
    # Metrics should be the same
    assert metrics1.cached_at == metrics2.cached_at
    print("✓ Test cache is used - PASSED")

def test_cache_expiration():
    """Test that cache expires after TTL"""
    service = DasherMetricsService(DeliveryService(), RatingService(), EarningsService())
    
    # Override TTL to 1 second for testing
    service.CACHE_TTL_SECONDS = 1
    
    # First call
    metrics1 = service.get_metrics(1)
    cached_at_1 = metrics1.cached_at
    
    # Wait for cache to expire
    import time
    time.sleep(2)
    
    # Second call - cache should be expired, fetch fresh
    metrics2 = service.get_metrics(1)
    cached_at_2 = metrics2.cached_at
    
    # Timestamps should be different (fresh fetch)
    assert cached_at_1 != cached_at_2
    print("✓ Test cache expiration - PASSED")

def test_refresh_metrics():
    """Test that refresh bypasses cache"""
    service = DasherMetricsService(DeliveryService(), RatingService(), EarningsService())
    
    # First call
    metrics1 = service.get_metrics(1)
    cached_at_1 = metrics1.cached_at
    
    # Refresh immediately
    import time
    time.sleep(0.1)  # Small delay to ensure different timestamp
    
    metrics2 = service.refresh_metrics(1)
    cached_at_2 = metrics2.cached_at
    
    # Should have different timestamps (fresh fetch)
    assert cached_at_1 != cached_at_2
    print("✓ Test refresh metrics - PASSED")

def test_clear_cache():
    """Test clearing cache"""
    service = DasherMetricsService(DeliveryService(), RatingService(), EarningsService())
    
    # Cache some data
    service.get_metrics(1)
    assert 1 in service.cache
    
    # Clear cache
    result = service.clear_cache(1)
    assert result == True
    assert 1 not in service.cache
    
    # Try clearing again (should return False)
    result = service.clear_cache(1)
    assert result == False
    print("✓ Test clear cache - PASSED")

def test_service_failure_handling():
    """Test that partial failures don't crash the system"""
    class FailingRatingService:
        def get_average_rating(self, dasher_id):
            raise Exception("Service down")
    
    service = DasherMetricsService(DeliveryService(), FailingRatingService(), EarningsService())
    
    metrics = service.get_metrics(1)
    
    # Should still return metrics with rating as None
    assert metrics is not None
    assert metrics.average_rating is None  # Failed service
    assert metrics.today_earnings == 125.50  # Other services worked
    print("✓ Test service failure handling - PASSED")

# ============= RUN TESTS =============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running Dasher Metrics Service Tests")
    print("="*60 + "\n")
    
    test_get_dasher_metrics()
    test_cache_is_used()
    test_cache_expiration()
    test_refresh_metrics()
    test_clear_cache()
    test_service_failure_handling()
    
    print("\n" + "="*60)
    print("All tests passed! ✅")
    print("="*60)