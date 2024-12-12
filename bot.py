import os
import logging
import random
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Initialize Flask app
app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.group_id = None  # Initialize group_id to None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # Only process the start command
        logger.info("Bot started and ready to receive messages.")
        await update.message.reply_text("Welcome to the group! 🎉")

    async def listen_for_group_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # Check if the message is from a group
        if update.message.chat.type in ['group', 'supergroup']:
            # If we haven't already logged the group ID, log it now
            if self.group_id is None:
                self.group_id = update.message.chat.id
                logger.info(f"Group ID fetched: {self.group_id}")

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            # Add handlers for commands and messages
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.listen_for_group_messages))

            logger.info("Bot started successfully!")
            
            # Run the bot asynchronously
            asyncio.get_event_loop().run_until_complete(application.run_polling(drop_pending_updates=True))

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

# Web server to keep the service running on Render
@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Get the bot token from environment variables
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)

    # Run the bot and the Flask app in the same event loop
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())  # Start the bot as a background task

    # Start the Flask app (it will run in the main thread)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
