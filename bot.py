import os
import logging
from typing import Dict
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='invite_tracker.log'
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        # Store invite counts for each user across different groups
        self.invite_counts: Dict[int, Dict[int, Dict[str, int]]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for the /start command in private chat"""
        user = update.effective_user
        
        # Create keyboard with Check Progress button
        keyboard = [
            [InlineKeyboardButton("Check My Total Invites", callback_data="my_progress")]
        ]
        
        await update.message.reply_text(
            f"Hello {user.first_name}! 👋\n\n"
            "I'm an invite tracking bot. I help you keep track of your group invitations!\n\n"
            "Click the button below to check your total invite progress across all groups.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_my_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle user's request to check their invite progress"""
        query = update.callback_query
        user = query.from_user

        # Prepare progress message
        progress_message = "🌟 Your Total Invite Progress 🌟\n\n"
        total_invites = 0
        total_balance = 0

        # Check if user has any invite records
        if user.id in self.invite_counts:
            for group_id, group_data in self.invite_counts[user.id].items():
                progress_message += (
                    f"Group ID {group_id}:\n"
                    f"👥 Invites: {group_data['invite_count']} people\n"
                    f"💰 Balance: {group_data['invite_count'] * 50} ETB\n"
                    f"🚀 Next Milestone: {group_data['invite_count'] + (6 - (group_data['invite_count'] % 2))} invites\n\n"
                )
                total_invites += group_data['invite_count']
                total_balance += group_data['invite_count'] * 50
        else:
            progress_message += "You haven't invited anyone to any groups yet. 😔\n"

        progress_message += (
            f"----------------------\n"
            f"Total Invites Across All Groups: {total_invites}\n"
            f"Total Balance Across All Groups: {total_balance} ETB"
        )

        # Send or update the message with progress
        await query.answer()
        await query.edit_message_text(
            text=progress_message,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Refresh", callback_data="my_progress")]
            ])
        )

    # [All other methods from the previous implementation remain EXACTLY THE SAME]
    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Track new members and their inviters"""
        group_id = update.message.chat_id
        
        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user

                # Ignore bot invites or self-joins
                if inviter.id == new_member.id:
                    continue

                # Initialize user's invite tracking if not exists
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {}
                
                if group_id not in self.invite_counts[inviter.id]:
                    self.invite_counts[inviter.id][group_id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name
                    }

                # Increment invite count for this specific group
                self.invite_counts[inviter.id][group_id]['invite_count'] += 1

                # Get invite stats for this group
                invite_count = self.invite_counts[inviter.id][group_id]['invite_count']
                balance = invite_count * 50
                next_milestone = invite_count + (6 - (invite_count % 2))
                remaining = max(next_milestone - invite_count, 0)

                # Milestone logic
                if invite_count % 2 == 0 or invite_count == 6:
                    keyboard = [
                        [InlineKeyboardButton("Check Progress", callback_data=f"check_{inviter.id}_{group_id}")],
                    ]
                    if invite_count >= 6:
                        keyboard.append(
                            [InlineKeyboardButton("Request Withdrawal", url="https://your-withdrawal-link.com")]
                        )
                    await update.message.reply_text(
                        f"🎉 Milestone Achieved! 🎉👏\n\n"
                        f"📋 Dashboard:\n"
                        f"-----------------------\n"
                        f"👤 Name: {inviter.first_name}\n"
                        f"👥 Invites in this Group: {invite_count} people\n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Next Goal: Invite {remaining} more\n"
                        f"-----------------------\n\n"
                        f"Keep inviting to earn more rewards!",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    def run(self):
        """Run the bot"""
        try:
            application = Application.builder().token(self.token).build()

            # Register handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.track_new_member
            ))
            # New handler for private progress check
            application.add_handler(CallbackQueryHandler(self.handle_my_progress, pattern="^my_progress$"))
            
            # Rest of the handlers remain the same
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_back, pattern=r'^back_\d+_\d+$'))

            # Start the bot
            logger.info("Bot started successfully!")
            application.run_polling(drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
