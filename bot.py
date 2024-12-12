import os
import logging
import random
import asyncio
from typing import Dict
import firebase_admin
from firebase_admin import credentials, firestore
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

# Firebase initialization
cred_path = os.getenv('FIREBASE_CREDENTIALS')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Ensure 'users' collection exists
def ensure_users_collection():
    try:
        users_ref = db.collection('users').document('default')
        if not users_ref.get().exists:
            users_ref.set({'created': True})
            logger.info("Default document added to 'users' collection.")
    except Exception as e:
        logger.error(f"Error ensuring users collection exists: {e}")

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_ref = db.collection('users').document(str(user.id))
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            })

        user_data = user_ref.get().to_dict()
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
        ]

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

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        user_id = query.data.split('_')[1]

        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            user_data = user_data.to_dict()
            invite_count = user_data['invite_count']
            balance = invite_count * 50
            message = f"Your current balance is {balance} ETB, based on {invite_count} invites."
        else:
            message = "No data found for this user."

        await query.edit_message_text(message)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        message = "This is the withdrawal key section. Please proceed with the next steps."
        await query.edit_message_text(message)

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user
                if inviter.id == new_member.id:
                    continue

                user_ref = db.collection('users').document(str(inviter.id))
                user_data = user_ref.get()

                if not user_data.exists:
                    user_ref.set({
                        'invite_count': 0,
                        'first_name': inviter.first_name,
                        'withdrawal_key': None
                    })

                invite_count = user_data.to_dict().get('invite_count', 0) if user_data.exists else 0
                user_ref.update({'invite_count': invite_count + 1})

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

            logger.info("Bot started successfully!")

            ensure_users_collection()

            asyncio.get_event_loop().run_until_complete(application.run_polling(drop_pending_updates=True))

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
    loop.create_task(bot.run())

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
