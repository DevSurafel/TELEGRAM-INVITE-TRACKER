# Telegram Invite Tracker Bot

A Telegram bot built with Python that tracks user invitations and rewards them with virtual ETB (Ethiopian Birr) currency. Users earn 50 ETB per successful invite and can withdraw after reaching 200 invites.

## Features

### Core Functionality
- **Invite Tracking**: Automatically tracks the number of invitations each user makes
- **Unique ID Generation**: Creates unique 8-character alphanumeric codes for each user
- **Reward System**: 
  - 50 ETB per successful invite
  - Minimum 200 invites required for withdrawal
  - Automatic withdrawal key generation upon reaching milestone
- **Progress Monitoring**: Real-time invite progress with interactive buttons
- **Smart Number Processing**: 
  - Accepts user input for invite counts with intelligent validation
  - Randomized calculation algorithms to prevent gaming
  - Ignores numbers greater than 500
  - Tracks maximum numbers to prevent count manipulation

### User Interface
- **Interactive Buttons**:
  - **Check**: View current invite progress
  - **Key🔑**: Get withdrawal key (available after 200 invites)
- **Multilingual Support**: Interface in Oromo language
- **Responsive Messages**: Dynamic typing indicators and processing animations
- **Inline Keyboard**: Easy navigation with callback buttons

### Technical Features
- **Asynchronous Processing**: Built with async/await for optimal performance
- **Nested Event Loop Support**: Uses `nest_asyncio` for compatibility
- **Environment Variables**: Secure token management with `.env` file
- **Error Handling**: Comprehensive logging and error management
- **Data Persistence**: In-memory storage for user data and invite counts
- **Rate Limiting**: Random delays (1-5 seconds) for processing messages

## Project Structure

```
.
├── bot.py                 # Main bot application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker containerization
├── Procfile              # Heroku deployment configuration
├── .env                  # Environment variables (not in repo)
└── README.md             # Project documentation
```

## Prerequisites

- Python 3.9 or higher
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd <repository-name>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**To get your Telegram Bot Token:**
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the token provided
4. Paste it in your `.env` file

## Usage

### Running Locally
```bash
python bot.py
```

### Running with Docker
```bash
# Build the Docker image
docker build -t telegram-invite-bot .

# Run the container
docker run -d --env-file .env telegram-invite-bot
```

### Deploying to Heroku
```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Deploy
git push heroku main
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot and view your invite progress |
| `/send_invite_code <CODE>` | Submit an inviter's code to credit them |

## How It Works

### For New Users
1. Start the bot with `/start`
2. Receive your unique invite code
3. Share your code with friends
4. Track your progress in real-time

### For Invited Users
1. Use `/send_invite_code <INVITER_CODE>` to submit the code
2. The inviter receives 50 ETB credit
3. Start inviting others to earn your own rewards

### Earning Withdrawals
1. Invite 200 people to unlock withdrawal
2. Click "Key🔑" button to receive your 6-digit withdrawal key
3. Use the key to claim your 10,000 ETB reward

## Configuration

### Customizable Values (in `bot.py`)
```python
# Line 46: ETB per invite
balance = invite_count * 50  # Change 50 to desired amount

# Line 48: Minimum invites for withdrawal
remaining = max(200 - invite_count, 0)  # Change 200 to desired threshold

# Line 126: Maximum number limit
if number > 500:  # Change 500 to adjust validation

# Line 165: Random subtraction range
subtract_value = random.randint(100, 150)  # Adjust algorithm parameters
```

## Dependencies

```
flask==latest
python-telegram-bot==20.3
firebase-admin==latest
gunicorn==latest
python-dotenv==latest
pyrogram==latest
tgcrypto==latest
nest_asyncio==latest
```

## Architecture

### Data Structure
```python
invite_counts = {
    user_id: {
        'invite_count': int,      # Number of successful invites
        'first_name': str,        # User's first name
        'withdrawal_key': int,    # 6-digit withdrawal key
        'user_id': int           # Telegram user ID
    }
}

user_unique_ids = {
    user_id: str  # 8-character unique code
}

user_max_numbers = {
    user_id: int  # Largest number posted by user
}
```

## Security Considerations

⚠️ **Important Security Notes:**
1. **Never commit `.env` file** to version control
2. **Rotate bot token** if accidentally exposed
3. **Use environment variables** for all sensitive data
4. **Monitor bot logs** for suspicious activity
5. **Implement rate limiting** in production

### Create `.env.example`
```bash
# Copy this file to .env and fill in your actual values
TELEGRAM_BOT_TOKEN=your_token_here
```

## Troubleshooting

### Bot Not Responding
- Verify bot token is correct in `.env`
- Check if bot is running: `ps aux | grep bot.py`
- Review logs for error messages

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

### Event Loop Issues
- The bot uses `nest_asyncio` to handle nested loops
- If issues persist, restart the bot process

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open-source and available under the MIT License.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub

## Changelog

### Version 1.0.0
- Initial release
- Core invite tracking functionality
- Reward system with ETB currency
- Unique ID generation
- Interactive keyboard buttons
- Multilingual support (Oromo)



## Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Inspired by referral reward systems
- Community feedback and contributions

---

**Made with ❤️ for the Ethiopian Telegram community**
