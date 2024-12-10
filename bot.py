import os
import logging
import random
from typing import Dict, Optional
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ChatType
from telegram.error import Conflict, TelegramError

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
        # Track user first join timestamp to prevent double counting
        self.user_join_timestamps: Dict[int, float] = {}

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
        """Comprehensive tracking of new group members."""
        if update.message.chat.type != ChatType.SUPERGROUP:
            logger.warning("Group is not a supergroup. Tracking not supported.")
            return

        for new_member in update.message.new_chat_members:
            # Skip if this user has joined recently to prevent double counting
            if new_member.id in self.user_join_timestamps:
                logger.info(f"User {new_member.first_name} already tracked.")
                continue

            # Try to get the user who added the new member
            try:
                # Attempt to get chat member info to identify who added the user
                chat = update.message.chat
                inviter = None

                # Try to find the inviter
                try:
                    added_by = update.message.from_user
                    if added_by and added_by.id != new_member.id:
                        # Check if the added_by user is an admin or the new member's inviter
                        chat_member = await chat.get_member(added_by.id)
                        if chat_member.status in ['administrator', 'creator'] or added_by.id != new_member.id:
                            inviter = added_by
                except Exception as admin_check_error:
                    logger.error(f"Error checking admin status: {admin_check_error}")

                # If no specific inviter found, log and continue
                if not inviter:
                    logger.info(f"No specific inviter found for {new_member.first_name}")
                    continue

                # Initialize invite count for the inviter
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name,
                        'withdrawal_key': None
                    }

                # Increment invite count
                self.invite_counts[inviter.id]['invite_count'] += 1
                invite_count = self.invite_counts[inviter.id]['invite_count']

                # Mark this user as tracked
                self.user_join_timestamps[new_member.id] = asyncio.get_event_loop().time()

                # Notification logic (every 10 invites)
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

                logger.info(f"Tracked invite: {inviter.first_name} added {new_member.first_name}")

            except Exception as e:
                logger.error(f"Error tracking new member: {e}")

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
        """Periodically fetch group member count and invite statistics."""
        while True:
            try:
                members = await self.application.bot.get_chat_member_count(chat_id)
                logger.info(f"Group has {members} members.")
                
                # Log invite counts
                for user_id, data in self.invite_counts.items():
                    if data['invite_count'] > 0:
                        logger.info(f"User {data['first_name']} (ID: {user_id}): {data['invite_count']} invites")
                
                # Optional: Clean up old join timestamps
                current_time = asyncio.get_event_loop().time()
                self.user_join_timestamps = {
                    k: v for k, v in self.user_join_timestamps.items() 
                    if current_time - v < 86400  # Keep timestamps for 24 hours
                }

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

            group_id = -1002033347065  # Replace with your group ID
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
