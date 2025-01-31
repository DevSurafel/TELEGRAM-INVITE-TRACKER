import os
import logging
import random
import re
from typing import Dict
import asyncio
from dotenv import load_dotenv
load_dotenv()
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class InviteTrackerBot:
    def __init__(self, token: str):
        self.token = token
        self.invite_counts: Dict[int, Dict[str, int]] = {}
        self.user_unique_ids: Dict[int, str] = {}
        self.user_max_numbers: Dict[int, int] = {}
        self.user_progress_tasks: Dict[int, asyncio.Task] = {}
        self.application = None
        self.is_running = False

    def generate_unique_id(self, user_id: int) -> str:
        if user_id not in self.user_unique_ids:
            unique_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            self.user_unique_ids[user_id] = unique_id
        return self.user_unique_ids[user_id]

    async def send_invite_info(self, update: Update, user: Dict[int, str], unique_id: str):
        invite_count = user['invite_count']
        buttons = [
            [InlineKeyboardButton("Check", callback_data=f"check_{user['user_id']}"),
             InlineKeyboardButton("Key🔑", callback_data=f"key_{user['user_id']}")]
        ]

        first_name = user['first_name']
        balance = invite_count * 50
        remaining = max(200 - invite_count, 0)

        if invite_count >= 200:
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
            buttons.append([InlineKeyboardButton("👉Baafachuuf", url="https://t.me/Digital_Birr_Bot?start=ar6222905852")])
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
        
        await update.message.reply_text(
            f"{message}\n\nCode'n keessan: {unique_id}", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None,
                'user_id': user.id
            }
        unique_id = self.generate_unique_id(user.id)
        await self.send_invite_info(update, self.invite_counts[user.id], unique_id)

    async def handle_number_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            user = update.message.from_user
            text = update.message.text

            numbers = re.findall(r'\d+', text)
            if not numbers:
                return

            number = int(numbers[0])
            if number > 500:
                return

            if user.id not in self.user_max_numbers or number > self.user_max_numbers[user.id]:
                self.user_max_numbers[user.id] = number

            largest_number = self.user_max_numbers[user.id]
            subtract_value = random.randint(100, 200)
            fake_invite_count = max(largest_number - subtract_value, 0)

            processing_message = await update.message.reply_text(
                "📊 Calculating your invite progress... Please wait..."
            )

            delay = random.randint(1, 5)
            await asyncio.sleep(delay)

            await context.bot.delete_message(
                chat_id=update.message.chat_id,
                message_id=processing_message.message_id
            )

            if user.id in self.user_progress_tasks:
                self.user_progress_tasks[user.id].cancel()

            self.user_progress_tasks[user.id] = asyncio.create_task(
                self.simulate_progress(update, user.id, fake_invite_count)
            )

        except Exception as e:
            logger.error(f"Error in handle_number_message: {e}")

    async def simulate_progress(self, update: Update, user_id: int, target_invites: int):
        try:
            if user_id not in self.invite_counts:
                self.invite_counts[user_id] = {
                    'invite_count': 0,
                    'first_name': update.message.from_user.first_name,
                    'withdrawal_key': None,
                    'user_id': user_id
                }

            current_invites = self.invite_counts[user_id]['invite_count']
            while current_invites < target_invites:
                current_invites += 10
                self.invite_counts[user_id]['invite_count'] = current_invites
                unique_id = self.generate_unique_id(user_id)
                await self.send_invite_info(update, self.invite_counts[user_id], unique_id)
                await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error in simulate_progress: {e}")

    async def handle_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            query = update.callback_query
            user_id = int(query.data.split('_')[1])

            if user_id not in self.invite_counts:
                await query.answer("No invitation data found.")
                return

            user_data = self.invite_counts[user_id]
            first_name = user_data['first_name']
            remaining = max(200 - user_data['invite_count'], 0)

            await query.answer(
                f"Kabajamoo {first_name}, maallaqa baafachuuf dabalataan nama {remaining} afeeruu qabdu",
                show_alert=True
            )

        except Exception as e:
            logger.error(f"Error in handle_check: {e}")

    async def handle_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
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

    async def handle_send_invite_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            user = update.effective_user
            message = update.message.text.split()
            
            if len(message) != 2:
                await update.message.reply_text(
                    "Code nama isin afeeree galchaa: \n\n /send_invite_code <Code> \n\n  👉/start"
                )
                return

            inviter_id = message[1].upper()

            if user.id not in self.invite_counts:
                await update.message.reply_text("You must be registered to submit an inviter's ID.")
                return
            
            if 'inviter_id' in self.invite_counts[user.id]:
                await update.message.reply_text(
                    "Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n 👉/start"
                )
                return

            for inviter_user_id, unique_id in self.user_unique_ids.items():
                if unique_id == inviter_id:
                    self.invite_counts[inviter_user_id]['invite_count'] += 1
                    self.invite_counts[user.id]['inviter_id'] = inviter_user_id
                    await update.message.reply_text(
                        "Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n  👉/start"
                    )
                    return
            
            await update.message.reply_text(
                "Code isin galchitan dogooggora. Irra deebi'uun galchaa. \n\n 👉/start"
            )

        except Exception as e:
            logger.error(f"Error in handle_send_invite_code: {e}")

    async def setup(self):
        """Initialize the application and add handlers"""
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_number_message))
            self.application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            self.application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))
            self.application.add_handler(CommandHandler("send_invite_code", self.handle_send_invite_code))

            await self.application.initialize()
            await self.application.start()
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error in setup: {e}")
            raise

    async def run(self):
        """Run the bot"""
        try:
            logger.info("Starting bot...")
            await self.setup()
            logger.info("Bot started successfully!")
            self.is_running = True
            
            await self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self.stop()
    
    async def stop(self):
        """Properly shutdown the bot"""
        try:
            if self.is_running and self.application:
                self.is_running = False
                await self.application.stop()
                await self.application.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    # Get token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    # Create bot instance
    bot = InviteTrackerBot(TOKEN)
    
    # Set up the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the bot
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping bot...")
        loop.run_until_complete(bot.stop())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        loop.run_until_complete(bot.stop())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
