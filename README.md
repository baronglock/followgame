# Instagram Fight Club - Battle Royale Game

A fun local game where Instagram followers battle in an arena!

## Features

- Fetch real Instagram followers to use as fighters
- Auto-generate fighter stats based on Instagram metrics
- Visual battle arena with health bars and combat animations
- Multiple data import methods for flexibility

## Installation

```bash
pip install -r requirements.txt
```

## Usage Options

### Option 1: Quick Start with Demo Data
```bash
python3 main.py
```

### Option 2: Full Experience with Launcher
```bash
python3 fight_club_launcher.py
```

### Option 3: Manual Import (Recommended for 401 Errors)
```bash
python3 manual_import.py
```

## Dealing with Instagram 401 Errors

Instagram's aggressive anti-bot measures often cause 401 Unauthorized errors. Here are solutions:

### 1. **Use Manual Import Instead**
The safest method - no API calls needed:
- Export your Instagram data from Settings > Privacy > Download Your Information
- Use `manual_import.py` to import the follower list
- Or manually enter usernames

### 2. **Wait and Retry**
If you get 401 errors:
- Wait 24-48 hours before trying again
- Instagram likely flagged your session temporarily
- Use a different network/IP if possible

### 3. **Alternative Authentication Methods**

#### Method A: Session File
1. Login successfully once
2. The session is saved to `session.pkl`
3. Reuse this session for future requests

#### Method B: Browser Session
1. Login to Instagram in your browser
2. Export cookies using a browser extension
3. Use cookies for authentication (requires code modification)

### 4. **Rate Limiting Best Practices**
- Fetch maximum 10-20 followers at a time
- Add 2-4 second delays between requests
- Use cached data when possible
- Don't run the fetcher multiple times in succession

### 5. **Use Public Profiles Only**
- Works without login
- Limited to public accounts
- Still subject to rate limits

## File Structure

```
fight_club_project/
├── main.py                 # Main game engine
├── instagram_fetcher.py    # Instagram API integration
├── manual_import.py        # Manual data import tool
├── fight_club_launcher.py  # Main launcher interface
├── config.json            # Game configuration
├── users.json             # Fighter data
├── profiles/              # Profile pictures
├── cache/                 # Cached API responses
└── requirements.txt       # Python dependencies
```

## Configuration

Edit `config.json` to customize:
- Game settings (screen size, FPS)
- Instagram rate limits
- Fighter stat calculations
- Debug options

## Manual Data Format

### CSV Format
Create a CSV file with columns:
```csv
username,full_name,is_verified,is_private
user1,User One,false,false
user2,User Two,true,false
```

### Text List Format
Simple text file with one username per line:
```
username1
username2
username3
```

## Troubleshooting

### "No module named 'pygame'"
```bash
pip install pygame
```

### "401 Unauthorized" from Instagram
- See "Dealing with Instagram 401 Errors" section above
- Use manual_import.py instead

### "No followers fetched"
- Check if target account is private
- Verify you're following the account (if private)
- Try a public account like "instagram"

### Game crashes on start
- Ensure users.json has at least 2 fighters
- Check that profile images exist or can be generated
- Verify pygame is properly installed

## Privacy & Security Notes

- This tool runs locally only
- No data is sent to external servers
- Instagram credentials are never stored in plain text
- Use at your own risk - respect Instagram's ToS
- Consider using data export instead of API for safety

## Credits

Built with:
- Pygame for game engine
- Instaloader for Instagram integration
- PIL/Pillow for image processing