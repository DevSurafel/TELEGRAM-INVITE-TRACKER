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
from telegram.constants import ChatType
from telegram.error import Conflict

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}

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

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Track new group members and count invites."""
        if update.message.chat.type != ChatType.SUPERGROUP:
            logger.warning("Group is not a supergroup. Tracking not supported.")
            return

        for new_member in update.message.new_chat_members:
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

                message = (
                    f"📊 Invite Progress:\n"
                    f"👤 User: {first_name}\n"
                    f"👥 Invites: {invite_count}\n"
                    f"💰 Balance: {balance} ETB\n"
                    f"🚀 Invite {remaining} more people for eligibility."
                )

                await update.message.reply_text(
                    message, reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                    ])
                )

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle 'Check' button presses."""
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        remaining = max(200 - invite_count, 0)

        await query.answer(
            f"You need to invite {remaining} more people to reach your goal!",
            show_alert=True,
        )

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle 'Key🔑' button presses."""
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']

        if invite_count >= 200:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            await query.answer(f"Your withdrawal key: {withdrawal_key}", show_alert=True)
        else:
            await query.answer(
                "You need to invite at least 200 people to receive a withdrawal key!",
                show_alert=True,
            )

    async def fetch_members_periodically(self, chat_id: int):
        """Periodically fetch group member count."""
        while True:
            try:
                members = await self.application.bot.get_chat_member_count(chat_id)
                logger.info(f"Group has {members} members.")
            except Exception as e:
                logger.error(f"Error fetching group members: {e}")
            await asyncio.sleep(600)

    def run(self):
        """Run the bot."""
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r"^check_\d+$"))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r"^key_\d+$"))

            group_id = -1001234567890  # Replace with your group ID
            self.application = application
            asyncio.get_event_loop().create_task(self.fetch_members_periodically(group_id))

            application.run_polling(drop_pending_updates=True)

        except Conflict:
            logger.error("Bot conflict: Another instance is running.")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")


# Flask endpoint for health check
@app.route('/')
def index():
    return "Bot is running!"


def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided.")
        return

    bot = InviteTrackerBot(TOKEN)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))


if __name__ == "__main__":
    main()
