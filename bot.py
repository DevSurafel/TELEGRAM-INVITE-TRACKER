import os
import logging
import random
from typing import Dict
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class InviteTrackerBot:
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.invite_counts: Dict[int, Dict[str, int]] = {}
        self.application = Application.builder().token(self.token).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            }

        invite_count = self.invite_counts[user.id]['invite_count']
        first_name = self.invite_counts[user.id]['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        buttons = [
            [
                InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
                InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")
            ]
        ]

        if invite_count >= 200:
            message = (
                f"Congratulations 👏👏🎉\n\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} people invited!\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 You are eligible for withdrawal!\n"
            )
            buttons.append(
                [InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]
            )
        else:
            message = (
                f"📊 Invite Progress:\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} people invited\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Invite {remaining} more people to become eligible for withdrawal."
            )

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    async def handle_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process incoming updates."""
        await self.application.process_update(update)

    async def set_webhook(self):
        """Set the webhook for Telegram."""
        await self.application.bot.set_webhook(self.webhook_url)

    def run(self):
        """Run the bot using webhooks."""
        self.application.add_handler(CommandHandler("start", self.start))

        asyncio.run(self.set_webhook())


# Flask endpoint for Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming updates from Telegram."""
    json_data = request.get_json()
    update = Update.de_json(json_data, bot.application.bot)
    asyncio.run(bot.handle_update(update))
    return "OK", 200


@app.route("/")
def health_check():
    """Health check endpoint."""
    return "Bot is running!"


def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    PUBLIC_IP = os.getenv('PUBLIC_IP')  # Set this to your EC2 public IP or domain
    WEBHOOK_URL = f"https://{PUBLIC_IP}/webhook"

    if not TOKEN or not PUBLIC_IP:
        logger.error("Bot token or public IP is not set.")
        return

    global bot
    bot = InviteTrackerBot(TOKEN, WEBHOOK_URL)
    bot.run()

    # Run Flask app with SSL
    app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"))


if __name__ == "__main__":
    main()
