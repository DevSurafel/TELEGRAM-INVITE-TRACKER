import os
import logging
import random
from typing import Dict, Any
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.error import NetworkError, TimedOut, RetryAfter

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, Any]] = {}
        self.group_migration_map: Dict[int, int] = {}
        self.retry_count = 0
        self.max_retries = 5

    async def safe_send_message(self, update: Update, message: str, buttons: list = None):
        """
        Safely send message with built-in error handling
        """
        try:
            reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
            await update.message.reply_text(message, reply_markup=reply_markup)
        except (NetworkError, TimedOut) as e:
            logger.error(f"Network error while sending message: {e}")
            await asyncio.sleep(2)  # Wait before retrying
        except Exception as e:
            logger.error(f"Unexpected error in message sending: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        
        # Initialize user if not exists
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None
            }
        
        invite_count = self.invite_counts[user.id]['invite_count']
        first_name = self.invite_counts[user.id]['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        buttons = [
            [
                InlineKeyboardButton("Check", callback_data=f"check_{user.id}"),
                InlineKeyboardButton("Key🔑", callback_data=f"key_{user.id}")
            ]
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

        await self.safe_send_message(update, message, buttons)

    async def track_group_migration(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Robust group migration tracking"""
        migrate_from_chat_id = update.message.migrate_from_chat_id
        migrate_to_chat_id = update.message.chat_id

        if migrate_from_chat_id and migrate_to_chat_id:
            self.group_migration_map[migrate_from_chat_id] = migrate_to_chat_id
            logger.info(f"Group migrated: {migrate_from_chat_id} -> {migrate_to_chat_id}")

    async def track_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            for new_member in update.message.new_chat_members:
                inviter = update.message.from_user
                
                # Skip self-join
                if inviter.id == new_member.id:
                    continue
                
                # Initialize inviter if not exists
                if inviter.id not in self.invite_counts:
                    self.invite_counts[inviter.id] = {
                        'invite_count': 0,
                        'first_name': inviter.first_name,
                        'withdrawal_key': None
                    }
                
                # Increment invite count
                self.invite_counts[inviter.id]['invite_count'] += 1
                invite_count = self.invite_counts[inviter.id]['invite_count']

                # Periodic notification
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

                    await self.safe_send_message(update, message, buttons)

        except Exception as e:
            logger.error(f"Error tracking new member: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()  # Always acknowledge the query
        
        try:
            user_id = int(query.data.split('_')[1])
            
            if user_id not in self.invite_counts:
                await query.answer("No invitation data found.")
                return

            user_data = self.invite_counts[user_id]
            invite_count = user_data['invite_count']
            first_name = user_data['first_name']
            balance = invite_count * 50
            remaining = max(200 - invite_count, 0)

            await query.answer(
                f"Kabajamoo {first_name}, maallaqa baafachuuf dabalataan nama {remaining} afeeruu qabdu", 
                show_alert=True
            )

        except Exception as e:
            logger.error(f"Error in handle_check: {e}")
            await query.answer("An unexpected error occurred.", show_alert=True)

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()  # Always acknowledge the query
        
        try:
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
                await query.answer(
                    f"Kabajamoo {first_name}, Lakkoofsi Key🔑 keessanii: 👉{withdrawal_key}", 
                    show_alert=True
                )
            else:
                await query.answer(
                    f"Kabajamoo {first_name}, lakkoofsa Key argachuuf yoo xiqqaate nama 200 afeeruu qabdu!", 
                    show_alert=True
                )

        except Exception as e:
            logger.error(f"Error in handle_key: {e}")
            await query.answer("An unexpected error occurred.", show_alert=True)

    async def start_bot(self):
        """
        Robust bot startup with retry mechanism
        """
        while self.retry_count < self.max_retries:
            try:
                application = Application.builder().token(self.token).build()

                # Add handlers
                application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, self.track_group_migration))
                application.add_handler(CommandHandler("start", self.start))
                application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.track_new_member))
                application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
                application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))

                logger.info("Bot started successfully!")
                
                # Run with additional error handling
                await application.run_polling(
                    drop_pending_updates=True,
                    stop_on_sigint=False,
                    stop_on_sigterm=False,
                    timeout=100,  # Extended timeout
                    read_timeout=10,
                    connect_timeout=15
                )
                
                break  # Exit loop if successful
            
            except RetryAfter as retry_error:
                wait_seconds = retry_error.retry_after
                logger.warning(f"Rate limited. Waiting {wait_seconds} seconds.")
                await asyncio.sleep(wait_seconds)
                self.retry_count += 1
            
            except Exception as e:
                logger.error(f"Bot startup error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                self.retry_count += 1

        if self.retry_count >= self.max_retries:
            logger.critical("Failed to start bot after multiple attempts")

@app.route('/')
def index():
    return "Bot is running!"

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)

    # Use asyncio to run the bot and flask app
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start_bot())
    
    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == "__main__":
    main()
