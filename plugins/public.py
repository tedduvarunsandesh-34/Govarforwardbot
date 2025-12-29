# Jishu Developer 
# Patched for Manual ID Entry

import asyncio
from .utils import STS
from database import db
from config import temp
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardRemove
)

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    user_id = message.from_user.id
    
    # 1. Check Bot
    _bot = await db.get_bot(user_id)
    if not _bot:
        return await message.reply("Please add a bot in /settings first.")

    # 2. Ask for Source Chat ID
    src_msg = await bot.ask(message.chat.id, "⬇️ **Enter the Source Chat ID:**\n(Example: `-100123456789` or `username`)", filters=filters.text)
    if src_msg.text.startswith("/"): return await message.reply("Cancelled.")
    source_chat = src_msg.text

    # 3. Ask for Destination Chat ID
    dest_msg = await bot.ask(message.chat.id, "⬆️ **Enter the Destination Chat ID:**\n(Example: `-100987654321` or `my_channel`)", filters=filters.text)
    if dest_msg.text.startswith("/"): return await message.reply("Cancelled.")
    destination_chat = dest_msg.text

    # 4. Ask for Start Message ID (Skip)
    skip_msg = await bot.ask(message.chat.id, "🔢 **Enter the Start Message ID:**\n(From which message do you want to start?)", filters=filters.text)
    if not skip_msg.text.isdigit(): return await message.reply("Invalid ID. Must be a number.")
    start_id = int(skip_msg.text)

    # 5. Ask for Total Limit
    limit_msg = await bot.ask(message.chat.id, "🛑 **How many messages to forward?**\n(Enter a number, e.g., `500`)", filters=filters.text)
    if not limit_msg.text.isdigit(): return await message.reply("Invalid Limit.")
    limit = int(limit_msg.text)

    # 6. Store Data and Show Mode Selection
    forward_id = f"{user_id}-{message.id}"
    STS(forward_id).store(source_chat, destination_chat, start_id, limit)

    buttons = [
        [
            InlineKeyboardButton("⚡ Single Mode", callback_data=f"mode_single_{forward_id}"),
            InlineKeyboardButton("📦 Batch Mode", callback_data=f"mode_batch_{forward_id}")
        ],
        [InlineKeyboardButton("✖️ Cancel", callback_data="close_btn")]
    ]

    await message.reply_text(
        f"📋 **Forwarding Setup**\n\n"
        f"FROM: `{source_chat}`\n"
        f"TO: `{destination_chat}`\n"
        f"START ID: `{start_id}`\n"
        f"LIMIT: `{limit}`\n\n"
        "Select your mode to set speed:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
