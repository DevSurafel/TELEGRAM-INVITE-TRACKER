import os
import logging
import random
from typing import Dict
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Initialize Flask app
app = Flask(__name__)

# Enhanced logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
    filename='bot_log.txt',  # Log to a file for persistent tracking
    filemode='a'  # Append mode to keep historical logs
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}
        # Persistent storage for invite counts (optional enhancement)
        self.load_invite_counts()

    def load_invite_counts(self):
        # Optional method to load invite counts from a persistent storage
        # You can implement file-based or database-based storage
        pass

    def save_invite_counts(self):
        # Optional method to save invite counts to persistent storage
        pass

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # Enhanced error handling and logging
            user = update.effective_user
            if not user:
                logger.warning("Start command called with no user")
                return

            # Log user details for debugging
            logger.info(f"Start command called by user: {user.id} - {user.first_name}")

            # Rest of your existing start method logic...
            if user.id not in self.invite_counts:
                self.invite_counts[user.id] = {
                    'invite_count': 0,
                    'first_name': user.first_name,
                    'withdrawal_key': None
                }
                self.save_invite_counts()  # Save after initial creation

            # ... (rest of your existing start method remains the same)

        except Exception as e:
            logger.error(f"Error in start method: {e}", exc_info=True)

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # More comprehensive logging and error handling
            chat = update.effective_chat
            if not chat:
                logger.warning("New member event in undefined chat")
                return

            # Log detailed information about the chat and new members
            logger.info(f"New member event in chat: {chat.id}")
            logger.info(f"Chat title: {chat.title}")
            logger.info(f"Chat type: {chat.type}")

            for new_member in update.message.new_chat_members:
                # Log each new member
                logger.info(f"New member joined: {new_member.id} - {new_member.first_name}")

                # Existing invite tracking logic
                inviter = update.message.from_user
                if inviter.id == new_member.id:
                    continue

                # Enhanced tracking with more robust error handling
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name,
                        'withdrawal_key': None
                    }

                self.invite_counts[inviter.id]['invite_count'] += 1
                self.save_invite_counts()  # Save after each invite

                # Rest of your existing tracking logic...
                invite_count = self.invite_counts[inviter.id]['invite_count']

                # Existing message and button logic...

        except Exception as e:
            logger.error(f"Comprehensive error in track_new_member: {e}", exc_info=True)

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            query = update.callback_query
            if not query:
                logger.warning("Check callback with no query")
                return

            user_id = int(query.data.split('_')[1])
            logger.info(f"Check invoked for user: {user_id}")

            # Rest of your existing handle_check method...

        except Exception as e:
            logger.error(f"Error in handle_check: {e}", exc_info=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            query = update.callback_query
            if not query:
                logger.warning("Key callback with no query")
                return

            user_id = int(query.data.split('_')[1])
            logger.info(f"Key requested for user: {user_id}")

            # Rest of your existing handle_key method...

        except Exception as e:
            logger.error(f"Error in handle_key: {e}", exc_info=True)

    def run(self):
        try:
            # More robust application setup
            application = Application.builder().token(self.token).build()

            # Add multiple handlers with more comprehensive filters
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.NEW_MEMBERS, 
                self.track_new_member
            ))
            application.add_handler(CallbackQueryHandler(
                self.handle_check, 
                pattern=r'^check_\d+$'
            ))
            application.add_handler(CallbackQueryHandler(
                self.handle_key, 
                pattern=r'^key_\d+$'
            ))

            logger.info("Bot configuration completed. Starting polling...")

            # Run the bot with enhanced error handling
            asyncio.get_event_loop().run_until_complete(
                application.run_polling(
                    drop_pending_updates=True, 
                    timeout=30,  # Increased timeout
                    read_timeout=30,
                    connect_timeout=30
                )
            )

        except Exception as e:
            logger.error(f"Critical failure in bot run: {e}", exc_info=True)

# Web server route
@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.critical("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)

    # Improved event loop handling
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(bot.run())

        # Start the Flask app
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)

if __name__ == "__main__":
    main()
