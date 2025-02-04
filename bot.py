import os
import logging
import random
import asyncio
from typing import Dict
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Load environment variables
load_dotenv()

# Configure logging
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

    def generate_unique_id(self, user_id: int) -> str:
        if user_id not in self.user_unique_ids:
            unique_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            self.user_unique_ids[user_id] = unique_id
        return self.user_unique_ids[user_id]

    async def send_invite_info(self, update: Update, user_id: int):
        user = self.invite_counts.get(user_id, {'invite_count': 0})
        invite_count = user['invite_count']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)
        first_name = user.get('first_name', 'User')
        unique_id = self.generate_unique_id(user_id)

        buttons = [[
            InlineKeyboardButton("Check", callback_data=f"check_{user_id}"),
            InlineKeyboardButton("Key🔑", callback_data=f"key_{user_id}")
        ]]

        if invite_count >= 200:
            message = (
                f"🎉 Congratulations {first_name}!\n\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 You can now withdraw!\n"
                f"👉 Click below to proceed."
            )
            buttons.append([InlineKeyboardButton("Withdraw", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
        else:
            message = (
                f"📊 Invite Progress\n\n"
                f"👥 Invites: {invite_count}\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Invite {remaining} more people to withdraw!"
            )

        await update.message.reply_text(
            f"{message}\n\nYour Code: {unique_id}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        await query.answer()
        await self.send_invite_info(update, user_id)

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name

        if user_id not in self.invite_counts:
            self.invite_counts[user_id] = {'invite_count': 0, 'first_name': first_name}
        
        await self.send_invite_info(update, user_id)

    async def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.handle_start))
        application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
        
        logger.info("Bot started successfully!")
        await application.run_polling(drop_pending_updates=True)


def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided.")
        return

    bot = InviteTrackerBot(TOKEN)
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()
