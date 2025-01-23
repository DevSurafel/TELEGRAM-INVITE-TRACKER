import os
import logging
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram.enums import ChatEventAction
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables for Telegram API
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Pyrogram client with bot token for handling bot-specific features if needed
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

invite_counts: Dict[int, Dict[str, int]] = {}

@app.on_message(enums.ChatAction.NEW_CHAT_MEMBERS)
async def new_member_handler(client: Client, message: Message):
    """
    Handler for when a new member joins the group. 
    This function checks the chat event log for the action that led to this join.
    """
    chat_id = message.chat.id
    for new_member in message.new_chat_members:
        events = await client.get_chat_event_log(
            chat_id=chat_id,
            query="",
            # Here, we use enums.ChatEventFilter instead of ChatEventLogFilters
            filters=enums.ChatEventFilter.GROUP_INFO,
            max_date=message.date
        )
        
        for event in events:
            if event.action == ChatEventAction.MEMBER_INVITED:
                inviter_id = event.from_user.id  # Changed from event.user.id to event.from_user.id
                if inviter_id not in invite_counts:
                    invite_counts[inviter_id] = {
                        'invite_count': 0,
                        'first_name': event.from_user.first_name,
                        'withdrawal_key': None
                    }
                invite_counts[inviter_id]['invite_count'] += 1
                invite_count = invite_counts[inviter_id]['invite_count']
                first_name = invite_counts[inviter_id]['first_name']
                balance = invite_count * 50
                remaining = max(4 - invite_count, 0)

                if invite_count % 2 == 0:
                    if invite_count >= 4:
                        message_text = (
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
                        message_text = (
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
                            [InlineKeyboardButton("Check", callback_data=f"check_{inviter_id}")]
                        ]

                    await client.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                break

@app.on_message(filters.command("invitecount"))
async def get_invite_count(client: Client, message: Message):
    """Command to check one's invite count."""
    user_id = message.from_user.id
    if user_id in invite_counts:
        invite_count = invite_counts[user_id]['invite_count']
        first_name = invite_counts[user_id]['first_name']
        balance = invite_count * 50
        remaining = max(4 - invite_count, 0)
        
        message_text = (
            f"📊 Invite Progress: @DIGITAL_BIRRI\n"
            f"-----------------------\n"
            f"👤 User: {first_name}\n"
            f"👥 Invites: Nama {invite_count} afeertaniittu \n"
            f"💰 Balance: {balance} ETB\n"
            f"🚀 Baafachuuf: Dabalataan nama {remaining} afeeraa\n"
            f"-----------------------\n\n"
            f"Add gochuun carraa badhaasaa keessan dabalaa!"
        )
        await message.reply_text(message_text)
    else:
        await message.reply_text("You haven't invited anyone yet.")

if __name__ == "__main__":
    app.run()
