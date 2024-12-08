import os
import logging
import random
from typing import Dict
from collections import defaultdict
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = defaultdict(lambda: {'invite_count': 0, 'first_name': None, 'withdrawal_key': None})
        self.group_id = int(os.getenv("TELEGRAM_GROUP_ID"))  # Group ID for operations

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_data = self.invite_counts[user.id]
        user_data['first_name'] = user.first_name or "User"
        invite_count = user_data['invite_count']

        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
        ]

        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)
        first_name = user_data['first_name']

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

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.chat.id != self.group_id:
            return

        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user
                if inviter.id == new_member.id:  # Ignore self-invites
                    continue

                user_data = self.invite_counts[inviter.id]
                user_data['first_name'] = inviter.first_name or "User"
                user_data['invite_count'] += 1
                invite_count = user_data['invite_count']

                if invite_count % 10 == 0:  # Notify every 10 invites
                    balance = invite_count * 50
                    remaining = max(200 - invite_count, 0)

                    if invite_count >= 200:
                        message = (
                            f"Congratulations 👏👏🎉\n\n"
                            f"📊 Milestone Achieved: @Digital_Birri\n"
                            f"-----------------------\n"
                            f"👤 User: {user_data['first_name']}\n"
                            f"👥 Invites: Nama {invite_count} afeertaniittu\n"
                            f"💰 Balance: {balance} ETB\n"
                            f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                            f"-----------------------\n\n"
                            f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
                        )
                        buttons = [[InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]]
                    else:
                        message = (
                            f"📊 Invite Progress: @Digital_Birri\n"
                            f"-----------------------\n"
                            f"👤 User: {user_data['first_name']}\n"
                            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                            f"💰 Balance: {balance} ETB\n"
                            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                            f"-----------------------\n\n"
                            f"Add gochuun carraa badhaasaa keessan dabalaa!"
                        )
                        buttons = [[InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]]

                    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        user_data = self.invite_counts.get(user_id)

        if not user_data:
            await query.answer("No invitation data found.")
            return

        invite_count = user_data['invite_count']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        message = (
            f"📊 Invite Progress: @Digital_Birri\n"
            f"-----------------------\n"
            f"👤 User: {user_data['first_name']}\n"
            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
            f"-----------------------\n\n"
            f"Add gochuun carraa badhaasaa keessan dabalaa!"
        )

        await query.answer(message, show_alert=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        user_data = self.invite_counts.get(user_id)

        if not user_data:
            await query.answer("No invitation data found.")
            return

        if user_data['invite_count'] >= 200:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            await query.answer(f"Lakkoofsi Key🔑 keessanii: 👉 {user_data['withdrawal_key']}", show_alert=True)
        else:
            await query.answer(f"Lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", show_alert=True)

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
        application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
        application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

        logger.info("Bot started successfully!")
        application.run_polling(drop_pending_updates=True)

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
