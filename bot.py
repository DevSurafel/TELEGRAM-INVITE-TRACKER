import os
import logging
import random
from typing import Dict
import asyncio
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes, InlineQueryHandler
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
        self.user_unique_ids: Dict[int, str] = {}

    def generate_unique_id(self, user_id: int) -> str:
        if user_id not in self.user_unique_ids:
            unique_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            self.user_unique_ids[user_id] = unique_id
        return self.user_unique_ids[user_id]

    async def send_invite_info(self, update: Update, user: Dict[int, str], unique_id: str):
        invite_count = user['invite_count']
        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user['user_id']}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user['user_id']}")],
            [InlineKeyboardButton("Enter Inviter Code", callback_data=f"enter_inviter_{user['user_id']}")]  # New button for ID submission
        ]

        first_name = user['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

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
        
        await update.message.reply_text(
            f"{message}\n\nCode'n keessan: {unique_id}", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None,
                'user_id': user.id
            }
        unique_id = self.generate_unique_id(user.id)
        await self.send_invite_info(update, self.invite_counts[user.id], unique_id)

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        for new_member in update.message.new_chat_members:
            try:
                if new_member.is_bot:
                    continue  # Skip if the new member is a bot
                
                user_id = new_member.id
                if user_id not in self.invite_counts:
                    self.invite_counts[user_id] = {
                        'invite_count': 0,
                        'first_name': new_member.first_name,
                        'withdrawal_key': None,
                        'user_id': user_id
                    }
                unique_id = self.generate_unique_id(user_id)
                await self.send_invite_info(update, self.invite_counts[user_id], unique_id)

                context.user_data['new_member_id'] = user_id

            except Exception as e:
                logger.error(f"Error tracking new member: {e}")

    async def first_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_id = user.id
        if user_id not in self.invite_counts:
            self.invite_counts[user_id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None,
                'user_id': user_id
            }
            unique_id = self.generate_unique_id(user_id)
            await self.send_invite_info(update, self.invite_counts[user_id], unique_id)

    async def handle_enter_inviter_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = int(query.data.split('_')[2])  # Extract user ID from callback data
        if user_id not in self.invite_counts or 'inviter_id' in self.invite_counts[user_id]:
            await query.edit_message_text("Kabajamoo, Code nama isin afeeree duraan galchitanii jirtu. Yeroo lammataa galchuu hin dandeessan. 👉/start ")
            return

        # Instead of inline query, we send a message with the command syntax
        await query.edit_message_text("Code nama isin afeeree galchaa :\n\n   /send_invite_code <Code> \n\n  👉/start")

    async def handle_send_invite_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message.text.split()
        
        if len(message) != 2:
            await update.message.reply_text("Code nama isin afeeree galchaa galchaa: \n\n /send_invite_code <Code> \n\n  👉/start")
            return

        inviter_id = message[1].upper()  # Convert to uppercase to match the IDs format

        if user.id not in self.invite_counts:
            await update.message.reply_text("You must be registered to submit an inviter's ID.")
            return
        
        if 'inviter_id' in self.invite_counts[user.id]:
            await update.message.reply_text("Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n 👉/start")
            return

        for inviter_user_id, unique_id in self.user_unique_ids.items():
            if unique_id == inviter_id:
                self.invite_counts[inviter_user_id]['invite_count'] += 1
                self.invite_counts[user.id]['inviter_id'] = inviter_user_id
                await update.message.reply_text(f"Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n  👉/start")
                return
        
        await update.message.reply_text("Code isin galchitan dogooggora. Irra deebi'uun galchaa. \n\n 👉/start")

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
            f"📊 Invite Progress: @DIGITAL_BIRRI\n"
            f"-----------------------\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
            f"-----------------------\n\n"
            f"Add gochuun carraa badhaasaa keessan dabalaa!"
        )

        await query.answer(f"Kabajamoo {first_name}, maallaqa baafachuuf dabalataan nama {remaining} afeeruu qabdu", show_alert=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']

        if invite_count >= 200:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            await query.answer(f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{withdrawal_key}", show_alert=True)
        else:
            await query.answer(f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", show_alert=True)

    async def handle_cancel_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        if 'new_member_id' in context.user_data:
            del context.user_data['new_member_id']
        await query.edit_message_text("ID submission cancelled.")

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.first_message))  
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_enter_inviter_id, pattern=r'^enter_inviter_\d+$'))  # Handler for ID entry instruction
            application.add_handler(CallbackQueryHandler(self.handle_cancel_id, pattern='^cancel_id$'))
            application.add_handler(CommandHandler("send_invite_code", self.handle_send_invite_code))  # New handler for the command

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
