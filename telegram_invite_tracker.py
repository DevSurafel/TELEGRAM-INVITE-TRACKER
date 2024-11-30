import os
import logging
from typing import Dict
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    filename='invite_tracker.log'
)
logger = logging.getLogger(__name__)

# Dictionary to store invite counts
invite_counts: Dict[int, int] = {}

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for the /start command"""
        await update.message.reply_text(
            "Welcome! I'm an invite tracking bot. "
            "I'll keep track of how many users each person invites to the group."
        )

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Track new members and their inviters"""
        for new_member in update.message.new_chat_members:
            # Try to get the inviter
            try:
                inviter = update.message.from_user
                
                # Ignore bot invites or self-joins
                if inviter.id == new_member.id:
                    continue
                
                # Update invite count
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = 0
                self.invite_counts[inviter.id] += 1
                
                # Log the invite
                logger.info(f"User {inviter.first_name} (ID: {inviter.id}) invited {new_member.first_name}")
                
                # Check for milestone
                if self.invite_counts[inviter.id] % 2 == 0:
                    milestone = self.invite_counts[inviter.id]
                    await update.message.reply_text(
                        f"🎉 Hi {inviter.first_name}, you have invited {milestone} people! Keep it up! 🚀
                      200 ETB Sent to your bank account 🏦
                        "
                    )
            
            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def show_invite_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the current invite count for the user"""
        user = update.effective_user
        invite_count = self.invite_counts.get(user.id, 0)
        await update.message.reply_text(
            f"You have invited {invite_count} people to the group!"
        )

    def run(self):
        """Run the bot"""
        try:
            # Create the Application and pass it your bot's token
            application = Application.builder().token(self.token).build()
            
            # Register handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("invites", self.show_invite_count))
            application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS, 
                self.track_new_member
            ))
            
            # Start the bot
            logger.info("Bot started successfully!")
            application.run_polling(drop_pending_updates=True)
        
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

def main():
    # Get bot token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create and run bot
    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()

# Requirements file (requirements.txt)
# python-telegram-bot==20.7
# 
# Installation Instructions:
# 1. Create a virtual environment:
#    python3 -m venv venv
#    source venv/bin/activate
# 
# 2. Install requirements:
#    pip install -r requirements.txt
# 
# 3. Set your Telegram Bot Token:
#    export TELEGRAM_BOT_TOKEN='your_bot_token_here'
# 
# 4. Run the bot:
#    python telegram_invite_tracker.py
