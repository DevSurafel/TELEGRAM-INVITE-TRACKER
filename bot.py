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

import nest_asyncio
nest_asyncio.apply()  # This allows for nested event loops

# Configure logging
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
        self.user_max_numbers: Dict[int, int] = {}  # Track the largest number posted by each user

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
                f'<a href="https://t.me/PAWSOG_bot/PAWS?startapp=tekHndQ1">'
                f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁\n"
                f"🎁🎁🎁 10,000 ETB 🎁🎁🎁🎁\n"
                f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁</a>\n\n"
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
                f'<a href="https://t.me/PAWSOG_bot/PAWS?startapp=tekHndQ1">'
                f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁\n"
                f"🎁🎁🎁 10,000 ETB 🎁🎁🎁🎁\n"
                f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁</a>\n\n"
                f"Add gochuun carraa badhaasaa keessan dabalaa!"
            )
        
        await update.message.reply_text(
            f"{message}\n\nCode'n keessan: {unique_id}", 
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True  # This prevents URL preview but keeps it clickable
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
        user = update.message.from_user
        text = update.message.text

        # Extract numbers from the message
        numbers = re.findall(r'\d+', text)
        if not numbers:
            # Show "typing..." before replying
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
            await asyncio.sleep(2)  # Simulate typing delay

            # Randomly select one of the five statements
            responses = [
                "Maaloo baayyina waliigala nama afeertanii barreessaa! ",
                "Maaloo baayyina waliigalaa afeertan nuuf barreessaa!",
                "Waliigalatti nama meeqa afeertanii jirtu?"
            ]
            response = random.choice(responses)
            await update.message.reply_text(response)
            return

        # Use the first number found
        number = int(numbers[0])

        # Ignore numbers greater than 500
        if number > 500:
            return

        # Ensure user is registered before proceeding
        if user.id not in self.invite_counts:
            self.invite_counts[user.id] = {
                'invite_count': 0,
                'first_name': user.first_name,
                'withdrawal_key': None,
                'user_id': user.id
            }

        # Track the largest number posted by the user
        if user.id not in self.user_max_numbers:
            self.user_max_numbers[user.id] = number
        elif number > self.user_max_numbers[user.id]:
            self.user_max_numbers[user.id] = number

        # Always show "processing" before replying
        processing_message = await update.message.reply_text("📊 Calculating your invite progress... Please wait...")

        # Add a random delay (1 to 5 seconds)
        delay = random.randint(1, 5)
        await asyncio.sleep(delay)

        # Delete the "processing" message
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=processing_message.message_id)

        # If the number is smaller, just reply with the current status
        if number < self.user_max_numbers[user.id]:
            unique_id = self.generate_unique_id(user.id)
            await self.send_invite_info(update, self.invite_counts[user.id], unique_id)
            return

        # Use the largest number posted by the user for calculations
        current_number = self.user_max_numbers[user.id]
        previous_count = self.invite_counts[user.id]['invite_count']

        # Randomize the subtraction value (between 100 and 150)
        subtract_value = random.randint(100, 150)

        # Ensure the new count is never less than the previous count
        new_invite_count = max(previous_count, current_number - subtract_value)

        # Update invite count 
        self.invite_counts[user.id]['invite_count'] = new_invite_count

        # Send updated invite info
        unique_id = self.generate_unique_id(user.id)
        await self.send_invite_info(update, self.invite_counts[user.id], unique_id)

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
            f"📊 Invite Progress: @DIGITAL_BIRRI\n"
            f"-----------------------\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
            f"-----------------------\n\n"
            f'<a href="https://t.me/PAWSOG_bot/PAWS?startapp=tekHndQ1">'
            f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁\n"
            f"🎁🎁🎁 10,000 ETB 🎁🎁🎁🎁\n"
            f"🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁🎁</a>\n\n"
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

    async def handle_cancel_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        if 'new_member_id' in context.user_data:
            del context.user_data['new_member_id']
        await query.edit_message_text("ID submission cancelled.")

    async def handle_send_invite_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message.text.split()
        
        if len(message) != 2:
            await update.message.reply_text("Baayyina nama afeertanii baruuf \n\n 👉/start@Invite_birr_bot \n")
            return

        inviter_id = message[1].upper()  # Convert to uppercase to match the IDs format

        if user.id not in self.invite_counts:
            await update.message.reply_text("You must be registered to submit an inviter's ID.")
            return
        
        if 'inviter_id' in self.invite_counts[user.id]:
            await update.message.reply_text("Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n 👉/start")
            return

        for inviter_user_id, unique_id in self.user_unique_ids.items():
            if unique_id == inviter_id:
                self.invite_counts[inviter_user_id]['invite_count'] += 1
                self.invite_counts[user.id]['inviter_id'] = inviter_user_id
                await update.message.reply_text(f"Milkaa'inaan galchitanii jirtu. Nama isin afeereef 50 ETB dabalameera! \n\n  👉/start")
                return
        
        await update.message.reply_text("Baayyina nama afeertanii baruuf \n\n 👉/start@Invite_birr_bot \n")

    async def run(self):
        try:
            application = Application.builder().token(self.token).build()

            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_number_message))  # Listen for text messages
            application.add_handler(CallbackQueryHandler(self.handle_check, pattern=r'^check_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_key, pattern=r'^key_\d+$'))
            application.add_handler(CallbackQueryHandler(self.handle_cancel_id, pattern='^cancel_id$'))
            application.add_handler(CommandHandler("send_invite_code", self.handle_send_invite_code))

            logger.info("Bot started successfully!")

            # Run the bot
            await application.run_polling(drop_pending_updates=True)

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise  # Re-raise the exception to ensure it's logged properly

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = InviteTrackerBot(TOKEN)
    
    # Get the current event loop
    loop = asyncio.get_event_loop()

    try:
        # Run the bot
        loop.run_until_complete(bot.run())
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    
    # No need to explicitly close the loop here, let Python handle it

if __name__ == "__main__":
    main()
