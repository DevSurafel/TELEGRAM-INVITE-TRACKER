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

# Dictionary to store invite counts
invite_counts: Dict[int, int] = {}

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for the /start command"""
        await update.message.reply_text(
            "Welcome! I'm an invite tracking bot. "
            "I'll keep track of how many users each person invites to the group."
        )

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Track new members and their inviters"""
        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user

                # Ignore bot invites or self-joins
                if inviter.id == new_member.id:
                    continue

                # Update invite count
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = 0
                self.invite_counts[inviter.id] += 1

                # Get invite stats
                invite_count = self.invite_counts[inviter.id]
                balance = invite_count * 50
                remaining = max(6 - invite_count, 0)

                # Milestone messages
                if invite_count in [2, 4]:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                    ])
                    await update.message.reply_text(
                        f"🎉 **Milestone Achieved!** 🎉\n\n"
                        f"📋 **Dashboard:**\n"
                        f"-----------------------\n"
                        f"👤 **User:** {inviter.first_name}\n"
                        f"👥 **Invites:** {invite_count}\n"
                        f"💰 **Balance:** {balance} ETB\n"
                        f"🚀 **Next Goal:** Invite {remaining} more\n"
                        f"-----------------------\n\n"
                        f"Keep inviting to earn more rewards!",
                        reply_markup=keyboard
                    )

                elif invite_count == 6:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")],
                        [InlineKeyboardButton("Request Withdrawal", url="https://your-withdrawal-link.com")]
                    ])
                    await update.message.reply_text(
                        f"🎉 **Congratulations, {inviter.first_name}!** 🎉\n\n"
                        f"🎯 **Milestone Reached:**\n"
                        f"-----------------------\n"
                        f"👥 **Total Invites:** {invite_count}\n"
                        f"💰 **Total Balance:** {balance} ETB\n"
                        f"🎖️ **Reward Unlocked:** Withdrawal Available\n"
                        f"-----------------------\n\n"
                        f"Click below to request your withdrawal!",
                        reply_markup=keyboard
                    )

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the 'Check' button callback"""
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        invite_count = self.invite_counts.get(user_id, 0)
        remaining = max(6 - invite_count, 0)

        await query.answer()
        await query.edit_message_text(
            text=(
                f"📊 **Your Progress:**\n"
                f"-----------------------\n"
                f"👥 **Invites:** {invite_count}\n"
                f"🚀 **Remaining:** {remaining} more\n"
                f"-----------------------\n\n"
                f"Keep inviting to earn more rewards!"
            )
        )

    async def show_invite_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the current invite count for the user"""
        user = update.effective_user
        invite_count = self.invite_counts.get(user.id, 0)
        await update.message.reply_text(
            f"You have invited {invite_count} people to the group!"
        )

    def run(self):
        """Run the bot"""
        try:
            # Create the Application and pass it your bot's token
            application = Application.builder().token(self.token).build()

            # Register handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("invites", self.show_invite_count))
            application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.track_new_member
            ))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))

            # Start the bot
            logger.info("Bot started successfully!")
            application.run_polling(drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

def main():
    # Get bot token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    # Create and run bot
    bot = InviteTrackerBot(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
