import os
import logging
import random
from typing import Dict, Any, Set
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

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
        self.invite_counts: Dict[int, Dict[str, Any]] = {}
        self.group_member_cache: Dict[int, Set[int]] = {}  # New cache to track members per group

    async def get_full_member_list(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> Set[int]:
        """
        Retrieve full member list with pagination and error handling
        """
        try:
            # Use getChatMemberCount first to check total members
            total_members = await context.bot.get_chat_member_count(chat_id)
            logger.info(f"Total members in group: {total_members}")

            # Initialize member set
            members = set()

            # Paginate through members (Telegram typically allows 200 members per request)
            offset = 0
            while offset < total_members:
                try:
                    chat_members = await context.bot.get_chat_members(
                        chat_id, 
                        offset=offset, 
                        limit=200  # Maximum allowed by Telegram API
                    )
                    
                    # Add member IDs to the set
                    members.update(member.user.id for member in chat_members)
                    
                    offset += 200
                    if len(chat_members) < 200:
                        break
                except Exception as page_error:
                    logger.error(f"Error fetching members page: {page_error}")
                    break

            logger.info(f"Successfully retrieved {len(members)} members")
            return members

        except Exception as e:
            logger.error(f"Error retrieving full member list: {e}")
            return set()

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
        remaining = max(200 - invite_count, 0)

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
        chat_id = update.message.chat_id

        # Initialize group cache if not exists
        if chat_id not in self.group_member_cache:
            self.group_member_cache[chat_id] = await self.get_full_member_list(context, chat_id)

        for new_member in update.message.new_chat_members:
            try:
                # Verify if the new member is actually a new addition to the group
                if new_member.id not in self.group_member_cache[chat_id]:
                    self.group_member_cache[chat_id].add(new_member.id)

                    inviter = update.message.from_user
                    if inviter.id == new_member.id:
                        continue
                    if inviter.id not in self.invite_counts:
                        self.invite_counts[inviter.id] = {
                            'invite_count': 0,
                            'first_name': inviter.first_name,
                            'withdrawal_key': None
                        }
                    self.invite_counts[inviter.id]['invite_count'] += 1
                    invite_count = self.invite_counts[inviter.id]['invite_count']

                    if invite_count % 10 == 0:
                        first_name = self.invite_counts[inviter.id]['first_name']
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
                            buttons = [
                                [InlineKeyboardButton("Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")]
                            ]
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
                            buttons = [
                                [InlineKeyboardButton("Check", callback_data=f"check_{inviter.id}")]
                            ]

                        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))

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
        remaining = max(200 - invite_count, 0)

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

        await query.answer(f"Kabajamoo {first_name}, maallaqa baafachuuf dabalataan nama {remaining} afeeruu qabdu", show_alert=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])

        if user_id not in self.invite_counts:
            await query.answer("No invitation data found.")
            return

        user_data = self.invite_counts[user_id]
        invite_count = user_data['invite_count']
        first_name = user_data['first_name']

        if invite_count >= 200:
            if not user_data['withdrawal_key']:
                user_data['withdrawal_key'] = random.randint(100000, 999999)
            withdrawal_key = user_data['withdrawal_key']
            await query.answer(f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{withdrawal_key}", show_alert=True)
        else:
            await query.answer(f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", show_alert=True)

    def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

            logger.info("Bot started successfully!")

            # Run the bot asynchronously, using asyncio.run() in a blocking way
            asyncio.get_event_loop().run_until_complete(application.run_polling(drop_pending_updates=True))

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

# Web server to keep the service running on Render
@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)

    # Run the bot and the Flask app in the same event loop
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run())  # Start the bot as a background task

    # Start the Flask app (it will run in the main thread)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
