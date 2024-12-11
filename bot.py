import os
import logging
import random
import json
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
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

class PersistentInviteTracker:
    def __init__(self, storage_file='invite_tracker.json'):
        self.storage_file = storage_file
        self.invite_counts = self.load_data()

    def load_data(self) -> Dict[str, Dict[str, int]]:
        """Load invite counts from a JSON file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading invite data: {e}")
            return {}

    def save_data(self):
        """Save invite counts to a JSON file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.invite_counts, f, indent=4)
            logger.debug("Invite data saved successfully")
        except Exception as e:
            logger.error(f"Error saving invite data: {e}")

    def increment_invite_count(self, inviter_id: int, inviter_name: str):
        """Increment invite count for a specific user."""
        inviter_id_str = str(inviter_id)
        
        if inviter_id_str not in self.invite_counts:
            self.invite_counts[inviter_id_str] = {
                'invite_count': 0,
                'first_name': inviter_name,
                'withdrawal_key': None
            }
        
        self.invite_counts[inviter_id_str]['invite_count'] += 1
        self.save_data()
        
        return self.invite_counts[inviter_id_str]['invite_count']

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.tracker = PersistentInviteTracker()
        self.user_join_timestamps: Dict[int, float] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        user = update.message.from_user
        user_id_str = str(user.id)

        # Ensure user exists in tracking
        if user_id_str not in self.tracker.invite_counts:
            self.tracker.invite_counts[user_id_str] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            }
            self.tracker.save_data()

        invite_count = self.tracker.invite_counts[user_id_str]['invite_count']
        first_name = self.tracker.invite_counts[user_id_str]['first_name']
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
        if update.message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
            logger.warning("Event not from a supergroup or regular group. Tracking not supported.")
            return

        for new_member in update.message.new_chat_members:
            # Skip if this user has joined recently to prevent double counting
            if new_member.id in self.user_join_timestamps:
                logger.info(f"User {new_member.first_name} already tracked.")
                continue
            
            try:
                inviter = update.message.from_user
                if inviter and inviter.id != new_member.id:
                    # Increment invite count and get new count
                    new_invite_count = self.tracker.increment_invite_count(
                        inviter.id,
                        inviter.first_name or "Unknown"
                    )

                    # Mark this user as tracked
                    self.user_join_timestamps[new_member.id] = asyncio.get_event_loop().time()

                    # Notification logic (every 10 invites)
                    if new_invite_count % 10 == 0 or new_invite_count == 200:
                        balance = new_invite_count * 50
                        remaining = max(200 - new_invite_count, 0)

                        message = (
                            f"📊 Invite Progress:\n"
                            f"👤 User: {inviter.first_name}\n"
                            f"👥 Invites: {new_invite_count}\n"
                            f"💰 Balance: {balance} ETB\n"
                            f"🚀 Invite {remaining} more people for eligibility."
                        )

                        await update.message.reply_text(
                            message, reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                            ])
                        )

                    logger.info(f"Tracked invite: {inviter.first_name} added {new_member.first_name}")

                else:
                    logger.info(f"{new_member.first_name} added without an inviter.")

            except Exception as e:
                logger.error(f"Error tracking new member {new_member.first_name}: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle 'Check' button presses."""
        query = update.callback_query
        user_id = str(query.data.split('_')[1])

        # Reload data to ensure latest information
        self.tracker.invite_counts = self.tracker.load_data()

        if user_id not in self.tracker.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.tracker.invite_counts[user_id]
        invite_count = user_data['invite_count']
        remaining = max(200 - invite_count, 0)

        logger.debug(f"Check request for user {user_id}: Current invite count is {invite_count}")

        await query.answer(
            f"You have invited {invite_count} people! You need to invite {remaining} more people to reach your goal!",
            show_alert=True,
        )

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle 'Key🔑' button presses."""
        query = update.callback_query
        user_id = str(query.data.split('_')[1])

        if user_id not in self.tracker.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.tracker.invite_counts[user_id]
        invite_count = user_data['invite_count']

        if invite_count >= 200:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            self.tracker.save_data()
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
                for user_id, data in self.tracker.invite_counts.items():
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
    loop.create_task(bot.run())  # Run the bot asynchronously
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))  # Start Flask app

if __name__ == "__main__":
    main()
