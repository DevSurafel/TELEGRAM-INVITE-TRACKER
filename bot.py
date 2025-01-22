import os
import logging
import random
from typing import Dict
import asyncio
from flask import Flask
from telegram import Update, ChatMemberUpdated
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, ContextTypes
)
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)

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
        self.application = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            }
        invite_count = self.invite_counts[user.id]['invite_count']

        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")]
        ]

        first_name = self.invite_counts[user.id]['first_name']
        balance = invite_count * 50
        remaining = max(4 - invite_count, 0)

        if invite_count >= 4:
            message = (
                f"Congratulations 👏👏🎉\n\n"
                f"📊 Milestone Achieved: @DIGITAL_BIRRI\n"
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
                f"📊 Invite Progress: @DIGITAL_BIRRI\n"
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
        if update.effective_chat.id != self.supergroup_id:
            return

        chat_member_update = update.chat_member or update.my_chat_member
        if not chat_member_update:
            return

        new_member = chat_member_update.new_chat_member.user
        inviter = chat_member_update.from_user

        if (chat_member_update.new_chat_member.status == "member" and 
            chat_member_update.old_chat_member.status != "member" and 
            inviter.id != new_member.id):
            
            if inviter.id not in self.invite_counts:
                self.invite_counts[inviter.id] = {
                    'invite_count': 0,
                    'first_name': inviter.first_name,
                    'withdrawal_key': None
                }
            self.invite_counts[inviter.id]['invite_count'] += 1
            invite_count = self.invite_counts[inviter.id]['invite_count']

            if invite_count % 2 == 0:
                first_name = self.invite_counts[inviter.id]['first_name']
                balance = invite_count * 50
                remaining = max(4 - invite_count, 0)

                if invite_count >= 4:
                    message = (
                        f"Congratulations 👏👏🎉\n\n"
                        f"📊 Milestone Achieved: @DIGITAL_BIRRI\n"
                        f"-----------------------\n"
                        f"👤 User: {first_name}\n"
                        f"👥 Invites: Nama {invite_count} afeertaniittu\n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Baafachuuf: Baafachuu ni dandeessu! \n"
                        f"-----------------------\n\n"
                        f"Baafachuuf kan jedhu tuquun baafadhaa 👇"
                    )
                    buttons = [
                        [InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]
                    ]
                else:
                    message = (
                        f"📊 Invite Progress: @DIGITAL_BIRRI\n"
                        f"-----------------------\n"
                        f"👤 User: {first_name}\n"
                        f"👥 Invites: Nama {invite_count} afeertaniittu \n"
                        f"💰 Balance: {balance} ETB\n"
                        f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
                        f"-----------------------\n\n"
                        f"Add gochuun carraa badhaasaa keessan dabalaa!"
                    )
                    buttons = [
                        [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                    ]

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']
        remaining = max(4 - invite_count, 0)

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
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']

        if invite_count >= 4:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            await query.answer(
                f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{withdrawal_key}",
                show_alert=True
            )
        else:
            await query.answer(
                f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 4 afeeruu qabdu!",
                show_alert=True
            )

    async def initialize(self):
        self.application = Application.builder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(ChatMemberHandler(self.track_new_member, ChatMemberUpdated))
        self.application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
        self.application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"]
        )

    async def stop(self):
        if self.application:
            await self.application.stop()

async def run_bot():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    SUPERGROUP_ID = int(os.getenv('SUPERGROUP_ID'))
    
    if not TOKEN or not SUPERGROUP_ID:
        logger.error("Missing required environment variables")
        return
    
    bot = InviteTrackerBot(TOKEN, SUPERGROUP_ID)
    await bot.initialize()

@app.route('/')
def index():
    return "Bot is running!"

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(run_bot())
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
