# Jishu Developer 
# Patched public.py

import re
import asyncio
from .utils import STS
from database import db
from config import temp
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChannelPrivate
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
        return await message.reply("Add a Bot in /settings first!")

    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply_text("Set a To Channel in /settings first!")

    if len(channels) > 1:
        buttons = [[KeyboardButton(c['title'])] for c in channels]
        buttons.append([KeyboardButton("cancel")])
        _toid = await bot.ask(message.chat.id, Translation.TO_MSG.format(_bot['name'], _bot['username']),
                             reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
        
        if _toid.text.lower() == 'cancel':
            return await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())
        
        target = next((c for c in channels if c['title'] == _toid.text), None)
        if not target: return await message.reply_text("Wrong Channel!")
        toid, to_title = target['chat_id'], target['title']
    else:
        toid, to_title = channels[0]['chat_id'], channels[0]['title']

    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'): return

    if fromid.text and not fromid.forward_date:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match: return await message.reply('Invalid Link')
        chat_id = int("-100" + match.group(4)) if match.group(4).isnumeric() else match.group(4)
        last_msg_id = int(match.group(5))
    elif fromid.forward_from_chat:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.id
    else: return await message.reply("Invalid Source!")

    try:
        title = (await bot.get_chat(chat_id)).title
    except: title = "Source Chat"

    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    forward_id = f"{user_id}-{skipno.id}"
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id))

    buttons = [
        [InlineKeyboardButton("⚡ One By One", callback_data=f"mode_single_{forward_id}"),
         InlineKeyboardButton("📦 Batch Mode", callback_data=f"mode_batch_{forward_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="close_btn")]
    ]
    await message.reply_text(Translation.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text), reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^mode_"))
async def set_mode(bot, q):
    _, mode, fid = q.data.split("_")
    sts = STS(fid)
    sts.set("mode", mode)
    await q.message.edit_text("<b>Choose speed:</b>", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("50 / 5s", f"speed_{fid}_50_5"),
         InlineKeyboardButton("100 / 10s", f"speed_{fid}_100_10"),
         InlineKeyboardButton("200 / 20s", f"speed_{fid}_200_20")],
        [InlineKeyboardButton("▶ Start", f"start_public_{fid}")]
    ]))

@Client.on_callback_query(filters.regex("^speed_"))
async def set_speed(bot, q):
    _, fid, size, delay = q.data.split("_")
    sts = STS(fid)
    sts.set("batch_size", int(size))
    sts.set("batch_delay", int(delay))
    await q.answer(f"Speed set to {size} per {delay}s", show_alert=True)
