import os
import logging
from typing import Dict
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user

        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {'invite_count': 0, 'first_name': user.first_name}

        keyboard = [[InlineKeyboardButton("Check", callback_data=f"check_{user.id}")]]
        await update.message.reply_text(
            "Welcome! I'm an invite tracking bot. I'll help you keep track of your group invitations!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        for new_member in update.message.new_chat_members:
            try:
                inviter = update.message.from_user

                if inviter.id == new_member.id:
                    continue

                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {'invite_count': 0, 'first_name': inviter.first_name}

                self.invite_counts[inviter.id]['invite_count'] += 1

                invite_count = self.invite_counts[inviter.id]['invite_count']
                balance = invite_count * 50
                remaining = max(6 - invite_count, 0)

                keyboard = [[InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]]
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
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        balance = invite_count * 50
        remaining = max(6 - invite_count, 0)

        keyboard = [[InlineKeyboardButton("Back", callback_data=f"back_{user_id}")]]
        if invite_count >= 6:
            keyboard.append(
                [InlineKeyboardButton("Request Withdrawal", url="https://your-withdrawal-link.com")]
            )

        message = (
            f"📊 Invite Progress:\n"
            f"-----------------------\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: {invite_count} people\n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Remaining for withdrawal: {remaining} more people\n"
            f"-----------------------\n\n"
            f"Keep inviting to earn more rewards!"
        )
        await query.answer()
        await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        balance = invite_count * 50
        remaining = max(6 - invite_count, 0)

        keyboard = [[InlineKeyboardButton("Check", callback_data=f"check_{user_id}")]]
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
                f"🚀 Remaining for withdrawal: {remaining} more\n"
                f"-----------------------\n\n"
                f"Keep inviting to earn more rewards!"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_back, pattern=r'^back_\d+$'))

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
