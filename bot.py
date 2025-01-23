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
        for new_member in update.message.new_chat_members:
            try:
                # Instead of assuming the message sender is the inviter, we check logs
                chat_id = update.message.chat_id
                events = await context.bot.get_chat_event_log(
                    chat_id=chat_id,
                    query="",
                    from_date=update.message.date - 60,  # Look back one minute for the invite event
                    to_date=update.message.date,
                    filters={'member_invited': True}  # Only member_invited events
                )
                
                for event in events:
                    if event.action == 'chat_member':
                        inviter_id = event.from_user.id
                        if inviter_id != new_member.id:  # Avoid counting self-joins
                            if inviter_id not in self.invite_counts:
                                self.invite_counts[inviter_id] = {
                                    'invite_count': 0,
                                    'first_name': event.from_user.first_name,
                                    'withdrawal_key': None
                                }
                            self.invite_counts[inviter_id]['invite_count'] += 1
                            invite_count = self.invite_counts[inviter_id]['invite_count']

                            if invite_count % 2 == 0:
                                first_name = self.invite_counts[inviter_id]['first_name']
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
                                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter_id}")]
                                    ]

                                await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=InlineKeyboardMarkup(buttons))
                            break  # We've identified the inviter, no need to continue

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # ... [No changes here, method remains the same]

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # ... [No changes here, method remains the same]

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
