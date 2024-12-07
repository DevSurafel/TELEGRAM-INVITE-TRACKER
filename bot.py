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
    level=logging.INFO,  # Kept at INFO level as in original script
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # More robust user extraction
            user = update.message.from_user or update.effective_user
            if not user:
                logger.warning("Start command called with no user")
                return

            # Log additional context for debugging
            logger.info(f"Start command in chat: {update.message.chat.id}, Chat Type: {update.message.chat.type}")

            if user.id not in self.invite_counts:
                self.invite_counts[user.id] = {
                    'invite_count': 0,
                    'first_name': user.first_name,
                    'withdrawal_key': None
                }
            invite_count = self.invite_counts[user.id]['invite_count']

            buttons = [
                [InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
                 InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
            ]

            first_name = self.invite_counts[user.id]['first_name']
            balance = invite_count * 50
            remaining = max(200 - invite_count, 0)

            # Rest of the original start method remains the same
            if invite_count >= 200:
                message = (
                    f"Congratulations 👏👏🎉\n\n"
                    f"📊 Milestone Achieved: @Digital_Birri\n"
                    f"-----------------------\n"
                    f"👤 User: {first_name}\n"
                    f"👥 Invites: Nama {invite_count} afeertaniittu! \n"
                    f"💰 Balance: {balance} ETB\n"
                    f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                    f"-----------------------\n\n"
                    f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
                )
                buttons.append([InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
            else:
                message = (
                    f"📊 Invite Progress: @Digital_Birri\n"
                    f"-----------------------\n"
                    f"👤 User: {first_name}\n"
                    f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                    f"💰 Balance: {balance} ETB\n"
                    f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                    f"-----------------------\n\n"
                    f"Add gochuun carraa badhaasaa keessan dabalaa!"
                )

            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))
        
        except Exception as e:
            logger.error(f"Error in start method: {e}", exc_info=True)

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            # Enhanced logging for new member tracking
            logger.info(f"New member event in chat: {update.message.chat.id}")
            logger.info(f"Chat Type: {update.message.chat.type}")

            # More robust new member handling
            for new_member in update.message.new_chat_members:
                # Log each new member details
                logger.info(f"New member: {new_member.id} - {new_member.first_name}")

                inviter = update.message.from_user
                if not inviter or inviter.id == new_member.id:
                    logger.info(f"Skipping self-join or no inviter found for {new_member.first_name}")
                    continue

                # Ensure inviter is tracked
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name,
                        'withdrawal_key': None
                    }

                # Increment invite count
                self.invite_counts[inviter.id]['invite_count'] += 1
                invite_count = self.invite_counts[inviter.id]['invite_count']

                # Rest of the original tracking logic remains the same
                if invite_count % 10 == 0:
                    first_name = self.invite_counts[inviter.id]['first_name']
                    balance = invite_count * 50
                    remaining = max(200 - invite_count, 0)

                    if invite_count >= 200:
                        message = (
                            f"Congratulations 👏👏🎉\n\n"
                            f"📊 Milestone Achieved: @Digital_Birri\n"
                            f"-----------------------\n"
                            f"👤 User: {first_name}\n"
                            f"👥 Invites: Nama {invite_count} afeertaniittu\n"
                            f"💰 Balance: {balance} ETB\n"
                            f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                            f"-----------------------\n\n"
                            f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
                        )
                        buttons = [
                            [InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]
                        ]
                    else:
                        message = (
                            f"📊 Invite Progress: @Digital_Birri\n"
                            f"-----------------------\n"
                            f"👤 User: {first_name}\n"
                            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                            f"💰 Balance: {balance} ETB\n"
                            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                            f"-----------------------\n\n"
                            f"Add gochuun carraa badhaasaa keessan dabalaa!"
                        )
                        buttons = [
                            [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                        ]

                    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

        except Exception as e:
            logger.error(f"Error tracking invite: {e}", exc_info=True)

    # The rest of the methods (handle_check, handle_key, run) remain exactly the same as in your original script

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            # Modified handler to be more inclusive
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.NEW_MEMBERS, 
                self.track_new_member
            ))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

            logger.info("Bot started successfully!")

            # Run the bot asynchronously, using asyncio.run() in a blocking way
            asyncio.get_event_loop().run_until_complete(application.run_polling(drop_pending_updates=True))

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
