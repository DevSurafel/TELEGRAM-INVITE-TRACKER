import os
import logging
from typing import Dict
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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

    @staticmethod
    def format_message_with_border(message: str) -> str:
        """Add a border around the message for better visuals."""
        lines = message.split('\n')
        max_length = max(len(line) for line in lines)
        border = '-' * (max_length + 4)  # Adding padding
        bordered_message = f"{border}\n" + \
                           '\n'.join(f"| {line.ljust(max_length)} |" for line in lines) + \
                           f"\n{border}"
        return bordered_message

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for the /start command"""
        message = (
            "👋 **Hello!**\n\n"
            "I'm an invite tracking bot. I'll keep track of how many users "
            "each person invites to the group.\n\n"
            "🎯 **Goal:** Invite friends and earn rewards!"
        )
        bordered_message = self.format_message_with_border(message)
        await update.message.reply_text(bordered_message, parse_mode="Markdown")

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

                # Log the invite
                logger.info(f"User {inviter.first_name} (ID: {inviter.id}) invited {new_member.first_name}")

                # Get invite stats
                invite_count = self.invite_counts[inviter.id]
                balance = invite_count * 50
                remaining = max(3 - invite_count, 0)

                # Milestone message
                if invite_count % 2 == 0:
                    if invite_count < 3:
                        message = (
                            f"👋 **Hello, {inviter.first_name}!**\n\n"
                            f"📊 **Your Progress So Far:**\n"
                            f"- **Invited:** {invite_count} people\n"
                            f"- **Balance:** {balance} ETB 💰\n"
                            f"- **Remaining to Next Goal:** {remaining} people 🚀\n\n"
                            "🏆 Keep inviting to earn more rewards!\n"
                            "💸 **Tip:** When you reach 10,000 ETB, you can withdraw your money!"
                        )
                        bordered_message = self.format_message_with_border(message)
                        await update.message.reply_text(bordered_message, parse_mode="Markdown")
                    elif invite_count == 3:
                        message = (
                            f"🎉 **Congratulations, {inviter.first_name}!** 🎉\n\n"
                            f"🌟 **You've Reached an Amazing Milestone!** 🌟\n"
                            f"- **Total Invites:** 200 people 👥\n"
                            f"- **Total Balance:** 10,000 ETB 💰\n"
                            f"- **Goal Achieved:** 🎯\n\n"
                            "📩 **Next Step:**\n"
                            "Now you can request a withdrawal by clicking the button below!\n"
                            "👇👇👇"
                        )
                        bordered_message = self.format_message_with_border(message)
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("Request Withdrawal", url="https://t.me/digital_birr_bot")]
                        ])
                        await update.message.reply_text(
                            bordered_message,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
            
            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def show_invite_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the current invite count for the user"""
        user = update.effective_user
        invite_count = self.invite_counts.get(user.id, 0)
        message = (
            f"👋 **Hello, {user.first_name}!**\n\n"
            f"📊 **Your Current Stats:**\n"
            f"- **Invited:** {invite_count} people\n\n"
            "Keep inviting to reach your goals! 🚀"
        )
        bordered_message = self.format_message_with_border(message)
        await update.message.reply_text(bordered_message, parse_mode="Markdown")

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
