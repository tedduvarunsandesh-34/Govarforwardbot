# Jishu Developer 
# Patched public.py

import re
import asyncio
from .utils import STS
from database import db
from config import temp
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
        return await message.reply("Add a bot in /settings first!")

    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply_text("Set a target channel in /settings!")

    # Multi-channel selection logic
    if len(channels) > 1:
        btn = [[KeyboardButton(c['title'])] for c in channels]
        btn.append([KeyboardButton("cancel")])
        _to = await bot.ask(message.chat.id, Translation.TO_MSG.format(_bot['name'], _bot['username']), 
                           reply_markup=ReplyKeyboardMarkup(btn, one_time_keyboard=True, resize_keyboard=True))
        if _to.text.lower() == "cancel": return await message.reply("Cancelled.", reply_markup=ReplyKeyboardRemove())
        target = next((c for c in channels if c['title'] == _to.text), None)
        toid, to_title = target['chat_id'], target['title']
    else:
        toid, to_title = channels[0]['chat_id'], channels[0]['title']

    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'): return

    # Link Parsing
    if fromid.text and not fromid.forward_date:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match: return await message.reply('Invalid Link')
        chat_id, last_msg_id = match.group(4), int(match.group(5))
        if chat_id.isnumeric(): chat_id = int("-100" + chat_id)
    elif fromid.forward_from_chat:
        last_msg_id, chat_id = fromid.forward_from_message_id, fromid.forward_from_chat.id
    else: return await message.reply("Invalid Source.")

    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    fid = f"{user_id}-{skipno.id}"
    STS(fid).store(chat_id, toid, int(skipno.text), int(last_msg_id))

    await message.reply_text(
        Translation.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat="Source", to_chat=to_title, skip=skipno.text),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Single", callback_data=f"mode_single_{fid}"),
             InlineKeyboardButton("📦 Batch", callback_data=f"mode_batch_{fid}")]
        ])
    )

@Client.on_callback_query(filters.regex("^mode_"))
async def set_mode(bot, q):
    _, mode, fid = q.data.split("_")
    sts = STS(fid)
    sts.set("mode", mode)
    await q.message.edit_text("<b>Select Speed:</b>", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("50/5s", f"speed_{fid}_50_5"),
         InlineKeyboardButton("100/10s", f"speed_{fid}_100_10"),
         InlineKeyboardButton("200/20s", f"speed_{fid}_200_20")],
        [InlineKeyboardButton("▶️ Start", f"start_public_{fid}")]
    ]))

@Client.on_callback_query(filters.regex("^speed_"))
async def set_speed(bot, q):
    _, fid, size, delay = q.data.split("_")
    sts = STS(fid)
    sts.set("batch_size", int(size))
    sts.set("batch_delay", int(delay))
    await q.answer(f"Speed: {size} msgs / {delay}s", show_alert=True)
