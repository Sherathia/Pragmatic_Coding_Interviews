from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

@dataclass
class RateLimitInfo:
    allowed: bool
    remaining_requests: int
    reset_time: str  # When the limit resets
    retry_after_seconds: Optional[int] = None  # If rejected, wait this long

class RateLimiter:
    """
    Simple token bucket rate limiter
    Default: 100 requests per minute per user
    """
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Track requests per user: {user_id: {'count': int, 'window_start': datetime}}
        self.user_requests: Dict[str, Dict] = {}
    
    def is_allowed(self, user_id: str) -> RateLimitInfo:
        """
        Check if request is allowed for user
        Returns RateLimitInfo with decision and metadata
        """
        now = datetime.now()
        
        # First request from this user
        if user_id not in self.user_requests:
            self.user_requests[user_id] = {
                'count': 1,
                'window_start': now
            }
            return RateLimitInfo(
                allowed=True,
                remaining_requests=self.max_requests - 1,
                reset_time=(now + timedelta(seconds=self.window_seconds)).isoformat()
            )
        
        user_data = self.user_requests[user_id]
        window_start = user_data['window_start']
        elapsed = (now - window_start).total_seconds()
        
        # Window has expired - reset counter
        if elapsed >= self.window_seconds:
            self.user_requests[user_id] = {
                'count': 1,
                'window_start': now
            }
            return RateLimitInfo(
                allowed=True,
                remaining_requests=self.max_requests - 1,
                reset_time=(now + timedelta(seconds=self.window_seconds)).isoformat()
            )
        
        # Still in same window
        current_count = user_data['count']
        
        # Under limit - allow request
        if current_count < self.max_requests:
            self.user_requests[user_id]['count'] += 1
            return RateLimitInfo(
                allowed=True,
                remaining_requests=self.max_requests - current_count - 1,
                reset_time=(window_start + timedelta(seconds=self.window_seconds)).isoformat()
            )
        
        # Over limit - reject request
        reset_time = window_start + timedelta(seconds=self.window_seconds)
        retry_after = int((reset_time - now).total_seconds())
        
        return RateLimitInfo(
            allowed=False,
            remaining_requests=0,
            reset_time=reset_time.isoformat(),
            retry_after_seconds=retry_after
        )
    
    def reset(self, user_id: str):
        """Reset rate limit for a user (admin function)"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]


# ==================== TESTS ====================

def test_basic_rate_limiting():
    """Test that requests are allowed up to limit"""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    # First 3 requests should pass
    result1 = limiter.is_allowed("user_1")
    assert result1.allowed == True
    assert result1.remaining_requests == 2
    
    result2 = limiter.is_allowed("user_1")
    assert result2.allowed == True
    assert result2.remaining_requests == 1
    
    result3 = limiter.is_allowed("user_1")
    assert result3.allowed == True
    assert result3.remaining_requests == 0
    
    # 4th request should fail
    result4 = limiter.is_allowed("user_1")
    assert result4.allowed == False
    assert result4.retry_after_seconds > 0
    
    print("✓ Test basic rate limiting - PASSED")

def test_different_users_independent():
    """Test that different users have independent limits"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    
    # User 1 makes 2 requests
    limiter.is_allowed("user_1")
    limiter.is_allowed("user_1")
    
    # User 1 is now blocked
    result = limiter.is_allowed("user_1")
    assert result.allowed == False
    
    # User 2 should still be allowed
    result = limiter.is_allowed("user_2")
    assert result.allowed == True
    
    print("✓ Test different users independent - PASSED")

def test_window_reset():
    """Test that window resets after time expires"""
    limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window
    
    # Make 2 requests
    limiter.is_allowed("user_1")
    limiter.is_allowed("user_1")
    
    # 3rd request blocked
    result = limiter.is_allowed("user_1")
    assert result.allowed == False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should be allowed now
    result = limiter.is_allowed("user_1")
    assert result.allowed == True
    
    print("✓ Test window reset - PASSED")

def test_reset_user():
    """Test manually resetting a user's limit"""
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    
    # Use up limit
    limiter.is_allowed("user_1")
    result = limiter.is_allowed("user_1")
    assert result.allowed == False
    
    # Reset user
    limiter.reset("user_1")
    
    # Should be allowed again
    result = limiter.is_allowed("user_1")
    assert result.allowed == True
    
    print("✓ Test reset user - PASSED")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running Rate Limiter Tests")
    print("="*60 + "\n")
    
    test_basic_rate_limiting()
    test_different_users_independent()
    test_window_reset()
    test_reset_user()
    
    print("\n" + "="*60)
    print("All tests passed! ✅")
    print("="*60)