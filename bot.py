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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
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
        remaining = max(4 - invite_count, 0)

        if invite_count >= 4:
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
            buttons.append([InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
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

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat.type != 'supergroup':
            for new_member in update.message.new_chat_members:
                try:
                    inviter = update.message.from_user
                    if inviter.id == new_member.id:
                        continue
                    if inviter.id not in self.invite_counts:
                        self.invite_counts[inviter.id] = {
                            'invite_count': 0,
                            'first_name': inviter.first_name,
                            'withdrawal_key': None
                        }
                    # Increment the invite count for the inviter
                    self.invite_counts[inviter.id]['invite_count'] += 1
                    self._update_user_status(inviter.id, update)
                except Exception as e:
                    logger.error(f"Error tracking invite: {e}")
        else:
            logger.warning("This event is not supported in supergroups directly. Use admin logs for tracking.")

    async def _update_user_status(self, user_id: int, update: Update):
        # This method checks if an invite should be counted (e.g., every 2 invites)
        invite_count = self.invite_counts[user_id]['invite_count']
        if invite_count % 2 == 0:  # Only update every 2 invites for simplicity
            first_name = self.invite_counts[user_id]['first_name']
            balance = invite_count * 50
            remaining = max(4 - invite_count, 0)

            if invite_count >= 4:
                message = (
                    f"Congratulations 👏👏🎉\n\n"
                    f"📊 Milestone Achieved: @DIGITAL_BIRRI\n"
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
                    f"📊 Invite Progress: @DIGITAL_BIRRI\n"
                    f"-----------------------\n"
                    f"👤 User: {first_name}\n"
                    f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                    f"💰 Balance: {balance} ETB\n"
                    f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                    f"-----------------------\n\n"
                    f"Add gochuun carraa badhaasaa keessan dabalaa!"
                )
                buttons = [
                    [InlineKeyboardButton("Check", callback_data=f"check_{user_id}")]
                ]

            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    # ... Keep other methods like handle_check, handle_key unchanged ...

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
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
