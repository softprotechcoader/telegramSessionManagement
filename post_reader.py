"""
Post reader for Telegram channels - on-demand and continuous monitoring
"""
import asyncio
from typing import List, Optional, Dict
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, Message

from client_behavior import human_behavior


class PostReader:
    """Reads posts from Telegram channels in newest to oldest order"""
    
    def __init__(self):
        self.is_monitoring = False
    
    async def read_posts_on_demand(self, client: TelegramClient, channel_username: str, 
                                 limit: int = 10) -> List[Dict]:
        """Read posts on-demand from a channel with pagination"""
        try:
            print(f"\n📖 Reading posts from @{channel_username}...")
            
            # Get channel entity
            entity = await client.get_entity(channel_username)
            
            if not isinstance(entity, (Channel, Chat)):
                print(f"❌ {channel_username} is not a channel or chat")
                return []
            
            # Add human-like delay before reading
            await human_behavior.pre_action_delay()
            
            # Start with the latest posts
            last_message_id = 0
            all_posts = []
            batch_count = 0
            
            print(f"🔄 Starting from latest posts...")
            print("=" * 80)
            
            while True:
                batch_count += 1
                print(f"\n📦 Batch {batch_count} - Loading {limit} posts...")
                
                # Get messages starting from the last message ID
                if last_message_id == 0:
                    # First batch - get latest messages
                    messages = await client.get_messages(entity, limit=limit)
                else:
                    # Subsequent batches - get older messages
                    messages = await client.get_messages(entity, limit=limit, max_id=last_message_id)
                
                if not messages:
                    print(f"📭 No more messages found")
                    break
                
                print(f"✅ Found {len(messages)} messages in this batch")
                
                # Process each message in this batch
                batch_posts = []
                for i, message in enumerate(messages, 1):
                    global_index = len(all_posts) + i
                    print(f"\n📄 Processing post {global_index}...")
                    
                    post_data = await self._format_message(message, global_index)
                    batch_posts.append(post_data)
                    all_posts.append(post_data)
                    
                    # Simulate reading time
                    await human_behavior.simulate_reading(len(post_data.get('text', '')))
                    
                    # Show progress
                    if i % 5 == 0 or i == len(messages):
                        print(f"⏳ Processed {i}/{len(messages)} posts in this batch...")
                
                # Update last message ID for next batch
                last_message_id = messages[-1].id
                
                # Ask user if they want to continue
                print(f"\n📊 Total posts read so far: {len(all_posts)}")
                print("=" * 50)
                
                while True:
                    choice = input("\n🔄 Continue reading older posts? (c)ontinue/(e)xit/(s)how more/(f)ile: ").strip().lower()
                    
                    if choice in ['c', 'continue']:
                        print("⏳ Loading next batch...")
                        await human_behavior.random_delay(1, 3)
                        break
                    elif choice in ['e', 'exit']:
                        print("✅ Reading completed!")
                        # Ask if user wants to save to file
                        save_choice = input("💾 Save posts to file? (y/N): ").strip().lower()
                        if save_choice == 'y':
                            await self._save_posts_to_file(all_posts, channel_username)
                        return all_posts
                    elif choice in ['s', 'show']:
                        # Show a summary of what we've read so far
                        print(f"\n📋 Summary of {len(all_posts)} posts read:")
                        for i, post in enumerate(all_posts[-5:], len(all_posts)-4):  # Show last 5
                            print(f"  {i}. [{post['date']}] {post['text'][:50]}...")
                        if len(all_posts) > 5:
                            print(f"  ... and {len(all_posts) - 5} more posts")
                        continue
                    elif choice in ['f', 'file']:
                        # Save current posts to file
                        await self._save_posts_to_file(all_posts, channel_username)
                        continue
                    else:
                        print("❌ Invalid choice. Please enter 'c' (continue), 'e' (exit), 's' (show), or 'f' (file)")
                        continue
                
                # Add delay between batches
                await human_behavior.random_delay(2, 5)
            
            print(f"\n✅ Finished reading all available posts ({len(all_posts)} total)")
            return all_posts
            
        except Exception as e:
            print(f"❌ Error reading posts from @{channel_username}: {e}")
            return []
    
    async def _format_message(self, message: Message, index: int) -> Dict:
        """Format a message for display"""
        # Basic message info
        post_data = {
            'index': index,
            'id': message.id,
            'date': message.date.strftime("%Y-%m-%d %H:%M:%S"),
            'sender_id': message.sender_id,
            'text': message.text or "",
            'media_type': None,
            'views': getattr(message, 'views', None),
            'forwards': getattr(message, 'forwards', None),
            'replies': getattr(message, 'replies', None)
        }
        
        # Media information
        if message.media:
            media_type = type(message.media).__name__
            post_data['media_type'] = media_type
        
        # Display the message
        print(f"\n📄 Message #{index}")
        print(f"🆔 ID: {message.id}")
        print(f"📅 Date: {post_data['date']}")
        print(f"👤 Sender: {message.sender_id}")
        
        if post_data['views']:
            print(f"👀 Views: {post_data['views']}")
        if post_data['forwards']:
            print(f"🔄 Forwards: {post_data['forwards']}")
        if post_data['replies']:
            print(f"💬 Replies: {post_data['replies']}")
        
        if post_data['media_type']:
            print(f"📎 Media: {post_data['media_type']}")
        
        if post_data['text']:
            # Truncate long text for display
            display_text = post_data['text']
            if len(display_text) > 200:
                display_text = display_text[:200] + "..."
            print(f"📝 Text: {display_text}")
        else:
            print("📝 Text: [No text content]")
        
        print("-" * 40)
        
        # Add a small delay between messages for better readability
        await human_behavior.random_delay(0.5, 1.5)
        
        return post_data
    
    async def _save_posts_to_file(self, posts: List[Dict], channel_username: str) -> None:
        """Save posts to a text file"""
        try:
            from datetime import datetime
            import os
            
            # Create posts directory if it doesn't exist
            posts_dir = "posts"
            os.makedirs(posts_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{posts_dir}/posts_{channel_username}_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Posts from @{channel_username}\n")
                f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total posts: {len(posts)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, post in enumerate(posts, 1):
                    f.write(f"Post #{i}\n")
                    f.write(f"ID: {post['id']}\n")
                    f.write(f"Date: {post['date']}\n")
                    f.write(f"Sender: {post['sender_id']}\n")
                    
                    if post['views']:
                        f.write(f"Views: {post['views']}\n")
                    if post['forwards']:
                        f.write(f"Forwards: {post['forwards']}\n")
                    if post['replies']:
                        f.write(f"Replies: {post['replies']}\n")
                    if post['media_type']:
                        f.write(f"Media: {post['media_type']}\n")
                    
                    f.write(f"Text: {post['text']}\n")
                    f.write("-" * 40 + "\n\n")
            
            print(f"💾 Posts saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving posts to file: {e}")
    
    async def start_continuous_monitoring(self, client: TelegramClient, 
                                        channel_username: str, 
                                        check_interval: int = 30) -> None:
        """Start continuous monitoring of a channel for new posts"""
        try:
            print(f"\n🔄 Starting continuous monitoring of @{channel_username}")
            print(f"⏰ Check interval: {check_interval} seconds")
            print("Press Ctrl+C to stop monitoring\n")
            
            # Get initial state
            entity = await client.get_entity(channel_username)
            if not isinstance(entity, (Channel, Chat)):
                print(f"❌ {channel_username} is not a channel or chat")
                return
            
            # Get the latest message ID
            latest_messages = await client.get_messages(entity, limit=1)
            last_message_id = latest_messages[0].id if latest_messages else 0
            
            print(f"📌 Starting from message ID: {last_message_id}")
            print("🔄 Monitoring for new posts...\n")
            
            self.is_monitoring = True
            
            while self.is_monitoring:
                try:
                    # Check for new messages
                    new_messages = await client.get_messages(
                        entity, 
                        limit=10,
                        min_id=last_message_id
                    )
                    
                    if new_messages:
                        # Sort by ID (newest first)
                        new_messages.sort(key=lambda x: x.id, reverse=True)
                        
                        for message in new_messages:
                            if message.id > last_message_id:
                                await self._format_message(message, 0)  # 0 for continuous mode
                                last_message_id = message.id
                                
                                # Simulate reading time
                                await human_behavior.simulate_reading(100)
                        
                        print(f"📌 Updated last message ID: {last_message_id}")
                    
                    # Wait before next check
                    await asyncio.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped by user")
                    break
                except Exception as e:
                    print(f"⚠️ Error during monitoring: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
            
        except Exception as e:
            print(f"❌ Error starting continuous monitoring: {e}")
        finally:
            self.is_monitoring = False
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.is_monitoring = False
        print("🛑 Stopping continuous monitoring...")
    
    async def read_channel_info(self, client: TelegramClient, channel_username: str) -> Optional[Dict]:
        """Get basic information about a channel"""
        try:
            entity = await client.get_entity(channel_username)
            
            if not isinstance(entity, (Channel, Chat)):
                print(f"❌ {channel_username} is not a channel or chat")
                return None
            
            info = {
                'username': channel_username,
                'title': getattr(entity, 'title', 'Unknown'),
                'id': entity.id,
                'type': 'Channel' if isinstance(entity, Channel) else 'Chat',
                'participants_count': getattr(entity, 'participants_count', 'Unknown'),
                'description': getattr(entity, 'about', 'No description')
            }
            
            print(f"\n📺 Channel Information:")
            print(f"📝 Title: {info['title']}")
            print(f"🆔 ID: {info['id']}")
            print(f"📱 Type: {info['type']}")
            print(f"👥 Participants: {info['participants_count']}")
            print(f"📄 Description: {info['description'][:100]}...")
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting channel info for @{channel_username}: {e}")
            return None
    
    async def search_posts(self, client: TelegramClient, channel_username: str, 
                          query: str, limit: int = 10) -> List[Dict]:
        """Search for posts containing specific text"""
        try:
            print(f"\n🔍 Searching for '{query}' in @{channel_username}...")
            
            entity = await client.get_entity(channel_username)
            
            if not isinstance(entity, (Channel, Chat)):
                print(f"❌ {channel_username} is not a channel or chat")
                return []
            
            # Search messages
            messages = await client.get_messages(entity, search=query, limit=limit)
            
            if not messages:
                print(f"🔍 No messages found containing '{query}'")
                return []
            
            print(f"✅ Found {len(messages)} messages containing '{query}'")
            print("=" * 80)
            
            posts = []
            for i, message in enumerate(messages, 1):
                post_data = await self._format_message(message, i)
                posts.append(post_data)
                
                # Simulate reading time
                await human_behavior.simulate_reading(len(post_data.get('text', '')))
            
            return posts
            
        except Exception as e:
            print(f"❌ Error searching posts in @{channel_username}: {e}")
            return []
    
    def get_monitoring_status(self) -> bool:
        """Get current monitoring status"""
        return self.is_monitoring


# Global instance
post_reader = PostReader()
