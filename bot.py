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

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}
        self.invite_requests: Dict[int, int] = {}

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
                f"👥 Invites: You have invited {invite_count} people!\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Withdrawal: You can now withdraw!\n"
                f"-----------------------\n\n"
                f"Click below to withdraw 👇"
            )
            buttons.append([InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot")])
        else:
            message = (
                f"📊 Invite Progress: @DIGITAL_BIRRI\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: You have invited {invite_count} people\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Withdrawal: Invite {remaining} more people to withdraw.\n"
                f"-----------------------\n\n"
                f"Invite more people to increase your rewards!"
            )

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        for new_member in update.message.new_chat_members:
            try:
                message = "Welcome! Please confirm your inviter with /confirm_inviter <username>"
                await update.message.reply_text(message)
                self.invite_requests[new_member.id] = None
            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def confirm_inviter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            message_text = update.message.text
            inviter_username = message_text.split(' ')[1]
            # In a real app, you'd look up the inviter by username
            inviter_id = random.randint(1000, 9999)  # Example logic

            self.invite_counts.setdefault(inviter_id, {
                'invite_count': 0,
                'first_name': inviter_username,
                'withdrawal_key': None
            })
            self.invite_counts[inviter_id]['invite_count'] += 1
            invite_count = self.invite_counts[inviter_id]['invite_count']
            first_name = self.invite_counts[inviter_id]['first_name']
            balance = invite_count * 50

            message = (
                f"🎉 {first_name}, you have {invite_count} invites now!\n"
                f"💰 Balance: {balance} ETB."
            )
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error confirming inviter: {e}")

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/confirm_inviter \w+$'), self.confirm_inviter))

            logger.info("Bot is starting...")
            asyncio.run(application.run_polling(drop_pending_updates=True))
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())  # Run bot as background task
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
