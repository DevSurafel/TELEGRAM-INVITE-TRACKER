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
from telegram.constants import ParseMode

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
        self.group_member_cache: Dict[int, set] = {}  # Cache to track unique members per group

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat

        if not user or not chat:
            return

        # Initialize user invite tracking
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name or "User",
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

        message = self._generate_progress_message(
            first_name, invite_count, balance, remaining
        )

        await update.message.reply_text(
            message, 
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat:
            return

        # Initialize group cache if not exists
        if chat.id not in self.group_member_cache:
            self.group_member_cache[chat.id] = set()

        for new_member in update.message.new_chat_members:
            try:
                # Skip if new member is the bot or is joining their own
                if new_member.id == context.bot.id or new_member.id == update.effective_user.id:
                    continue

                # Try to get the inviter (might be None in some scenarios)
                inviter = update.effective_user
                if not inviter or inviter.id == new_member.id:
                    continue

                # Only increment if this is a new unique member in the group
                if new_member.id not in self.group_member_cache[chat.id]:
                    # Initialize inviter tracking if not exists
                    if inviter.id not in self.invite_counts:
                        self.invite_counts[inviter.id] = {
                            'invite_count': 0,
                            'first_name': inviter.first_name or "User",
                            'withdrawal_key': None
                        }

                    # Increment invite count
                    self.invite_counts[inviter.id]['invite_count'] += 1
                    invite_count = self.invite_counts[inviter.id]['invite_count']

                    # Add member to group cache
                    self.group_member_cache[chat.id].add(new_member.id)

                    # Periodic notification (every 10 invites)
                    if invite_count % 10 == 0:
                        await self._send_invite_progress(update, inviter, invite_count)

            except Exception as e:
                logger.error(f"Error tracking invite for {new_member.id}: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer("Checking invite progress...")
        
        if not query.data:
            return

        try:
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
                f"📊 Invite Progress: @Digital_Birri\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} successful\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Remaining: {remaining} more invites needed\n"
                f"-----------------------"
            )

            await query.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error in handle_check: {e}")

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer("Generating withdrawal key...")
        
        if not query.data:
            return

        try:
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
                await query.answer(f"Key for {first_name}: {withdrawal_key}", show_alert=True)
            else:
                await query.answer(f"Need 200 invites to get a withdrawal key. Current invites: {invite_count}", show_alert=True)

        except Exception as e:
            logger.error(f"Error in handle_key: {e}")

    # NEW: Added run method to start the bot
    def run(self):
        try:
            # Create the Application and pass it your bot's token
            application = Application.builder().token(self.token).build()

            # Register handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

            # Start the Bot
            logger.info("Starting bot...")
            
            # Use run_polling for development, switched to asyncio for better compatibility
            asyncio.run(application.run_polling(drop_pending_updates=True))

        except Exception as e:
            logger.error(f"Error running bot: {e}")

    def _generate_progress_message(self, first_name, invite_count, balance, remaining):
        if invite_count >= 200:
            return (
                f"🎉 <b>Milestone Achieved: @Digital_Birri</b>\n\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} successful\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Withdrawal: Now Available!\n\n"
                f"Click Withdrawal Request to proceed"
            )
        else:
            return (
                f"📊 <b>Invite Progress: @Digital_Birri</b>\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} successful\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Goal: {remaining} more invites needed\n\n"
                f"Keep inviting to reach your milestone!"
            )

    async def _send_invite_progress(self, update: Update, inviter, invite_count):
        first_name = self.invite_counts[inviter.id]['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        buttons = []
        if invite_count >= 200:
            message = (
                f"🎉 <b>Milestone Achieved: @Digital_Birri</b>\n\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} successful\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Withdrawal: Now Available!\n\n"
                f"Click below to proceed with withdrawal 👇"
            )
            buttons.append([InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
        else:
            message = (
                f"📊 <b>Invite Progress: @Digital_Birri</b>\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} successful\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Goal: {remaining} more invites needed\n\n"
                f"Keep inviting to reach your milestone!"
            )
            buttons.append([InlineKeyboardButton("Check Progress", callback_data=f"check_{inviter.id}")])

        try:
            await update.message.reply_text(
                message, 
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Could not send progress message: {e}")

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
