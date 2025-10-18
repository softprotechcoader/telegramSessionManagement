"""
Setup script for Telegram Automation System GUI
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "sessions",
        "logs", 
        "posts",
        "assets/icons",
        "build",
        "dist"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_gui():
    """Test if GUI can be imported"""
    print("🧪 Testing GUI imports...")
    try:
        import tkinter
        print("✅ tkinter available")
        
        import telethon
        print("✅ telethon available")
        
        import openpyxl
        print("✅ openpyxl available")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Telegram Automation System - GUI Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test GUI
    if not test_gui():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the GUI: python gui_app.py")
    print("2. Or use the batch file: run_gui.bat")
    print("3. To build executable: python build_exe.py")
    print("4. Or use the batch file: build_exe.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
