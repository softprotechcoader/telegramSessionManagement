"""
Build script for creating standalone Windows executable
"""
import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    try:
        print("🔨 Building standalone Windows executable...")
        
        # PyInstaller command
        cmd = [
            "pyinstaller",
            "--onefile",                    # Create single executable file
            "--windowed",                   # No console window
            "--name=TelegramAutomation",    # Executable name
            "--icon=assets/icons/telegram.ico",  # Icon file (if exists)
            "--add-data=assets;assets",     # Include assets folder
            "--hidden-import=telethon",
            "--hidden-import=openpyxl",
            "--hidden-import=asyncio",
            "--hidden-import=tkinter",
            "--hidden-import=tkinter.ttk",
            "--hidden-import=tkinter.messagebox",
            "--hidden-import=tkinter.filedialog",
            "--hidden-import=tkinter.simpledialog",
            "--clean",                      # Clean cache
            "gui_app.py"                    # Main GUI file
        ]
        
        # Remove icon parameter if icon file doesn't exist
        if not Path("assets/icons/telegram.ico").exists():
            cmd = [arg for arg in cmd if not arg.startswith("--icon")]
            print("⚠️ Icon file not found, building without custom icon")
        
        print(f"Running: {' '.join(cmd)}")
        
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print("📁 Executable created in: dist/TelegramAutomation.exe")
            print("📦 You can now distribute the executable file")
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
        
    return True

def create_installer():
    """Create Windows installer using NSIS (optional)"""
    print("\n📦 Creating installer...")
    print("Note: This requires NSIS to be installed")
    print("You can manually create an installer or use the executable directly")

def main():
    """Main build function"""
    print("🚀 Telegram Automation System - Windows Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("gui_app.py").exists():
        print("❌ gui_app.py not found. Please run from the project root directory.")
        return
        
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/TelegramAutomation.exe")
        print("2. Copy the executable to any Windows machine")
        print("3. The executable is completely standalone")
        
        # Create installer if requested
        create_installer()
    else:
        print("\n❌ Build failed. Please check the errors above.")

if __name__ == "__main__":
    main()
