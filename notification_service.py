"""
Notification service for monitoring Telegram channels
"""
import asyncio
import time
from typing import List, Dict, Set
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat

from config import NOTIFICATION_CHECK_INTERVAL, MAX_MESSAGES_PER_CHECK
from client_behavior import human_behavior


class NotificationService:
    """Monitors Telegram channels for new posts and sends notifications"""
    
    def __init__(self):
        self.monitored_channels = {}
        self.last_message_ids = {}
        self.is_running = False
        self.clients = {}
    
    async def add_channel(self, client: TelegramClient, channel_username: str) -> bool:
        """Add a channel to monitor"""
        try:
            # Resolve channel
            entity = await client.get_entity(channel_username)
            
            if not isinstance(entity, (Channel, Chat)):
                print(f"❌ {channel_username} is not a channel or chat")
                return False
            
            # Get initial message ID
            messages = await client.get_messages(entity, limit=1)
            last_id = messages[0].id if messages else 0
            
            self.monitored_channels[channel_username] = {
                'entity': entity,
                'client': client,
                'last_id': last_id,
                'title': getattr(entity, 'title', channel_username)
            }
            
            print(f"✅ Added channel: {entity.title} (@{channel_username})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding channel {channel_username}: {e}")
            return False
    
    async def start_monitoring(self, clients: List[TelegramClient], channels: List[str]) -> None:
        """Start monitoring channels for new posts"""
        if not clients:
            print("❌ No clients provided for monitoring")
            return
        
        if not channels:
            print("❌ No channels provided for monitoring")
            return
        
        print(f"\n🔔 Starting notification service...")
        print(f"📱 Clients: {len(clients)}")
        print(f"📺 Channels: {len(channels)}")
        print("=" * 50)
        
        # Add channels to each client
        for client in clients:
            for channel in channels:
                await self.add_channel(client, channel)
        
        if not self.monitored_channels:
            print("❌ No channels could be added for monitoring")
            return
        
        self.is_running = True
        print(f"✅ Monitoring {len(self.monitored_channels)} channels")
        print("🔄 Checking for new posts every 30 seconds...")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.is_running:
                await self._check_for_new_posts()
                await asyncio.sleep(NOTIFICATION_CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
        finally:
            self.is_running = False
    
    async def _check_for_new_posts(self) -> None:
        """Check all monitored channels for new posts"""
        for channel_username, channel_info in self.monitored_channels.items():
            try:
                await self._check_channel(channel_username, channel_info)
                # Add small delay between channel checks
                await human_behavior.random_delay(1, 3)
                
            except Exception as e:
                print(f"⚠️ Error checking {channel_username}: {e}")
    
    async def _check_channel(self, channel_username: str, channel_info: Dict) -> None:
        """Check a single channel for new posts"""
        client = channel_info['client']
        entity = channel_info['entity']
        last_id = channel_info['last_id']
        
        try:
            # Get recent messages
            messages = await client.get_messages(
                entity, 
                limit=MAX_MESSAGES_PER_CHECK,
                min_id=last_id
            )
            
            if not messages:
                return
            
            # Sort by ID to get newest first
            messages.sort(key=lambda x: x.id, reverse=True)
            
            # Update last message ID
            if messages:
                channel_info['last_id'] = messages[0].id
            
            # Process new messages
            for message in messages:
                if message.id > last_id:
                    await self._process_new_message(channel_username, channel_info, message)
                    
        except Exception as e:
            print(f"⚠️ Error checking channel {channel_username}: {e}")
    
    async def _process_new_message(self, channel_username: str, channel_info: Dict, message) -> None:
        """Process and notify about a new message"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        channel_title = channel_info['title']
        
        # Format message preview
        text_preview = ""
        if message.text:
            text_preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
        else:
            text_preview = "[Media message]"
        
        # Console notification
        print(f"\n🔔 NEW POST DETECTED!")
        print(f"📺 Channel: {channel_title} (@{channel_username})")
        print(f"⏰ Time: {timestamp}")
        print(f"👤 From: {message.sender_id}")
        print(f"📝 Message: {text_preview}")
        
        # Show media info if present
        if message.media:
            media_type = type(message.media).__name__
            print(f"📎 Media: {media_type}")
        
        # Show views if available
        if hasattr(message, 'views') and message.views:
            print(f"👀 Views: {message.views}")
        
        print("-" * 50)
        
        # Simulate reading the message
        await human_behavior.simulate_reading(len(text_preview))
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring service"""
        self.is_running = False
        print("🛑 Stopping notification service...")
    
    def get_monitored_channels(self) -> List[str]:
        """Get list of currently monitored channels"""
        return list(self.monitored_channels.keys())
    
    def remove_channel(self, channel_username: str) -> bool:
        """Remove a channel from monitoring"""
        if channel_username in self.monitored_channels:
            del self.monitored_channels[channel_username]
            print(f"✅ Removed channel: {channel_username}")
            return True
        else:
            print(f"⚠️ Channel not found: {channel_username}")
            return False
    
    async def test_channel_access(self, client: TelegramClient, channel_username: str) -> bool:
        """Test if we can access a channel"""
        try:
            entity = await client.get_entity(channel_username)
            messages = await client.get_messages(entity, limit=1)
            print(f"✅ Channel access test successful: {channel_username}")
            return True
        except Exception as e:
            print(f"❌ Channel access test failed for {channel_username}: {e}")
            return False


# Global instance
notification_service = NotificationService()
