from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Bot started by a user.")
        await update.message.reply_text("Welcome to Digital Birr! 🚀")

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("New member detected in the group")
        for new_member in update.message.new_chat_members:
            logger.info(f"New member: {new_member}")
            inviter = update.message.from_user
            inviter_id = inviter.id

            logger.info(f"Inviter: {inviter}")

            if inviter_id == new_member.id:
                logger.info("Self-invite detected. Skipping.")
                continue

            if inviter_id not in self.invite_counts:
                self.invite_counts[inviter_id] = {
                    'invite_count': 0,
                    'first_name': inviter.first_name,
                    'withdrawal_key': None
                }

            self.invite_counts[inviter_id]['invite_count'] += 1
            logger.info(f"Updated invite count for {inviter_id}: {self.invite_counts[inviter_id]['invite_count']}")

            invite_count = self.invite_counts[inviter_id]['invite_count']

            # Notify user when milestones are reached
            if invite_count % 10 == 0:
                logger.info(f"Milestone reached for {inviter_id}. Sending a message.")
                first_name = self.invite_counts[inviter_id]['first_name']
                balance = invite_count * 50
                remaining = max(200 - invite_count, 0)

                if invite_count >= 200:
                    message = (
                        f"Congratulations 👏👏🎉\n\n"
                        f"📊 Milestone Achieved: @Digital_Birri\n"
                        f"-----------------------\n"
                        f"👤 User: {first_name}\n"
                        f"👥 Invites: Nama {invite_count} afeertaniittu\n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                        f"-----------------------\n\n"
                        f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
                    )
                    buttons = [[InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]]
                else:
                    message = (
                        f"📊 Invite Progress: @Digital_Birri\n"
                        f"-----------------------\n"
                        f"👤 User: {first_name}\n"
                        f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                        f"-----------------------\n\n"
                        f"Add gochuun carraa badhaasaa keessan dabalaa!"
                    )
                    buttons = [[InlineKeyboardButton("Check", callback_data=f"check_{inviter_id}")]]
                
                await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    def run(self):
        app = Application.builder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))

        logger.info("Bot is running...")
        app.run_polling()

if __name__ == "__main__":
    TOKEN = "7726783785:AAHWRISAiUfcvc67hrxE1RZCjxLkGUwaTxo"
    bot = TelegramBot(TOKEN)
    bot.run()
