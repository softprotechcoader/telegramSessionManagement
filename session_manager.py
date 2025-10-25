"""
Session management for Telegram accounts
"""
import asyncio
import os
from typing import List, Dict, Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sessions import StringSession

from config import SESSIONS_DIR, SESSION_TIMEOUT, MAX_RETRIES
from excel_manager import excel_manager
from client_behavior import human_behavior


class SessionManager:
    """Manages Telegram session creation and authentication"""
    
    def __init__(self):
        self.sessions_dir = SESSIONS_DIR
        self.sessions_dir.mkdir(exist_ok=True)
        self.active_sessions = {}
    
    def get_session_path(self, phone_number: str) -> str:
        """Get session file path for a phone number"""
        # Clean phone number for filename
        clean_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        return str(self.sessions_dir / f"session_{clean_phone}.session")
    
    async def create_session(self, account: Dict[str, str]) -> bool:
        """Create a session for a single account"""
        phone_number = account["Mobile_Number"]
        api_id = int(account["API_Key"])
        api_hash = account["Hash_Key"]
        session_path = self.get_session_path(phone_number)
        
        print(f"\n🔐 Creating session for {phone_number}...")
        
        try:
            # Create client
            client = TelegramClient(session_path, api_id, api_hash)
            
            # Add human-like behavior delays
            await human_behavior.pre_action_delay()
            
            # Connect to Telegram
            await client.connect()
            
            if not await client.is_user_authorized():
                print(f"📱 Sending code to {phone_number}...")
                
                # Send code with human-like delay
                await human_behavior.random_delay(1, 3)
                await client.send_code_request(phone_number)
                
                # Get code from user
                code = input(f"📝 Enter verification code for {phone_number}: ").strip()
                
                if not code:
                    print("❌ No code provided, skipping this account")
                    await client.disconnect()
                    return False
                
                try:
                    # Verify code with human-like behavior
                    await human_behavior.random_delay(1, 2)
                    await client.sign_in(phone_number, code)
                    print(f"✅ Successfully authenticated {phone_number}")
                    
                except SessionPasswordNeededError:
                    # Handle 2FA
                    print(f"🔒 2FA enabled for {phone_number}")
                    password = input(f"🔑 Enter 2FA password for {phone_number}: ").strip()
                    
                    if not password:
                        print("❌ No password provided, skipping this account")
                        await client.disconnect()
                        return False
                    
                    await human_behavior.random_delay(1, 2)
                    await client.sign_in(password=password)
                    print(f"✅ Successfully authenticated {phone_number} with 2FA")
                
                except PhoneCodeInvalidError:
                    print(f"❌ Invalid verification code for {phone_number}")
                    await client.disconnect()
                    return False
                
                except Exception as e:
                    print(f"❌ Authentication failed for {phone_number}: {e}")
                    await client.disconnect()
                    return False
            
            else:
                print(f"✅ Session already exists for {phone_number}")
            
            # Test the session
            try:
                me = await client.get_me()
                print(f"👤 Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'no username'})")
                
                # Simulate reading time
                await human_behavior.simulate_reading(50)
                
            except Exception as e:
                print(f"⚠️ Warning: Could not get user info for {phone_number}: {e}")
            
            # Disconnect and store session
            await client.disconnect()
            
            # Add post-action delay
            await human_behavior.post_action_delay()
            
            print(f"✅ Session created successfully: {session_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create session for {phone_number}: {e}")
            return False
    
    async def create_all_sessions(self) -> Dict[str, bool]:
        """Create sessions for all accounts in Excel file"""
        accounts = excel_manager.load_accounts()
        
        if not accounts:
            print("❌ No accounts found in Excel file")
            return {}
        
        print(f"\n🚀 Creating sessions for {len(accounts)} accounts...")
        print("=" * 60)
        
        results = {}
        successful = 0
        
        for i, account in enumerate(accounts, 1):
            phone_number = account["Mobile_Number"]
            print(f"\n[{i}/{len(accounts)}] Processing {phone_number}...")
            
            success = await self.create_session(account)
            results[phone_number] = success
            
            if success:
                successful += 1
            
            # Add delay between accounts to avoid rate limiting
            if i < len(accounts):
                print("⏳ Waiting before next account...")
                await human_behavior.random_delay(3, 8)
        
        print("\n" + "=" * 60)
        print(f"📊 Session creation summary:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {len(accounts) - successful}")
        print(f"📁 Sessions saved in: {self.sessions_dir}")
        
        return results
    
    def get_available_sessions(self) -> List[str]:
        """Get list of available session files"""
        if not self.sessions_dir.exists():
            return []
        
        sessions = []
        for file in self.sessions_dir.glob("session_*.session"):
            # Extract phone number from filename
            phone = file.stem.replace("session_", "")
            # Add + prefix for consistency with Excel data
            if not phone.startswith("+"):
                phone = "+" + phone
            sessions.append(phone)
        
        return sorted(sessions)
    
    async def load_session(self, phone_number: str, api_id: int, api_hash: str) -> Optional[TelegramClient]:
        """Load an existing session with improved error handling"""
        session_path = self.get_session_path(phone_number)
        
        if not os.path.exists(session_path):
            print(f"❌ Session not found for {phone_number}")
            return None
        
        # Check for journal file and clean it up
        journal_path = f"{session_path}-journal"
        if os.path.exists(journal_path):
            print(f"⚠️ Found journal file, cleaning up...")
            try:
                os.remove(journal_path)
                print(f"✅ Journal file removed")
            except Exception as e:
                print(f"⚠️ Could not remove journal file: {e}")
        
        try:
            client = TelegramClient(session_path, api_id, api_hash)
            await client.connect()
            
            if await client.is_user_authorized():
                print(f"✅ Session loaded for {phone_number}")
                return client
            else:
                print(f"❌ Session expired for {phone_number}")
                await client.disconnect()
                return None
                
        except Exception as e:
            print(f"❌ Error loading session for {phone_number}: {e}")
            # Try to clean up corrupted session
            if "database is locked" in str(e).lower():
                print(f"🔧 Attempting to fix locked database...")
                try:
                    # Remove journal file if it exists
                    journal_path = f"{session_path}-journal"
                    if os.path.exists(journal_path):
                        os.remove(journal_path)
                        print(f"✅ Removed journal file")
                    
                    # Try to reconnect after cleanup
                    try:
                        await client.disconnect()
                    except:
                        pass
                    
                    # Wait a moment before retry
                    import asyncio
                    await asyncio.sleep(2)
                    
                    # Retry connection
                    client = TelegramClient(session_path, api_id, api_hash)
                    await client.connect()
                    
                    if await client.is_user_authorized():
                        print(f"✅ Session loaded successfully after cleanup")
                        return client
                    else:
                        print(f"❌ Session still not authorized after cleanup")
                        await client.disconnect()
                        return None
                        
                except Exception as retry_error:
                    print(f"❌ Failed to fix session: {retry_error}")
                    return None
            return None
    
    async def test_session(self, client: TelegramClient) -> bool:
        """Test if a session is working"""
        try:
            me = await client.get_me()
            print(f"✅ Session test successful: {me.first_name} (@{me.username or 'no username'})")
            return True
        except Exception as e:
            print(f"❌ Session test failed: {e}")
            return False
    
    def delete_session(self, phone_number: str) -> bool:
        """Delete a session file"""
        session_path = self.get_session_path(phone_number)
        
        if os.path.exists(session_path):
            try:
                os.remove(session_path)
                print(f"✅ Session deleted for {phone_number}")
                
                # Also remove journal file if it exists
                journal_path = f"{session_path}-journal"
                if os.path.exists(journal_path):
                    try:
                        os.remove(journal_path)
                        print(f"✅ Journal file also removed")
                    except:
                        pass
                        
                return True
            except Exception as e:
                print(f"❌ Error deleting session for {phone_number}: {e}")
                return False
        else:
            print(f"⚠️ Session not found for {phone_number}")
            return False
    
    def cleanup_sessions(self) -> None:
        """Clean up corrupted session files"""
        print("🧹 Cleaning up session files...")
        
        for session_file in self.sessions_dir.glob("session_*.session"):
            journal_path = f"{session_file}-journal"
            if os.path.exists(journal_path):
                try:
                    os.remove(journal_path)
                    print(f"✅ Cleaned journal file for {session_file.name}")
                except Exception as e:
                    print(f"⚠️ Could not clean journal file for {session_file.name}: {e}")
        
        print("✅ Session cleanup completed")
    
    def list_sessions(self) -> None:
        """List all available sessions"""
        sessions = self.get_available_sessions()
        
        if not sessions:
            print("📁 No sessions found")
            return
        
        print(f"\n📁 Available sessions ({len(sessions)}):")
        print("-" * 40)
        for i, phone in enumerate(sessions, 1):
            print(f"{i:2d}. {phone}")
        print("-" * 40)
    
    def find_account_by_phone(self, phone_number: str) -> Optional[Dict[str, str]]:
        """Find account in Excel data by phone number, handling format variations"""
        from excel_manager import excel_manager
        accounts = excel_manager.load_accounts()
        
        if not accounts:
            print(f"❌ No accounts loaded from Excel file")
            return None
        
        # Debug: Print what we're looking for and what's available
        print(f"🔍 Looking for phone: '{phone_number}'")
        print(f"📊 Available phones in Excel: {[acc.get('Mobile_Number', 'No phone') for acc in accounts]}")
        
        # Try exact match first
        for account in accounts:
            if account.get("Mobile_Number") == phone_number:
                print(f"✅ Found exact match: {account['Mobile_Number']}")
                return account
        
        # Try without + prefix
        clean_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        for account in accounts:
            account_phone = account.get("Mobile_Number", "").replace("+", "").replace("-", "").replace(" ", "")
            if account_phone == clean_phone:
                print(f"✅ Found match after cleaning: {account['Mobile_Number']} -> {phone_number}")
                return account
        
        # Try with + prefix if original doesn't have it
        if not phone_number.startswith("+"):
            plus_phone = "+" + phone_number
            for account in accounts:
                if account.get("Mobile_Number") == plus_phone:
                    print(f"✅ Found match with + prefix: {account['Mobile_Number']}")
                    return account
        
        # Try without + prefix if original has it
        if phone_number.startswith("+"):
            no_plus_phone = phone_number[1:]
            for account in accounts:
                if account.get("Mobile_Number") == no_plus_phone:
                    print(f"✅ Found match without + prefix: {account['Mobile_Number']}")
                    return account
        
        print(f"❌ No account found for phone: {phone_number}")
        return None


# Global instance
session_manager = SessionManager()
