import os
import logging
import asyncio
from typing import Dict
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ChatType

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id
        self.invite_counts.setdefault(user_id, {'invite_count': 0, 'withdrawal_key': None})

        invites = self.invite_counts[user_id]['invite_count']
        balance = invites * 50
        remaining = max(200 - invites, 0)
        first_name = user.first_name

        message = (
            f"👤 User: {first_name}\n"
            f"👥 Invites: {invites}\n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Remaining to Withdraw: {remaining}\n"
        )

        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user_id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user_id}")],
        ]

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        inviter = update.effective_user
        if inviter:
            user_id = inviter.id
            self.invite_counts.setdefault(user_id, {'invite_count': 0, 'withdrawal_key': None})
            self.invite_counts[user_id]['invite_count'] += 1
            logger.info(f"{inviter.first_name} has now {self.invite_counts[user_id]['invite_count']} invites.")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        invites = self.invite_counts.get(user_id, {}).get('invite_count', 0)
        remaining = max(200 - invites, 0)
        await query.answer(f"Invites: {invites}, Remaining: {remaining}", show_alert=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        if self.invite_counts.get(user_id, {}).get('invite_count', 0) >= 200:
            key = self.invite_counts[user_id].setdefault('withdrawal_key', random.randint(100000, 999999))
            await query.answer(f"Your withdrawal key: {key}", show_alert=True)
        else:
            await query.answer("You need at least 200 invites to get a withdrawal key!", show_alert=True)

    async def fetch_members_periodically(self, chat_id: int):
        while True:
            try:
                count = await self.application.bot.get_chat_members_count(chat_id)
                logger.info(f"Group has {count} members.")
            except Exception as e:
                logger.error(f"Failed to fetch group members: {e}")
            await asyncio.sleep(600)

    def run(self):
        application = Application.builder().token(self.token).build()

        # Handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
        application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r"^check_\d+$"))
        application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r"^key_\d+$"))

        # Periodic Task
        self.application = application
        group_id = -1002033347065  # Replace with actual group ID
        asyncio.get_event_loop().create_task(self.fetch_members_periodically(group_id))

        logger.info("Starting bot...")
        application.run_polling()

# Flask health check
@app.route('/')
def health_check():
    return "Bot is running!"

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("Bot token not provided.")
        return

    bot = InviteTrackerBot(token)
    asyncio.run(bot.run())

if __name__ == "__main__":
    app.run(port=5000)
    main()
