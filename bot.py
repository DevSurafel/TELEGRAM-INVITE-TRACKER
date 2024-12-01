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
        # Store invite counts for each user
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for the /start command"""
        await update.message.reply_text(
            "Welcome! %firstname% I'm an invite tracking bot. "
            "I'll help you keep track of your group invitations!"
        )

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Track new members and their inviters"""
        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user

                # Ignore bot invites or self-joins
                if inviter.id == new_member.id:
                    continue

                # Initialize user's invite tracking if not exists
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name
                    }

                # Increment invite count
                self.invite_counts[inviter.id]['invite_count'] += 1

                # Get invite stats
                invite_count = self.invite_counts[inviter.id]['invite_count']
                balance = invite_count * 50
                next_milestone = invite_count + (6 - (invite_count)
                remaining = (6 - (invite_count)) people

                # Milestone logic
                if invite_count % 2 == 0 or invite_count == 6:
                    keyboard = [
                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")],
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
                        f"👥 Invites: {invite_count} people\n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Next Goal: Invite {remaining} more\n"
                        f"-----------------------\n\n"
                        f"Keep inviting to earn more rewards!",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )

            except Exception as e:
                logger.error(f"Error tracking invite: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the 'Check' button callback"""
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        
        # Ensure the user has invite tracking
        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        # Get the specific user's invite details
        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']

        # Requesting user's details
        requester_id = query.from_user.id
        requester_data = self.invite_counts.get(requester_id, {'invite_count': 0, 'first_name': query.from_user.first_name})
        
        next_milestone = invite_count + (6 - (invite_count % 2))
        remaining = max(next_milestone - invite_count, 0)

        keyboard = [[InlineKeyboardButton("Back", callback_data=f"back_{user_id}")]]
        
        if invite_count == 6:
            message = (
                f"🎉 Milestone achieved 🎉\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} people\n"
                f"🚀 Remaining to withdrawal: {remaining} people\n"
                f"-----------------------\n"
                f"👤 Your Invites: {requester_data['invite_count']} people\n"
                f"-----------------------\n\n"
                f"Keep inviting to earn more rewards!"
            )
        else:
            message = (
                f"📊 Invite Progress:\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: {invite_count} people\n"
                f"🚀 Remaining for withdrawal: {remaining} more people\n"
                f"-----------------------\n"
                f"👤 Your Invites: {requester_data['invite_count']} people\n"
                f"-----------------------\n\n"
                f"Keep inviting to earn more rewards!"
            )

        await query.answer()
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the 'Back' button callback"""
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        
        # Ensure the user has invite tracking
        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        # Get the specific user's invite details
        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        balance = invite_count * 50
        next_milestone = invite_count + (2 - (invite_count % 2))
        remaining = (6 - invite_count, 0)

        keyboard = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user_id}")],
        ]
        if invite_count >= 6:
            keyboard.append(
                [InlineKeyboardButton("Request Withdrawal", url="https://your-withdrawal-link.com")]
            )

        await query.answer()
        await query.edit_message_text(
            text=(
                f"🎉 Milestone Achieved! 🎉👏\n\n"
                f"📋 Dashboard:\n"
                f"-----------------------\n"
                f"👤 Name: {first_name}\n"
                f"👥 Invites: {invite_count} people\n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Next Goal: Invite {remaining} more\n"
                f"-----------------------\n\n"
                f"Keep inviting to earn more rewards!"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

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
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_back, pattern=r'^back_\d+$'))

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
