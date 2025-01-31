import os
import logging
import random
import re
from typing import Dict
import asyncio
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

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
        self.invite_counts: Dict[int, Dict[str, int]] = {}
        self.user_unique_ids: Dict[int, str] = {}
        self.user_max_numbers: Dict[int, int] = {}  # Track the largest number posted by each user
        self.user_progress_tasks: Dict[int, asyncio.Task] = {}  # Track ongoing progress tasks

    def generate_unique_id(self, user_id: int) -> str:
        if user_id not in self.user_unique_ids:
            unique_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            self.user_unique_ids[user_id] = unique_id
        return self.user_unique_ids[user_id]

    async def send_invite_info(self, update: Update, user: Dict[int, str], unique_id: str):
        invite_count = user['invite_count']
        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user['user_id']}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user['user_id']}")]
        ]

        first_name = user['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        if invite_count >= 200:
            message = (
                f"Congratulations 👏👏🎉\n\n"
                f"📊 Milestone Achieved: @DIGITAL_BIRRI\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: Nama {invite_count} afeertaniittu! \n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                f"-----------------------\n\n"
                f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
            )
            buttons.append([InlineKeyboardButton("👉Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
        else:
            message = (
                f"📊 Invite Progress: @DIGITAL_BIRRI\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                f"-----------------------\n\n"
                f"Add gochuun carraa badhaasaa keessan dabalaa!"
            )
        
        await update.message.reply_text(
            f"{message}\n\nCode'n keessan: {unique_id}", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None,
                'user_id': user.id
            }
        unique_id = self.generate_unique_id(user.id)
        await self.send_invite_info(update, self.invite_counts[user.id], unique_id)

    async def handle_number_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        text = update.message.text

        # Extract numbers from the message
        numbers = re.findall(r'\d+', text)
        if not numbers:
            return  # Ignore messages without numbers

        # Use the first number found
        number = int(numbers[0])

        # Ignore numbers greater than 500
        if number > 500:
            return

        # Track the largest number posted by the user
        if user.id not in self.user_max_numbers or number > self.user_max_numbers[user.id]:
            self.user_max_numbers[user.id] = number

        # Use the largest number posted by the user
        largest_number = self.user_max_numbers[user.id]

        # Randomize the subtraction value (between 100 and 200)
        subtract_value = random.randint(100, 200)
        fake_invite_count = max(largest_number - subtract_value, 0)  # Ensure it's not negative

        # Send a "processing" message
        processing_message = await update.message.reply_text("📊 Calculating your invite progress... Please wait...")

        # Add a random delay (1 to 5 seconds)
        delay = random.randint(1, 5)
        await asyncio.sleep(delay)

        # Delete the "processing" message
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=processing_message.message_id)

        # Simulate gradual progress over time
        if user.id in self.user_progress_tasks:
            self.user_progress_tasks[user.id].cancel()  # Cancel any ongoing progress task

        self.user_progress_tasks[user.id] = asyncio.create_task(
            self.simulate_progress(update, user.id, fake_invite_count)
        )

    async def simulate_progress(self, update: Update, user_id: int, target_invites: int):
        """
        Simulate gradual progress towards the target invite count.
        """
        if user_id not in self.invite_counts:
            self.invite_counts[user_id] = {
                'invite_count': 0,
                'first_name': update.message.from_user.first_name,
                'withdrawal_key': None,
                'user_id': user_id
            }

        current_invites = self.invite_counts[user_id]['invite_count']
        while current_invites < target_invites:
            current_invites += 10  # Increment by 10
            self.invite_counts[user_id]['invite_count'] = current_invites

            # Send updated invite info
            unique_id = self.generate_unique_id(user_id)
            await self.send_invite_info(update, self.invite_counts[user_id], unique_id)

            # Wait for 5 seconds before the next update
            await asyncio.sleep(5)

    # ... (rest of the methods remain the same)

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_number_message))  # Listen for text messages
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_cancel_id, pattern='^cancel_id$'))
            application.add_handler(CommandHandler("send_invite_code", self.handle_send_invite_code))

            logger.info("Bot started successfully!")

            # Return the coroutine for running the bot
            return application.run_polling(drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

# Web server to keep the service running on Render
@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
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
