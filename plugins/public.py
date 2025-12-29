# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import re
import asyncio
from .utils import STS
from database import db
from config import temp
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)

# =================== RUN =================== #

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id

    _bot = await db.get_bot(user_id)
    if not _bot:
        return await message.reply("You Did Not Added Any Bot. Please Add A Bot Using /settings !")

    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply_text("Please Set A To Channel In /settings Before Forwarding")

    if len(channels) > 1:
        for channel in channels:
            buttons.append([KeyboardButton(channel['title'])])
            btn_data[channel['title']] = channel['chat_id']
        buttons.append([KeyboardButton("cancel")])

        _toid = await bot.ask(
            message.chat.id,
            Translation.TO_MSG.format(_bot['name'], _bot['username']),
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        )

        if _toid.text.startswith(('/', 'cancel')):
            return await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())

        toid = btn_data.get(_toid.text)
        if not toid:
            return await message.reply_text("Wrong Channel Choosen !", reply_markup=ReplyKeyboardRemove())

        to_title = _toid.text
    else:
        toid = channels[0]['chat_id']
        to_title = channels[0]['title']

    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())

    if fromid.text and fromid.text.startswith('/'):
        return await message.reply(Translation.CANCEL)

    if fromid.text and not fromid.forward_date:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid Link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
    elif fromid.forward_from_chat.type in [enums.ChatType.CHANNEL]:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if not last_msg_id:
            return await message.reply_text("Invalid forwarded message")
    else:
        return await message.reply_text("Invalid !")

    try:
        title = (await bot.get_chat(chat_id)).title
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "private"
    except Exception as e:
        return await message.reply(f"Error: {e}")

    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    if skipno.text.startswith('/'):
        return await message.reply(Translation.CANCEL)

    forward_id = f"{user_id}-{skipno.id}"

    # Store job
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id))

    # Mode Selection
    buttons = [
        [
            InlineKeyboardButton("⚡ One By One", callback_data=f"mode_single_{forward_id}"),
            InlineKeyboardButton("📦 Batch Mode", callback_data=f"mode_batch_{forward_id}")
        ],
        [InlineKeyboardButton("❌ Cancel", "close_btn")]
    ]

    await message.reply_text(
        Translation.DOUBLE_CHECK.format(
            botname=_bot['name'],
            botuname=_bot['username'],
            from_chat=title,
            to_chat=to_title,
            skip=skipno.text
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ========== MODE SELECTION ========== #

@Client.on_callback_query(filters.regex("^mode_"))
async def set_mode(bot, q):
    _, mode, fid = q.data.split("_")
    sts = STS(fid)

    if not sts.verify():
        return await q.answer("Expired", show_alert=True)

    sts.set("mode", "single" if mode == "single" else "batch")

    await q.message.edit_text(
        "Choose speed:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("50 / 5s", f"speed_{fid}_50_5"),
                InlineKeyboardButton("100 / 10s", f"speed_{fid}_100_10"),
                InlineKeyboardButton("200 / 20s", f"speed_{fid}_200_20")
            ],
            [InlineKeyboardButton("▶ Start", f"start_public_{fid}")]
        ])
    )


# ========== SPEED ========== #

@Client.on_callback_query(filters.regex("^speed_"))
async def set_speed(bot, q):
    _, fid, size, delay = q.data.split("_")
    sts = STS(fid)
    sts.set("batch_size", int(size))
    sts.set("batch_delay", int(delay))
    await q.answer("Speed set")


# =================================== #
