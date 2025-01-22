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
        self.invite_tokens = {}  # {inviter_id: {token: used_status}}
        self.invite_counts = {}  # {user_id: {'invite_count': count, 'first_name': name, 'withdrawal_key': key}}
        self.application = None  # Store application instance for later use

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            }

        buttons = [
            [InlineKeyboardButton("Generate Invite Token", callback_data=f"generate_token_{user.id}"),
             InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
        ]
        await update.message.reply_text("Welcome! Here you can manage your invites and check your progress.", reply_markup=InlineKeyboardMarkup(buttons))

    async def generate_invite_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        token = random.randint(100000, 999999)  # Generate a unique token
        if user.id not in self.invite_tokens:
            self.invite_tokens[user.id] = {}
        self.invite_tokens[user.id][token] = False  # Mark token as unused

        await update.message.reply_text(
            f"Your invite token for your friend is: {token}\n"
            "Ask your friend to use this token when joining the group.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Generate Another Token", callback_data=f"generate_token_{user.id}")]
            ])
        )

    async def join_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            token = int(context.args[0])
            matched = False
            for inviter_id, tokens in self.invite_tokens.items():
                if token in tokens and not tokens[token]:
                    tokens[token] = True  # Mark token as used
                    await self.update_invite_count_by_id(inviter_id, context)
                    await update.message.reply_text("You've successfully joined the group! Welcome!")
                    matched = True
                    break
            if not matched:
                await update.message.reply_text("Invalid or already used token.")
        else:
            await update.message.reply_text("Please provide your invite token. Example: /join 123456")

    async def update_invite_count_by_id(self, inviter_id, context: ContextTypes.DEFAULT_TYPE):
        if inviter_id not in self.invite_counts:
            user = await context.bot.get_chat_member(context.chat_id, inviter_id)
            self.invite_counts[inviter_id] = {
                'invite_count': 0,
                'first_name': user.user.first_name,
                'withdrawal_key': None
            }
        self.invite_counts[inviter_id]['invite_count'] += 1
        invite_count = self.invite_counts[inviter_id]['invite_count']
        
        if invite_count % 2 == 0:  # Every 2 invites, notify the inviter
            message = f"Congratulations! You've invited {invite_count} members. Use /claim to get your reward!"
            await context.bot.send_message(chat_id=inviter_id, text=message)

    async def claim_invite(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if user.id in self.invite_counts:
            invite_count = self.invite_counts[user.id]['invite_count']
            if invite_count > 0:
                balance = invite_count * 50
                message = f"You have claimed your reward for {invite_count} invites. Your balance is now {balance} ETB."
                self.invite_counts[user.id]['invite_count'] = 0  # Reset invite count after claim
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("You have no invites to claim.")
        else:
            await update.message.reply_text("You have no invitation data.")

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
        remaining = max(4 - invite_count, 0)

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

        if invite_count >= 4:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            await query.answer(f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{withdrawal_key}", show_alert=True)
        else:
            await query.answer(f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", show_alert=True)

    async def run(self):
        try:
            self.application = Application.builder().token(self.token).build()

            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("generate_token", self.generate_invite_token))
            self.application.add_handler(CommandHandler("join", self.join_group))
            self.application.add_handler(CommandHandler("claim", self.claim_invite))
            self.application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            self.application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))
            self.application.add_handler(CallbackQueryHandler(self.generate_invite_token, pattern=r'^generate_token_\d+$'))

            logger.info("Bot started successfully!")

            # Send a message to confirm bot is operational in the group
            await self.send_startup_message()

            # Run the bot asynchronously
            await self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

    async def send_startup_message(self):
        """Send a message to the group to confirm the bot is operational."""
        try:
            # Replace '-1002033347065' with the actual chat ID of the group
            await self.application.bot.send_message(chat_id='-1002033347065', text="Bot has started and is now operational!")
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")

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
    asyncio.run(bot.run())

if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    main()
