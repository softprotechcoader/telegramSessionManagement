"""
Main GUI window for Telegram Automation System
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import asyncio
import sys
import os
from pathlib import Path

# Import core modules
from config import EXCEL_FILE
from excel_manager import excel_manager
from session_manager import session_manager
from notification_service import notification_service
from post_reader import post_reader

class TelegramAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.is_monitoring = False
        self.monitoring_thread = None
        self.subscribed_channels = []  # Store fetched channels
        
        # Create main interface
        self.create_widgets()
        self.setup_layout()
        self.load_initial_data()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        
        # Tab 1: Account Management
        self.account_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.account_frame, text="📊 Account Management")
        
        # Tab 2: Session Management
        self.session_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.session_frame, text="🔐 Session Management")
        
        # Tab 3: Channel Monitoring
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="🔔 Channel Monitoring")
        
        # Tab 4: Post Reading
        self.reader_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reader_frame, text="📖 Post Reading")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        
        # Create tab content
        self.create_account_tab()
        self.create_session_tab()
        self.create_monitor_tab()
        self.create_reader_tab()
        
    def create_account_tab(self):
        """Create account management tab"""
        # Excel file section
        excel_frame = ttk.LabelFrame(self.account_frame, text="Excel File Management")
        excel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(excel_frame, text="Generate Excel Template", 
                  command=self.generate_excel_template).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(excel_frame, text="Load Excel File", 
                  command=self.load_excel_file).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(excel_frame, text="Refresh Accounts", 
                  command=self.refresh_accounts).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Accounts list
        accounts_frame = ttk.LabelFrame(self.account_frame, text="Loaded Accounts")
        accounts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for accounts
        columns = ("Phone", "API Key", "Status")
        self.accounts_tree = ttk.Treeview(accounts_frame, columns=columns, show="headings")
        
        for col in columns:
            self.accounts_tree.heading(col, text=col)
            self.accounts_tree.column(col, width=200)
        
        # Scrollbar for accounts
        accounts_scroll = ttk.Scrollbar(accounts_frame, orient=tk.VERTICAL, command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=accounts_scroll.set)
        
        self.accounts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        accounts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_session_tab(self):
        """Create session management tab"""
        # Session controls
        session_controls = ttk.LabelFrame(self.session_frame, text="Session Controls")
        session_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(session_controls, text="Create All Sessions", 
                  command=self.create_all_sessions).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(session_controls, text="Test Selected Session", 
                  command=self.test_selected_session).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(session_controls, text="Delete Selected Session", 
                  command=self.delete_selected_session).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(session_controls, text="Cleanup Sessions", 
                  command=self.cleanup_sessions).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(session_controls, text="Refresh Sessions", 
                  command=self.refresh_sessions).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Sessions list
        sessions_frame = ttk.LabelFrame(self.session_frame, text="Available Sessions")
        sessions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for sessions
        session_columns = ("Phone", "Status", "Account Linked")
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=session_columns, show="headings")
        
        for col in session_columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=200)
        
        # Scrollbar for sessions
        sessions_scroll = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scroll.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_monitor_tab(self):
        """Create channel monitoring tab"""
        # Monitoring mode selection
        mode_frame = ttk.LabelFrame(self.monitor_frame, text="Monitoring Mode")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.monitor_mode = tk.StringVar(value="specific")
        
        specific_radio = ttk.Radiobutton(mode_frame, text="Monitor Specific Channel", 
                                       variable=self.monitor_mode, value="specific",
                                       command=self.on_monitor_mode_change)
        specific_radio.pack(side=tk.LEFT, padx=10, pady=5)
        
        all_radio = ttk.Radiobutton(mode_frame, text="Monitor All Subscribed Channels", 
                                  variable=self.monitor_mode, value="all",
                                  command=self.on_monitor_mode_change)
        all_radio.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Channel input section (for specific channel monitoring)
        self.channel_frame = ttk.LabelFrame(self.monitor_frame, text="Channel Configuration")
        self.channel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.channel_frame, text="Channel Username:").pack(side=tk.LEFT, padx=5)
        self.channel_entry = ttk.Entry(self.channel_frame, width=30)
        self.channel_entry.pack(side=tk.LEFT, padx=5)
        
        # Interval configuration
        interval_frame = ttk.LabelFrame(self.monitor_frame, text="Monitoring Settings")
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interval_frame, text="Check Interval (seconds):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value="30")
        self.interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.pack(side=tk.LEFT, padx=5)
        
        # Channel list display (for all channels mode)
        self.channel_list_frame = ttk.LabelFrame(self.monitor_frame, text="Subscribed Channels")
        self.channel_list_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.fetch_channels_btn = ttk.Button(self.channel_list_frame, text="Fetch Subscribed Channels", 
                                           command=self.fetch_subscribed_channels)
        self.fetch_channels_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.channels_count_label = ttk.Label(self.channel_list_frame, text="No channels loaded")
        self.channels_count_label.pack(side=tk.LEFT, padx=10)
        
        # Hide channel list frame initially
        self.channel_list_frame.pack_forget()
        
        # Session selection
        session_frame = ttk.LabelFrame(self.monitor_frame, text="Session Selection")
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(session_frame, text="Select Session:").pack(side=tk.LEFT, padx=5)
        self.session_var = tk.StringVar()
        self.session_combo = ttk.Combobox(session_frame, textvariable=self.session_var, width=30, state="readonly")
        self.session_combo.pack(side=tk.LEFT, padx=5)
        
        # Monitor controls
        monitor_controls = ttk.LabelFrame(self.monitor_frame, text="Monitor Controls")
        monitor_controls.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_monitor_btn = ttk.Button(monitor_controls, text="Start Monitoring", 
                                          command=self.start_monitoring)
        self.start_monitor_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_monitor_btn = ttk.Button(monitor_controls, text="Stop Monitoring", 
                                         command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_monitor_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Monitor output
        output_frame = ttk.LabelFrame(self.monitor_frame, text="Monitor Output")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.monitor_text = tk.Text(output_frame, height=15, wrap=tk.WORD)
        monitor_scroll = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.monitor_text.yview)
        self.monitor_text.configure(yscrollcommand=monitor_scroll.set)
        
        self.monitor_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        monitor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_reader_tab(self):
        """Create post reading tab"""
        # Reader configuration
        reader_config = ttk.LabelFrame(self.reader_frame, text="Reader Configuration")
        reader_config.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(reader_config, text="Channel Username:").pack(side=tk.LEFT, padx=5)
        self.reader_channel_entry = ttk.Entry(reader_config, width=30)
        self.reader_channel_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(reader_config, text="Posts to Read:").pack(side=tk.LEFT, padx=5)
        self.posts_var = tk.StringVar(value="10")
        self.posts_entry = ttk.Entry(reader_config, textvariable=self.posts_var, width=10)
        self.posts_entry.pack(side=tk.LEFT, padx=5)
        
        # Session selection for reader
        reader_session_frame = ttk.LabelFrame(self.reader_frame, text="Session Selection")
        reader_session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(reader_session_frame, text="Select Session:").pack(side=tk.LEFT, padx=5)
        self.reader_session_var = tk.StringVar()
        self.reader_session_combo = ttk.Combobox(reader_session_frame, textvariable=self.reader_session_var, width=30, state="readonly")
        self.reader_session_combo.pack(side=tk.LEFT, padx=5)
        
        # Reader controls
        reader_controls = ttk.LabelFrame(self.reader_frame, text="Reader Controls")
        reader_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(reader_controls, text="Read Posts", 
                  command=self.read_posts).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(reader_controls, text="Start Continuous Reading", 
                  command=self.start_continuous_reading).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(reader_controls, text="Stop Reading", 
                  command=self.stop_continuous_reading).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reader output
        reader_output_frame = ttk.LabelFrame(self.reader_frame, text="Posts Output")
        reader_output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.reader_text = tk.Text(reader_output_frame, height=15, wrap=tk.WORD)
        reader_scroll = ttk.Scrollbar(reader_output_frame, orient=tk.VERTICAL, command=self.reader_text.yview)
        self.reader_text.configure(yscrollcommand=reader_scroll.set)
        
        self.reader_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reader_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_layout(self):
        """Setup the main layout"""
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def load_initial_data(self):
        """Load initial data into the GUI"""
        self.refresh_accounts()
        self.refresh_sessions()
        self.update_session_combos()
        
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def log_message(self, text_widget, message):
        """Add message to text widget"""
        text_widget.insert(tk.END, f"{message}\n")
        text_widget.see(tk.END)
        self.root.update_idletasks()
        
    # Account Management Methods
    def generate_excel_template(self):
        """Generate Excel template"""
        try:
            self.update_status("Generating Excel template...")
            success = excel_manager.generate_template()
            if success:
                self.log_message(self.monitor_text, "✅ Excel template generated successfully")
                messagebox.showinfo("Success", "Excel template generated successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate Excel template")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating template: {e}")
        finally:
            self.update_status("Ready")
            
    def load_excel_file(self):
        """Load Excel file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if file_path:
                # Update excel manager to use selected file
                from excel_manager import excel_manager
                excel_manager.excel_file = file_path
                self.refresh_accounts()
                messagebox.showinfo("Success", f"Loaded Excel file: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading Excel file: {e}")
            
    def refresh_accounts(self):
        """Refresh accounts list"""
        try:
            # Clear existing items
            for item in self.accounts_tree.get_children():
                self.accounts_tree.delete(item)
                
            # Load accounts
            accounts = excel_manager.load_accounts()
            for account in accounts:
                phone = account.get("Mobile_Number", "")
                api_key = account.get("API_Key", "")
                status = "✅ Valid" if phone and api_key else "❌ Invalid"
                
                self.accounts_tree.insert("", tk.END, values=(phone, api_key, status))
                
            self.update_session_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing accounts: {e}")
            
    def refresh_sessions(self):
        """Refresh sessions list"""
        try:
            # Clear existing items
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
                
            # Load sessions
            sessions = session_manager.get_available_sessions()
            for phone in sessions:
                account = session_manager.find_account_by_phone(phone)
                status = "✅ Active" if account else "❌ No Account"
                linked = "✅ Yes" if account else "❌ No"
                
                self.sessions_tree.insert("", tk.END, values=(phone, status, linked))
                
            self.update_session_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing sessions: {e}")
            
    def update_session_combos(self):
        """Update session combo boxes"""
        try:
            sessions = session_manager.get_available_sessions()
            self.session_combo['values'] = sessions
            self.reader_session_combo['values'] = sessions
            
            if sessions:
                self.session_combo.set(sessions[0])
                self.reader_session_combo.set(sessions[0])
                
        except Exception as e:
            print(f"Error updating session combos: {e}")
    
    # Channel Monitoring Methods
    def on_monitor_mode_change(self):
        """Handle monitoring mode change"""
        mode = self.monitor_mode.get()
        if mode == "specific":
            self.channel_frame.pack(fill=tk.X, padx=10, pady=5)
            self.channel_list_frame.pack_forget()
        else:  # mode == "all"
            self.channel_frame.pack_forget()
            self.channel_list_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def fetch_subscribed_channels(self):
        """Fetch all subscribed channels"""
        session_phone = self.session_var.get()
        if not session_phone:
            messagebox.showwarning("Warning", "Please select a session first")
            return
        
        def fetch_channels():
            try:
                self.update_status("Fetching subscribed channels...")
                self.fetch_channels_btn.config(state=tk.DISABLED)
                
                # Debug: Log the phone number being used
                self.root.after(0, lambda: self.log_message(self.monitor_text, 
                    f"🔍 Looking for account with phone: {session_phone}"))
                
                # Run in async loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get account and create client
                account = session_manager.find_account_by_phone(session_phone)
                if not account:
                    # Try to load all accounts for debugging
                    all_accounts = excel_manager.load_accounts()
                    self.root.after(0, lambda: self.log_message(self.monitor_text, 
                        f"❌ Account not found for {session_phone}"))
                    self.root.after(0, lambda: self.log_message(self.monitor_text, 
                        f"📊 Available accounts in Excel: {[acc.get('Mobile_Number', 'No phone') for acc in all_accounts]}"))
                    
                    # Try alternative phone formats
                    alt_phone_formats = [
                        session_phone,
                        session_phone.replace("+", ""),
                        "+" + session_phone.replace("+", ""),
                        session_phone.replace("-", "").replace(" ", "")
                    ]
                    
                    for alt_phone in alt_phone_formats:
                        account = session_manager.find_account_by_phone(alt_phone)
                        if account:
                            self.root.after(0, lambda p=alt_phone: self.log_message(self.monitor_text, 
                                f"✅ Found account using format: {p}"))
                            break
                    
                    if not account:
                        self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Account not found for {session_phone}. Please check your Excel file contains this phone number."))
                        return
                
                self.root.after(0, lambda: self.log_message(self.monitor_text, 
                    f"✅ Found account: {account['Mobile_Number']} (API: {account['API_Key']})"))
                
                async def get_channels():
                    from telethon import TelegramClient
                    client = TelegramClient(
                        session_manager.get_session_path(session_phone),
                        account['API_Key'],
                        account['Hash_Key']
                    )
                    
                    await client.start()
                    
                    channels = []
                    async for dialog in client.iter_dialogs():
                        if dialog.is_channel and not dialog.is_group:
                            channels.append({
                                'title': dialog.title,
                                'username': dialog.entity.username if dialog.entity.username else f"ID:{dialog.entity.id}",
                                'id': dialog.entity.id
                            })
                    
                    await client.disconnect()
                    return channels
                
                channels = loop.run_until_complete(get_channels())
                self.subscribed_channels = channels
                
                # Update UI in main thread
                self.root.after(0, lambda: self.channels_count_label.config(
                    text=f"Found {len(channels)} subscribed channels"))
                self.root.after(0, lambda: self.log_message(self.monitor_text, 
                    f"✅ Fetched {len(channels)} subscribed channels"))
                
                # Log channel names
                for channel in channels[:10]:  # Show first 10
                    self.root.after(0, lambda ch=channel: self.log_message(self.monitor_text, 
                        f"📺 {ch['title']} (@{ch['username']})"))
                
                if len(channels) > 10:
                    self.root.after(0, lambda: self.log_message(self.monitor_text, 
                        f"... and {len(channels) - 10} more channels"))
                
            except Exception as e:
                error_msg = f"Failed to fetch channels: {e}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.log_message(self.monitor_text, f"❌ Error fetching channels: {e}"))
                import traceback
                self.root.after(0, lambda: self.log_message(self.monitor_text, f"🔍 Traceback: {traceback.format_exc()}"))
            finally:
                self.root.after(0, lambda: self.fetch_channels_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.update_status("Ready"))
        
        # Run in separate thread
        thread = threading.Thread(target=fetch_channels, daemon=True)
        thread.start()
            
    # Session Management Methods
    def create_all_sessions(self):
        """Create all sessions"""
        def run_async():
            try:
                self.update_status("Creating sessions...")
                self.log_message(self.monitor_text, "🔐 Starting session creation...")
                
                # Run async session creation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(session_manager.create_all_sessions())
                loop.close()
                
                successful = sum(1 for success in results.values() if success)
                self.log_message(self.monitor_text, f"✅ Session creation completed: {successful} successful")
                self.refresh_sessions()
                
            except Exception as e:
                self.log_message(self.monitor_text, f"❌ Error creating sessions: {e}")
            finally:
                self.update_status("Ready")
                
        # Run in background thread
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        
    def test_selected_session(self):
        """Test selected session"""
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a session to test")
            return
            
        item = self.sessions_tree.item(selected[0])
        phone = item['values'][0]
        
        def run_async():
            try:
                self.update_status(f"Testing session for {phone}...")
                self.log_message(self.monitor_text, f"🧪 Testing session for {phone}...")
                
                # Find account
                account = session_manager.find_account_by_phone(phone)
                if not account:
                    self.log_message(self.monitor_text, f"❌ No account found for {phone}")
                    return
                    
                # Test session
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                client = loop.run_until_complete(session_manager.load_session(
                    phone, int(account["API_Key"]), account["Hash_Key"]
                ))
                
                if client:
                    test_result = loop.run_until_complete(session_manager.test_session(client))
                    if test_result:
                        self.log_message(self.monitor_text, f"✅ Session test successful for {phone}")
                    else:
                        self.log_message(self.monitor_text, f"❌ Session test failed for {phone}")
                    loop.run_until_complete(client.disconnect())
                    loop.close()
                else:
                    self.log_message(self.monitor_text, f"❌ Failed to load session for {phone}")
                    
            except Exception as e:
                self.log_message(self.monitor_text, f"❌ Error testing session: {e}")
            finally:
                self.update_status("Ready")
                
        # Run in background thread
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        
    def delete_selected_session(self):
        """Delete selected session"""
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a session to delete")
            return
            
        item = self.sessions_tree.item(selected[0])
        phone = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete session for {phone}?"):
            try:
                success = session_manager.delete_session(phone)
                if success:
                    self.log_message(self.monitor_text, f"✅ Session deleted for {phone}")
                    self.refresh_sessions()
                else:
                    self.log_message(self.monitor_text, f"❌ Failed to delete session for {phone}")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting session: {e}")
                
    # Monitoring Methods
    def start_monitoring(self):
        """Start channel monitoring"""
        mode = self.monitor_mode.get()
        
        # Get session
        session_phone = self.session_var.get()
        if not session_phone:
            messagebox.showwarning("Warning", "Please select a session")
            return
        
        # Validate based on mode
        if mode == "specific":
            channel = self.channel_entry.get().strip()
            if not channel:
                messagebox.showwarning("Warning", "Please enter a channel username")
                return
            channels_to_monitor = [channel]
        else:  # mode == "all"
            if not hasattr(self, 'subscribed_channels') or not self.subscribed_channels:
                messagebox.showwarning("Warning", "Please fetch subscribed channels first")
                return
            channels_to_monitor = [ch['username'] for ch in self.subscribed_channels if ch['username'] != f"ID:{ch['id']}"]
            if not channels_to_monitor:
                messagebox.showwarning("Warning", "No channels with usernames found. Most channels need usernames to be monitored.")
                return
            
        try:
            interval = int(self.interval_var.get())
        except ValueError:
            interval = 30
            
        def run_monitoring():
            try:
                self.is_monitoring = True
                self.start_monitor_btn.config(state=tk.DISABLED)
                self.stop_monitor_btn.config(state=tk.NORMAL)
                
                if mode == "specific":
                    self.update_status(f"Monitoring {channels_to_monitor[0]}...")
                    self.log_message(self.monitor_text, f"🔔 Starting monitoring for @{channels_to_monitor[0]}")
                else:
                    self.update_status(f"Monitoring {len(channels_to_monitor)} channels...")
                    self.log_message(self.monitor_text, f"🔔 Starting monitoring for {len(channels_to_monitor)} channels:")
                    for ch in channels_to_monitor[:5]:  # Show first 5
                        self.log_message(self.monitor_text, f"  📺 @{ch}")
                    if len(channels_to_monitor) > 5:
                        self.log_message(self.monitor_text, f"  ... and {len(channels_to_monitor) - 5} more")
                
                # Run monitoring in async loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get account and create client
                account = session_manager.find_account_by_phone(session_phone)
                if not account:
                    self.log_message(self.monitor_text, f"❌ No account found for {session_phone}")
                    return
                    
                client = loop.run_until_complete(session_manager.load_session(
                    session_phone, int(account["API_Key"]), account["Hash_Key"]
                ))
                
                if not client:
                    self.log_message(self.monitor_text, f"❌ Failed to load session for {session_phone}")
                    return
                
                # Start monitoring with interval checking
                async def monitor_channels():
                    try:
                        while self.is_monitoring:
                            for channel in channels_to_monitor:
                                if not self.is_monitoring:
                                    break
                                try:
                                    # Get recent messages from channel
                                    entity = await client.get_entity(channel)
                                    messages = await client.get_messages(entity, limit=5)
                                    
                                    for message in messages:
                                        if message.text and message.date:
                                            # Log new message (you can add timestamp checking here)
                                            self.log_message(self.monitor_text, 
                                                f"� New from @{channel}: {message.text[:100]}{'...' if len(message.text) > 100 else ''}")
                                    
                                except Exception as e:
                                    self.log_message(self.monitor_text, f"⚠️ Error monitoring @{channel}: {e}")
                            
                            # Wait for the specified interval
                            await asyncio.sleep(interval)
                    except Exception as e:
                        self.log_message(self.monitor_text, f"❌ Monitoring error: {e}")
                    finally:
                        await client.disconnect()
                
                # Start monitoring
                loop.run_until_complete(monitor_channels())
                
            except Exception as e:
                self.log_message(self.monitor_text, f"❌ Monitoring error: {e}")
            finally:
                self.is_monitoring = False
                self.start_monitor_btn.config(state=tk.NORMAL)
                self.stop_monitor_btn.config(state=tk.DISABLED)
                self.update_status("Ready")
                
        # Run in background thread
        self.monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop channel monitoring"""
        self.is_monitoring = False
        self.log_message(self.monitor_text, "🛑 Stopping monitoring...")
        
    # Reading Methods
    def read_posts(self):
        """Read posts on-demand"""
        channel = self.reader_channel_entry.get().strip()
        if not channel:
            messagebox.showwarning("Warning", "Please enter a channel username")
            return
            
        session_phone = self.reader_session_var.get()
        if not session_phone:
            messagebox.showwarning("Warning", "Please select a session")
            return
            
        try:
            limit = int(self.posts_var.get())
        except ValueError:
            limit = 10
            
        def run_reading():
            try:
                self.update_status(f"Reading posts from @{channel}...")
                self.log_message(self.reader_text, f"📖 Reading {limit} posts from @{channel}...")

                def dual_log(msg):
                    self.log_message(self.reader_text, msg)
                    self.log_message(self.monitor_text, msg)

                # Run reading in async loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Get account and create client
                account = session_manager.find_account_by_phone(session_phone)
                if not account:
                    self.log_message(self.reader_text, f"❌ No account found for {session_phone}")
                    self.log_message(self.monitor_text, f"❌ No account found for {session_phone}")
                    return
                client = loop.run_until_complete(session_manager.load_session(
                    session_phone, int(account["API_Key"]), account["Hash_Key"]
                ))
                if not client:
                    self.log_message(self.reader_text, f"❌ Failed to load session for {session_phone}")
                    self.log_message(self.monitor_text, f"❌ Failed to load session for {session_phone}")
                    return
                # Read posts
                posts = loop.run_until_complete(post_reader.read_posts_on_demand(client, channel, limit, log_func=dual_log))
                loop.run_until_complete(client.disconnect())
                loop.close()
                if posts:
                    self.log_message(self.reader_text, f"✅ Successfully read {len(posts)} posts")
                    self.log_message(self.monitor_text, f"✅ Successfully read {len(posts)} posts")
                else:
                    self.log_message(self.reader_text, "❌ No posts were read")
                    self.log_message(self.monitor_text, "❌ No posts were read")
            except Exception as e:
                self.log_message(self.reader_text, f"❌ Error reading posts: {e}")
                self.log_message(self.monitor_text, f"❌ Error reading posts: {e}")
            finally:
                self.update_status("Ready")
                
        # Run in background thread
        thread = threading.Thread(target=run_reading, daemon=True)
        thread.start()
        
    def start_continuous_reading(self):
        """Start continuous post reading"""
        channel = self.reader_channel_entry.get().strip()
        if not channel:
            messagebox.showwarning("Warning", "Please enter a channel username")
            return
            
        session_phone = self.reader_session_var.get()
        if not session_phone:
            messagebox.showwarning("Warning", "Please select a session")
            return
            
        def run_continuous_reading():
            try:
                self.update_status(f"Continuous reading from @{channel}...")
                self.log_message(self.reader_text, f"🔄 Starting continuous reading from @{channel}...")
                
                # Run continuous reading in async loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get account and create client
                account = session_manager.find_account_by_phone(session_phone)
                if not account:
                    self.log_message(self.reader_text, f"❌ No account found for {session_phone}")
                    return
                    
                client = loop.run_until_complete(session_manager.load_session(
                    session_phone, int(account["API_Key"]), account["Hash_Key"]
                ))
                
                if not client:
                    self.log_message(self.reader_text, f"❌ Failed to load session for {session_phone}")
                    return
                    
                # Start continuous reading
                loop.run_until_complete(post_reader.start_continuous_monitoring(client, channel, 30))
                
            except Exception as e:
                self.log_message(self.reader_text, f"❌ Error in continuous reading: {e}")
            finally:
                self.update_status("Ready")
                
        # Run in background thread
        thread = threading.Thread(target=run_continuous_reading, daemon=True)
        thread.start()
        
    def stop_continuous_reading(self):
        """Stop continuous post reading"""
        self.log_message(self.reader_text, "🛑 Stopping continuous reading...")
        # Implementation would depend on how to stop the continuous reading
    
    def cleanup_sessions(self):
        """Clean up corrupted session files"""
        try:
            self.update_status("Cleaning up sessions...")
            self.log_message(self.monitor_text, "🧹 Cleaning up session files...")
            
            # Run cleanup in background thread
            def run_cleanup():
                try:
                    session_manager.cleanup_sessions()
                    self.log_message(self.monitor_text, "✅ Session cleanup completed")
                except Exception as e:
                    self.log_message(self.monitor_text, f"❌ Cleanup error: {e}")
                finally:
                    self.update_status("Ready")
                    self.refresh_sessions()
            
            thread = threading.Thread(target=run_cleanup, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during cleanup: {e}")
            self.update_status("Ready")
