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
    def __init__(self, token: str, group_id: str):
        self.token = token
        self.group_id = group_id  # Store the group ID
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.chat.id != int(self.group_id):
            return

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

        if invite_count >= 200:
            message = (
                f"Congratulations 👏👏🎉\n\n"
                f"📊 Milestone Achieved: DIGITAL BIRR\n"
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
                f"📊 Invite Progress: DIGITAL BIRR\n"
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
        if update.message.chat.id != int(self.group_id):
            return

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

                if invite_count % 10 == 0:
                    first_name = self.invite_counts[inviter.id]['first_name']
                    balance = invite_count * 50
                    remaining = max(200 - invite_count, 0)

                    if invite_count >= 200:
                        message = (
                            f"Congratulations 👏👏🎉\n\n"
                            f"📊 Milestone Achieved: DIGITAL BIRR\n"
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
                            f"📊 Invite Progress: DIGITAL BIRR\n"
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
                logger.error(f"Error tracking invite: {e}")

    def run(self):
        application = Application.builder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
        application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
        application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

        return application

# Flask route
@app.route('/')
def index():
    return "Bot is running!"

async def run_both(bot: InviteTrackerBot):
    application = bot.run()
    loop = asyncio.get_event_loop()

    # Run Flask app and bot simultaneously
    await asyncio.gather(
        application.run_polling(drop_pending_updates=True),
        loop.run_in_executor(None, app.run, '0.0.0.0', int(os.getenv('PORT', 5000)))
    )

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GROUP_ID = os.getenv('GROUP_ID')
    if not TOKEN or not GROUP_ID:
        logger.error("No bot token or group ID provided. Set TELEGRAM_BOT_TOKEN and GROUP_ID environment variables.")
        return

    bot = InviteTrackerBot(TOKEN, GROUP_ID)
    asyncio.run(run_both(bot))

if __name__ == "__main__":
    main()
