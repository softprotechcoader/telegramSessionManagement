"""
Main CLI interface for Telegram Automation System
"""
import asyncio
import sys
from typing import List, Optional

from config import SESSIONS_DIR, EXCEL_FILE
from excel_manager import excel_manager
from session_manager import session_manager
from notification_service import notification_service
from post_reader import post_reader
from client_behavior import human_behavior


class TelegramAutomation:
    """Main automation system"""
    
    def __init__(self):
        self.active_clients = []
        self.is_running = True
    
    def display_banner(self):
        """Display welcome banner"""
        print("=" * 60)
        print("🤖 TELEGRAM AUTOMATION SYSTEM")
        print("📱 Powered by Telethon 1.41.0")
        print("=" * 60)
        print("Features:")
        print("• Excel-based account management")
        print("• Automated session creation")
        print("• Channel monitoring with notifications")
        print("• Post reading (newest to oldest)")
        print("• Human-like behavior simulation")
        print("=" * 60)
        
        # Check if Excel file exists and show status
        from config import EXCEL_FILE
        if EXCEL_FILE.exists():
            from excel_manager import excel_manager
            accounts = excel_manager.load_accounts()
            sessions = session_manager.get_available_sessions()
            print(f"\n📊 Current Status:")
            print(f"  📁 Excel accounts: {len(accounts)}")
            print(f"  🔐 Active sessions: {len(sessions)}")
            if len(accounts) > 0 and len(sessions) == 0:
                print(f"  💡 Tip: Use option 3 to create sessions for your accounts")
            print("=" * 60)
    
    def display_menu(self):
        """Display main menu"""
        print("\n📋 MAIN MENU")
        print("-" * 30)
        print("1. 📊 Generate Excel template")
        print("2. 📁 Load Excel and view accounts")
        print("3. 🔐 Generate session files (automated)")
        print("4. 🔔 Start notification service")
        print("5. 📖 Read posts (on-demand)")
        print("6. 👀 Monitor posts (continuous)")
        print("7. 📁 List available sessions")
        print("8. 🧪 Test session")
        print("9. 🗑️ Delete session")
        print("0. 🚪 Exit")
        print("-" * 30)
    
    async def generate_excel_template(self):
        """Generate Excel template"""
        print("\n📊 Generating Excel template...")
        success = excel_manager.generate_template()
        if success:
            print(f"✅ Template created: {EXCEL_FILE}")
            print("📝 Please fill in your account details and save the file.")
        else:
            print("❌ Failed to create template")
    
    async def load_and_view_accounts(self):
        """Load and display accounts from Excel"""
        print("\n📁 Loading accounts from Excel...")
        excel_manager.display_accounts()
    
    async def generate_sessions(self):
        """Generate session files for all accounts"""
        print("\n🔐 Starting automated session creation...")
        print("⚠️ You will need to provide verification codes for each account")
        
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Session creation cancelled")
            return
        
        results = await session_manager.create_all_sessions()
        
        if results:
            successful = sum(1 for success in results.values() if success)
            print(f"\n📊 Session creation completed:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {len(results) - successful}")
        else:
            print("❌ No sessions were created")
    
    async def start_notification_service(self):
        """Start notification service for channel monitoring"""
        print("\n🔔 Starting notification service...")
        
        # Get available sessions
        sessions = session_manager.get_available_sessions()
        if not sessions:
            print("❌ No sessions available. Please create sessions first.")
            return
        
        # Select session
        print(f"\n📁 Available sessions ({len(sessions)}):")
        for i, phone in enumerate(sessions, 1):
            print(f"{i}. {phone}")
        
        try:
            choice = int(input(f"\nSelect session (1-{len(sessions)}): ")) - 1
            if 0 <= choice < len(sessions):
                selected_phone = sessions[choice]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Load session
        account = session_manager.find_account_by_phone(selected_phone)
        
        if not account:
            print(f"❌ Account not found for {selected_phone}")
            return
        
        # Create client
        client = await session_manager.load_session(
            selected_phone, 
            int(account["API_Key"]), 
            account["Hash_Key"]
        )
        
        if not client:
            print("❌ Failed to load session")
            return
        
        # Get channels to monitor
        channels_input = input("\n📺 Enter channel usernames (comma-separated): ").strip()
        if not channels_input:
            print("❌ No channels provided")
            await client.disconnect()
            return
        
        channels = [ch.strip().replace('@', '') for ch in channels_input.split(',')]
        
        # Start monitoring
        try:
            await notification_service.start_monitoring([client], channels)
        finally:
            await client.disconnect()
    
    async def read_posts_on_demand(self):
        """Read posts on-demand"""
        print("\n📖 Reading posts on-demand...")
        
        # Get session and channel
        client, channel = await self._get_client_and_channel()
        if not client or not channel:
            return
        
        try:
            # Get number of posts to read
            try:
                limit = int(input("📊 Number of posts to read (default 10): ") or "10")
            except ValueError:
                limit = 10
            
            # Read posts
            posts = await post_reader.read_posts_on_demand(client, channel, limit)
            
            if posts:
                print(f"\n✅ Successfully read {len(posts)} posts")
            else:
                print("❌ No posts were read")
                
        finally:
            await client.disconnect()
    
    async def monitor_posts_continuous(self):
        """Monitor posts continuously"""
        print("\n👀 Starting continuous post monitoring...")
        
        # Get session and channel
        client, channel = await self._get_client_and_channel()
        if not client or not channel:
            return
        
        try:
            # Get check interval
            try:
                interval = int(input("⏰ Check interval in seconds (default 30): ") or "30")
            except ValueError:
                interval = 30
            
            # Start monitoring
            await post_reader.start_continuous_monitoring(client, channel, interval)
            
        finally:
            await client.disconnect()
    
    async def _get_client_and_channel(self):
        """Get client and channel for operations"""
        # Get available sessions
        sessions = session_manager.get_available_sessions()
        if not sessions:
            print("❌ No sessions available. Please create sessions first.")
            return None, None
        
        # Select session
        print(f"\n📁 Available sessions ({len(sessions)}):")
        for i, phone in enumerate(sessions, 1):
            print(f"{i}. {phone}")
        
        try:
            choice = int(input(f"\nSelect session (1-{len(sessions)}): ")) - 1
            if 0 <= choice < len(sessions):
                selected_phone = sessions[choice]
            else:
                print("❌ Invalid selection")
                return None, None
        except ValueError:
            print("❌ Invalid input")
            return None, None
        
        # Load session
        account = session_manager.find_account_by_phone(selected_phone)
        
        if not account:
            print(f"❌ Account not found for {selected_phone}")
            return None, None
        
        # Create client
        client = await session_manager.load_session(
            selected_phone, 
            int(account["API_Key"]), 
            account["Hash_Key"]
        )
        
        if not client:
            print("❌ Failed to load session")
            return None, None
        
        # Get channel
        channel = input("\n📺 Enter channel username (without @): ").strip()
        if not channel:
            print("❌ No channel provided")
            await client.disconnect()
            return None, None
        
        return client, channel
    
    async def list_sessions(self):
        """List available sessions"""
        print("\n📁 Available Sessions:")
        session_manager.list_sessions()
        
        # Also show which sessions have corresponding accounts
        sessions = session_manager.get_available_sessions()
        if sessions:
            print("\n🔍 Session Status:")
            for phone in sessions:
                account = session_manager.find_account_by_phone(phone)
                status = "✅ Linked to account" if account else "❌ No account found"
                print(f"  {phone}: {status}")
    
    async def test_session(self):
        """Test a session"""
        print("\n🧪 Testing session...")
        
        # Get available sessions
        sessions = session_manager.get_available_sessions()
        if not sessions:
            print("❌ No sessions available")
            return
        
        # Select session
        print(f"\n📁 Available sessions ({len(sessions)}):")
        for i, phone in enumerate(sessions, 1):
            print(f"{i}. {phone}")
        
        try:
            choice = int(input(f"\nSelect session to test (1-{len(sessions)}): ")) - 1
            if 0 <= choice < len(sessions):
                selected_phone = sessions[choice]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Load session
        account = session_manager.find_account_by_phone(selected_phone)
        
        if not account:
            print(f"❌ Account not found for {selected_phone}")
            return
        
        # Test session
        client = await session_manager.load_session(
            selected_phone, 
            int(account["API_Key"]), 
            account["Hash_Key"]
        )
        
        if client:
            try:
                await session_manager.test_session(client)
            finally:
                await client.disconnect()
        else:
            print("❌ Failed to load session")
    
    async def delete_session(self):
        """Delete a session"""
        print("\n🗑️ Delete session...")
        
        # Get available sessions
        sessions = session_manager.get_available_sessions()
        if not sessions:
            print("❌ No sessions available")
            return
        
        # Select session
        print(f"\n📁 Available sessions ({len(sessions)}):")
        for i, phone in enumerate(sessions, 1):
            print(f"{i}. {phone}")
        
        try:
            choice = int(input(f"\nSelect session to delete (1-{len(sessions)}): ")) - 1
            if 0 <= choice < len(sessions):
                selected_phone = sessions[choice]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        # Confirm deletion
        confirm = input(f"⚠️ Delete session for {selected_phone}? (y/N): ").strip().lower()
        if confirm == 'y':
            session_manager.delete_session(selected_phone)
        else:
            print("❌ Deletion cancelled")
    
    async def run(self):
        """Main application loop"""
        self.display_banner()
        
        while self.is_running:
            try:
                self.display_menu()
                choice = input("\n🎯 Select option (0-9): ").strip()
                
                if choice == '1':
                    await self.generate_excel_template()
                elif choice == '2':
                    await self.load_and_view_accounts()
                elif choice == '3':
                    await self.generate_sessions()
                elif choice == '4':
                    await self.start_notification_service()
                elif choice == '5':
                    await self.read_posts_on_demand()
                elif choice == '6':
                    await self.monitor_posts_continuous()
                elif choice == '7':
                    await self.list_sessions()
                elif choice == '8':
                    await self.test_session()
                elif choice == '9':
                    await self.delete_session()
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    self.is_running = False
                else:
                    print("❌ Invalid option. Please try again.")
                
                if self.is_running:
                    input("\n⏸️ Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Application interrupted by user")
                self.is_running = False
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("⏸️ Press Enter to continue...")


async def main():
    """Main entry point"""
    try:
        automation = TelegramAutomation()
        await automation.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
