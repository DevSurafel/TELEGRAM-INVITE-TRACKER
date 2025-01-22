import os
import logging
import random
from typing import Dict
from telegram import Update, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str, supergroup_id: int):
        self.token = token
        self.supergroup_id = supergroup_id
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # [Previous start method remains the same]

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"Received member update in chat {update.effective_chat.id}")
        
        if not update.chat_member and not update.my_chat_member:
            logger.info("No chat member update found")
            return

        # Get the correct update
        chat_member_update = update.chat_member or update.my_chat_member
        
        # Log the update details
        logger.info(f"New member status: {chat_member_update.new_chat_member.status}")
        logger.info(f"Old member status: {chat_member_update.old_chat_member.status}")
        logger.info(f"Inviter ID: {chat_member_update.from_user.id}")
        logger.info(f"New member ID: {chat_member_update.new_chat_member.user.id}")

        # Only process updates for the target supergroup
        if update.effective_chat.id != self.supergroup_id:
            logger.info(f"Ignoring update from chat {update.effective_chat.id}")
            return

        new_member = chat_member_update.new_chat_member.user
        inviter = chat_member_update.from_user

        # Check if this is a new member joining
        if (chat_member_update.new_chat_member.status in ["member", "restricted"] and 
            chat_member_update.old_chat_member.status not in ["member", "restricted"]):
            
            # Skip if user joined themselves
            if inviter.id == new_member.id:
                logger.info(f"User {new_member.id} joined by themselves")
                return

            # Initialize inviter's count if needed
            if inviter.id not in self.invite_counts:
                logger.info(f"Initializing count for inviter {inviter.id}")
                self.invite_counts[inviter.id] = {
                    'invite_count': 0,
                    'first_name': inviter.first_name,
                    'withdrawal_key': None
                }

            # Update invite count
            self.invite_counts[inviter.id]['invite_count'] += 1
            invite_count = self.invite_counts[inviter.id]['invite_count']
            logger.info(f"Updated invite count for {inviter.id} to {invite_count}")

            # Rest of the tracking logic remains the same...
            [Previous message sending code remains the same]

    # [Previous handle_check and handle_key methods remain the same]

def run_bot():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    SUPERGROUP_ID = int(os.getenv('SUPERGROUP_ID'))

    if not TOKEN or not SUPERGROUP_ID:
        logger.error("Missing required environment variables")
        return

    bot = InviteTrackerBot(TOKEN, SUPERGROUP_ID)
    app = Application.builder().token(TOKEN).build()

    app.add_handler(ChatMemberHandler(bot.track_new_member, ChatMemberUpdated))
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.handle_check, pattern=r'^check_\d+$'))
    app.add_handler(CallbackQueryHandler(bot.handle_key, pattern=r'^key_\d+$'))

    logger.info("Starting bot...")
    app.run_polling(
        allowed_updates=["message", "chat_member", "my_chat_member", "callback_query"],
        drop_pending_updates=True
    )

if __name__ == "__main__":
    run_bot()
