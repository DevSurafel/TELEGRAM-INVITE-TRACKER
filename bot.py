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

    # Rest of the methods (handle_check, handle_key, run) remain the same as in the original script
    # ... (copy the previous implementation)

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
