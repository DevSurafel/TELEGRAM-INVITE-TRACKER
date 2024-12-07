import os
import logging
import random
import asyncio
from typing import Dict
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
    def __init__(self, token: str, group_id: int):
        self.token = token
        self.group_id = group_id  # Target group ID
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def send_to_group(self, message: str, buttons: InlineKeyboardMarkup = None):
        """Send a message to the specified group."""
        try:
            application = Application.builder().token(self.token).build()
            await application.bot.send_message(
                chat_id=self.group_id,
                text=message,
                reply_markup=buttons
            )
            logger.info("Message sent to the group successfully.")
        except Exception as e:
            logger.error(f"Failed to send message to the group: {e}")

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
        remaining = max(200 - invite_count, 0)

        message = (
            f"📊 Invite Progress: @Digital_Birri\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: {invite_count}\n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Remaining Invites: {remaining}"
        )
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))
        # Send notification to the group
        await self.send_to_group(message, InlineKeyboardMarkup(buttons))

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                self.invite_counts[inviter.id]['invite_count'] += 1
                invite_count = self.invite_counts[inviter.id]['invite_count']
                first_name = self.invite_counts[inviter.id]['first_name']
                balance = invite_count * 50
                remaining = max(200 - invite_count, 0)

                message = (
                    f"📊 New Invite:\n"
                    f"👤 User: {first_name}\n"
                    f"👥 Invites: {invite_count}\n"
                    f"💰 Balance: {balance} ETB\n"
                    f"🚀 Remaining Invites: {remaining}"
                )
                # Notify group on every 10th invite
                if invite_count % 10 == 0:
                    await self.send_to_group(message)
            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        message = (
            f"📊 Invite Progress:\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: {invite_count}\n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Remaining Invites: {remaining}"
        )

        await query.answer(f"Progress for {first_name}: {remaining} more invites needed!", show_alert=True)

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))

            logger.info("Bot started successfully!")

            # Run the bot asynchronously
            asyncio.run(application.run_polling(drop_pending_updates=True))

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

# Web server to keep the service running on Render
@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GROUP_ID = int(os.getenv('TELEGRAM_GROUP_ID', 0))  # Group ID from env

    if not TOKEN or not GROUP_ID:
        logger.error("Bot token or group ID missing. Check environment variables.")
        return

    bot = InviteTrackerBot(TOKEN, GROUP_ID)

    # Run the bot and the Flask app in the same event loop
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())  # Start the bot as a background task

    # Start the Flask app (it will run in the main thread)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
