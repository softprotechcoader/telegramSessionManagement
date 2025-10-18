"""
Human-like behavior simulation for Telegram automation
"""
import asyncio
import random
import time
from typing import Optional
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from config import (
    MIN_DELAY, MAX_DELAY, TYPING_DELAY_MIN, TYPING_DELAY_MAX,
    READ_TIME_MIN, READ_TIME_MAX, MAX_REQUESTS_PER_MINUTE,
    FLOOD_WAIT_RETRY_DELAY, MAX_RETRIES
)


class HumanBehavior:
    """Simulates human-like behavior for Telegram operations"""
    
    def __init__(self):
        self.request_times = []
        self.last_activity = time.time()
    
    async def random_delay(self, min_delay: float = MIN_DELAY, max_delay: float = MAX_DELAY):
        """Add random delay between actions"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
        self.last_activity = time.time()
    
    async def typing_simulation(self, text: str = ""):
        """Simulate human typing with random pauses"""
        if not text:
            return
        
        # Simulate typing each character with random delays
        for char in text:
            if char.isspace():
                # Longer pause for spaces
                await asyncio.sleep(random.uniform(0.1, 0.3))
            else:
                # Random typing speed
                await asyncio.sleep(random.uniform(TYPING_DELAY_MIN, TYPING_DELAY_MAX))
    
    async def simulate_reading(self, message_length: int = 100):
        """Simulate time spent reading a message"""
        # Base reading time + additional time based on message length
        base_time = random.uniform(READ_TIME_MIN, READ_TIME_MAX)
        length_factor = message_length / 1000  # Additional time for longer messages
        total_time = base_time + length_factor
        
        await asyncio.sleep(min(total_time, 30))  # Cap at 30 seconds
    
    def rate_limit_check(self):
        """Check if we're within rate limits"""
        current_time = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= MAX_REQUESTS_PER_MINUTE:
            return False
        return True
    
    def record_request(self):
        """Record a request for rate limiting"""
        self.request_times.append(time.time())
    
    async def handle_flood_wait(self, error: FloodWaitError):
        """Handle flood wait errors with exponential backoff"""
        wait_time = error.seconds + random.uniform(1, 5)  # Add some randomness
        print(f"⏳ Flood wait error: waiting {wait_time:.1f} seconds...")
        await asyncio.sleep(wait_time)
    
    async def safe_request(self, client: TelegramClient, method_name: str, *args, **kwargs):
        """Execute a request with rate limiting and flood wait handling"""
        # Check rate limits
        if not self.rate_limit_check():
            print("⏳ Rate limit reached, waiting...")
            await asyncio.sleep(60)
        
        # Add random delay before request
        await self.random_delay(0.5, 2.0)
        
        # Record the request
        self.record_request()
        
        # Execute with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                method = getattr(client, method_name)
                result = await method(*args, **kwargs)
                return result
            except FloodWaitError as e:
                await self.handle_flood_wait(e)
                if attempt == MAX_RETRIES - 1:
                    raise
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                print(f"⚠️ Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                await self.random_delay(2, 5)
        
        return None
    
    async def simulate_online_activity(self):
        """Simulate being online with random activity patterns"""
        # Random chance to be "away" for a bit
        if random.random() < 0.1:  # 10% chance
            away_time = random.uniform(30, 120)  # 30 seconds to 2 minutes
            print(f"😴 Simulating away time: {away_time:.1f} seconds")
            await asyncio.sleep(away_time)
    
    async def pre_action_delay(self):
        """Random delay before any major action"""
        await self.random_delay(1, 3)
    
    async def post_action_delay(self):
        """Random delay after any major action"""
        await self.random_delay(0.5, 2)
    
    def get_random_user_agent(self):
        """Get a random user agent to appear more human-like"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
        ]
        return random.choice(user_agents)


# Global instance for consistent behavior across the application
human_behavior = HumanBehavior()
