# Telegram Automation System

A comprehensive Telegram automation system built with Telethon 1.41.0 that provides Excel-based account management, automated session creation, channel monitoring, and post reading capabilities with human-like behavior simulation.

## Features

- 📊 **Excel-based Account Management**: Generate and load account credentials from Excel files
- 🔐 **Automated Session Creation**: Create Telegram sessions for multiple accounts automatically
- 🔔 **Channel Monitoring**: Real-time notifications for new posts in monitored channels
- 📖 **Post Reading**: Read posts from newest to oldest (on-demand and continuous)
- 🤖 **Human-like Behavior**: Random delays, typing simulation, rate limiting, and anti-flood measures
- 🛡️ **Error Resilience**: Comprehensive error handling and retry logic
- 📱 **Real Client Behavior**: Simulates authentic Telegram client behavior

## Installation

### **Option 1: Console Application**
1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the console application**:
   ```bash
   python main.py
   ```

### **Option 2: Windows GUI Application**
1. **Run the setup script**:
   ```bash
   python setup_gui.py
   ```
2. **Launch the GUI application**:
   ```bash
   python gui_app.py
   ```
   Or double-click `run_gui.bat`

### **Option 3: Standalone Executable**
1. **Build the executable**:
   ```bash
   python build_exe.py
   ```
2. **Run the standalone executable**:
   - Navigate to `dist/` folder
   - Double-click `TelegramAutomation.exe`
   - No Python installation required!

## Quick Start

### 1. Generate Excel Template
- Select option `1` from the main menu
- This creates `telegram_accounts.xlsx` with the required headers
- Fill in your account details (Mobile_Number, API_Key, Hash_Key)

### 2. Create Sessions
- Select option `3` to generate session files
- You'll need to provide verification codes for each account
- Sessions are saved in the `sessions/` directory

### 3. Monitor Channels
- Select option `4` to start notification service
- Enter channel usernames (comma-separated)
- Get real-time notifications for new posts

### 4. Read Posts
- Select option `5` for on-demand reading
- Select option `6` for continuous monitoring
- Choose number of posts and channels to monitor

## Excel File Format

The system uses an Excel file with the following headers:

| Mobile_Number | API_Key | Hash_Key |
|---------------|---------|----------|
| +1234567890   | 12345   | abc123... |
| +0987654321   | 67890   | def456... |

- **Mobile_Number**: Your phone number with country code (e.g., +1234567890)
- **API_Key**: Your Telegram API ID (numeric)
- **Hash_Key**: Your Telegram API Hash (string)

## Getting Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy the API ID and API Hash

## Usage Examples

### Monitor Multiple Channels
```
📺 Enter channel usernames (comma-separated): channel1, channel2, channel3
```

### Read Recent Posts
```
📊 Number of posts to read: 20
📺 Enter channel username: mychannel
```

### Continuous Monitoring
```
⏰ Check interval in seconds: 30
📺 Enter channel username: mychannel
```

## Human-like Behavior Features

- **Random Delays**: 1-5 seconds between actions
- **Typing Simulation**: Realistic typing patterns with pauses
- **Rate Limiting**: Respects Telegram's API limits
- **Reading Simulation**: Time spent "reading" messages
- **Anti-Flood Measures**: Handles flood wait errors gracefully
- **Online Patterns**: Simulates realistic user behavior

## File Structure

```
/
├── main.py                    # Main CLI interface
├── config.py                  # Configuration and constants
├── excel_manager.py           # Excel file operations
├── session_manager.py         # Session creation and management
├── notification_service.py    # Channel monitoring
├── post_reader.py            # Post reading functionality
├── client_behavior.py        # Human-like behavior simulation
├── requirements.txt          # Dependencies
├── sessions/                 # Session files directory
├── logs/                     # Log files directory
└── README.md                 # This file
```

## Configuration

Key settings in `config.py`:

- **Delays**: Adjust timing between actions
- **Rate Limits**: Control API request frequency
- **Session Timeout**: Session connection timeout
- **Notification Interval**: Channel check frequency

## Troubleshooting

### Common Issues

1. **"No sessions available"**
   - Run option 3 to create sessions first
   - Ensure Excel file is properly filled

2. **"Channel access test failed"**
   - Check channel username (without @)
   - Ensure you have access to the channel
   - Verify session is working

3. **"Flood wait error"**
   - The system handles this automatically
   - Wait for the specified time before retrying

4. **"Invalid verification code"**
   - Check the code sent to your phone
   - Ensure you're entering the correct code

### Session Management

- **List Sessions**: Option 7 shows all available sessions
- **Test Session**: Option 8 verifies a session is working
- **Delete Session**: Option 9 removes a session file

## Security Notes

- Session files contain authentication data - keep them secure
- Don't share your API credentials
- Use the system responsibly and respect Telegram's terms of service
- The system includes rate limiting to prevent abuse

## Requirements

- Python 3.7+
- Telethon 1.41.0
- openpyxl for Excel operations
- Internet connection for Telegram API

## License

This project is for educational and personal use only. Please respect Telegram's terms of service and use responsibly.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your API credentials
3. Ensure all dependencies are installed
4. Check that channels are accessible

---

**⚠️ Important**: This system is designed to behave like a real Telegram client. Use it responsibly and in accordance with Telegram's terms of service.
