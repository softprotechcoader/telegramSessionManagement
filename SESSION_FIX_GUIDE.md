# Session Fix Guide

## Problem: "Failed to load session for +919587763441"

### Root Cause
The "database is locked" error occurs when:
1. **Journal files exist**: Session files have associated journal files (`session_*.session-journal`)
2. **Improper session closure**: Previous sessions weren't properly disconnected
3. **Multiple processes**: Multiple applications trying to access the same session

### Solution Implemented

#### 1. **Enhanced Session Loading** (`session_manager.py`)
- **Automatic journal cleanup**: Detects and removes journal files before loading
- **Retry mechanism**: Attempts to fix locked databases automatically
- **Better error handling**: Specific handling for database lock errors
- **Session validation**: Ensures sessions are properly authorized

#### 2. **Session Cleanup Tools**
- **Console cleanup**: Option 10 in main menu - "Cleanup sessions"
- **GUI cleanup**: "Cleanup Sessions" button in Session Management tab
- **Standalone fix script**: `fix_sessions.py` for manual cleanup

#### 3. **Improved Session Management**
- **Proper disconnection**: Ensures clients are properly disconnected
- **Journal file removal**: Automatically removes journal files during deletion
- **Session validation**: Tests sessions before use

## How to Fix Session Issues

### Method 1: Using the Application
1. **Console App**: Run `python main.py` → Select option 10 → "Cleanup sessions"
2. **GUI App**: Run `python gui_app.py` → Session Management tab → "Cleanup Sessions"

### Method 2: Using Fix Script
```bash
python fix_sessions.py
```

### Method 3: Manual Fix
1. Stop all Python processes: `taskkill /F /IM python.exe`
2. Delete journal files: `del "sessions\session_*.session-journal"`
3. Restart the application

## Prevention Measures

### 1. **Proper Session Closure**
- Always disconnect clients properly
- Use try/finally blocks for session management
- Handle exceptions gracefully

### 2. **Single Process Access**
- Don't run multiple instances simultaneously
- Use session locks if needed
- Monitor active sessions

### 3. **Regular Cleanup**
- Run cleanup periodically
- Monitor for journal files
- Check session health

## Technical Details

### Journal Files
- **Purpose**: SQLite transaction logs
- **Problem**: Left behind when sessions aren't properly closed
- **Solution**: Automatic detection and removal

### Database Lock
- **Cause**: Multiple processes accessing same session
- **Detection**: "database is locked" error message
- **Fix**: Cleanup + retry mechanism

### Session Validation
- **Check**: `client.is_user_authorized()`
- **Test**: `client.get_me()` for basic functionality
- **Cleanup**: Remove invalid sessions

## Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `database is locked` | Journal file exists | Run cleanup |
| `Session not found` | File doesn't exist | Create new session |
| `Session expired` | Authentication failed | Re-authenticate |
| `Failed to load session` | General error | Check logs, run cleanup |

## Best Practices

### 1. **Session Management**
```python
# Good practice
try:
    client = await session_manager.load_session(phone, api_id, api_hash)
    if client:
        # Use session
        await client.disconnect()  # Always disconnect
except Exception as e:
    print(f"Error: {e}")
    # Handle error
```

### 2. **Regular Maintenance**
- Run cleanup weekly
- Monitor session health
- Check for journal files
- Validate session functionality

### 3. **Error Handling**
- Always use try/catch blocks
- Implement retry mechanisms
- Log errors for debugging
- Provide user feedback

## Troubleshooting

### Quick Fix Checklist
1. ✅ Stop all Python processes
2. ✅ Run session cleanup
3. ✅ Check for journal files
4. ✅ Test session loading
5. ✅ Verify session functionality

### Common Issues
- **Multiple instances**: Kill all Python processes
- **Corrupted sessions**: Delete and recreate
- **Permission errors**: Run as administrator
- **Network issues**: Check internet connection

## Files Modified

1. **`session_manager.py`**: Enhanced session loading with cleanup
2. **`main.py`**: Added cleanup option (option 10)
3. **`gui/main_window.py`**: Added cleanup button
4. **`fix_sessions.py`**: Standalone cleanup script
5. **`.gitignore`**: Added fix script to ignore list

The session loading issue has been resolved with comprehensive error handling and automatic cleanup mechanisms.
