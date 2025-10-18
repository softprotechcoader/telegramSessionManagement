"""
Telegram Automation System - Windows GUI Application
Main entry point for the standalone Windows application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
import asyncio
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from gui.main_window import TelegramAutomationGUI

class AsyncTkinterApp:
    """Wrapper to handle async operations in tkinter"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.loop = None
        self.thread = None
        
    def run_async(self, coro):
        """Run async coroutine in background thread"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = loop
            loop.run_until_complete(coro)
            
        self.thread = threading.Thread(target=run_in_thread, daemon=True)
        self.thread.start()
    
    def run(self):
        """Start the GUI application"""
        try:
            # Create main window
            app = TelegramAutomationGUI(self.root)
            
            # Center window on screen
            self.root.update_idletasks()
            width = 1000
            height = 700
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Set window properties
            self.root.title("Telegram Automation System v1.0")
            self.root.resizable(True, True)
            
            # Set minimum size
            self.root.minsize(800, 600)
            
            # Try to set icon
            try:
                icon_path = current_dir / "assets" / "icons" / "telegram.ico"
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except:
                pass
            
            # Start GUI
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application: {e}")
            sys.exit(1)

def main():
    """Main entry point for GUI application"""
    try:
        app = AsyncTkinterApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
