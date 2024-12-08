import os
import logging
import random
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes, ChatMemberHandler
)
import asyncio

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts = {}
        self.invited_members = set()  # Tracks unique invited members

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user

        # Initialize user data
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                "invite_count": 0,
                "first_name": user.first_name,
                "withdrawal_key": None
            }

        invite_count = self.invite_counts[user.id]["invite_count"]
        first_name = self.invite_counts[user.id]["first_name"]
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        # Generate message and buttons
        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
        ]

        if invite_count >= 200:
            message = (
                f"Congratulations 👏👏🎉\n\n"
                f"📊 Milestone Achieved: @Digital_Birri\n"
                f"-----------------------\n"
                f"👤 User: {first_name}\n"
                f"👥 Invites: Nama {invite_count} afeertaniittu! \n"
                f"💰 Balance: {balance} ETB\n"
                f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                f"-----------------------\n\n"
                f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
            )
            buttons.append([InlineKeyboardButton("Withdrawal Request", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
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

        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.new_chat_members:  # Check if there are new chat members
            for new_member in update.message.new_chat_members:
                inviter = update.message.from_user
                await self.handle_member_invitation(new_member, inviter)

    async def handle_member_invitation(self, new_member, inviter):
        if new_member.id == context.bot.id or new_member.id in self.invited_members or inviter.id == new_member.id:
            return

        if inviter.id not in self.invite_counts:
            self.invite_counts[inviter.id] = {
                "invite_count": 0,
                "first_name": inviter.first_name,
                "withdrawal_key": None
            }

        self.invite_counts[inviter.id]["invite_count"] += 1
        self.invited_members.add(new_member.id)

        await self.send_invite_update(inviter.id)

    async def send_invite_update(self, inviter_id):
        invite_count = self.invite_counts[inviter_id]["invite_count"]
        first_name = self.invite_counts[inviter_id]["first_name"]
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        if invite_count % 10 == 0:  # Example milestone tracking
            if invite_count >= 200:
                # Congratulations message
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
                buttons = [[InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Bir_Bot?start=ar6222905852")]]
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

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Updates related to chat members."""
        new_member = update.chat_member.new_chat_member
        if new_member.status == "member":
            inviter = update.chat_member.from_user  # The user who invited the new member
            await self.handle_member_invitation(new_member, inviter)

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data["invite_count"]
        first_name = user_data["first_name"]
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        await query.answer(
            f"Kabajamoo {first_name}, maallaqa baafachuuf dabalataan nama {remaining} afeeruu qabdu", 
            show_alert=True
        )

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data["invite_count"]
        first_name = user_data["first_name"]

        if invite_count >= 200:
            if not user_data["withdrawal_key"]:
                user_data["withdrawal_key"] = random.randint(100000, 999999)
            await query.answer(
                f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{user_data['withdrawal_key']}", 
                show_alert=True
            )
        else:
            await query.answer(
                f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", 
                show_alert=True
            )

    def run(self):
        application = Application.builder().token(self.token).build()

        # Register handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
        application.add_handler(ChatMemberHandler(self.handle_chat_member_update))  # Added handler for chat member updates
        application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r"^check_\d+$"))
        application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r"^key_\d+$"))

        logger.info("Bot started successfully!")
        asyncio.get_event_loop().run_until_complete(application.run_polling(drop_pending_updates=True))

# Flask route
@app.route("/")
def index():
    return "Bot is running!"

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(token)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    main()
