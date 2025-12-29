# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Developer @JishuDeveloper

import math
import time
import asyncio
from .utils import STS, get_readable_time
from database import db 
from .test import CLIENT, start_clone_bot
from config import temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user, frwd_id = message.from_user.id, message.data.split("_")[2]
    sts = STS(frwd_id)
    if not sts.verify(): return await message.answer("Session Expired")
    
    i = sts.get(full=True)
    batch_limit = sts.get("batch_size") or 100
    batch_sleep = sts.get("batch_delay") or 10
    mode = sts.get("mode") or "batch"

    m = await message.message.edit("Initializing...")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
    
    try:
        client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:
        return await m.edit(f"Error: {e}")

    temp.lock[user] = True
    temp.IS_FRWD_CHAT.append(i.TO)
    sts.add(time=True)

    try:
        batch_counter = 0
        MSG = []
        async for msg in client.iter_messages(client, chat_id=i.FROM, limit=int(i.limit), offset=sts.get_last()):
            if temp.CANCEL.get(user): break
            
            sts.save_last(msg.id)
            sts.add('fetched')

            if batch_counter % 20 == 0: 
                await edit(m, 'Progressing', 10, sts)

            if mode == "batch" and batch_counter >= batch_limit:
                await edit(m, 'Sleeping', batch_sleep, sts)
                await asyncio.sleep(batch_sleep)
                batch_counter = 0

            if msg.empty or msg.service:
                sts.add('deleted')
                continue

            if forward_tag:
                MSG.append(msg.id)
                if len(MSG) >= batch_limit:
                    await forward(client, MSG, m, sts, protect)
                    sts.add('total_files', len(MSG))
                    await asyncio.sleep(batch_sleep)
                    MSG, batch_counter = [], 0
            else:
                await copy(client, {"msg_id": msg.id, "media": media(msg), "caption": custom_caption(msg, caption), "button": button, "protect": protect}, m, sts)
                sts.add('total_files')
                batch_counter += 1
                await asyncio.sleep(1 if _bot['is_bot'] else 5)

    except Exception as e: 
        await m.edit(f"Stopped Error: {e}")

    temp.lock[user] = False
    temp.IS_FRWD_CHAT.remove(i.TO)
    await edit(m, 'Completed', "completed", sts)
    await client.stop()

async def edit(msg, title, status, sts):
    i = sts.get(full=True)
    perc = float(i.fetched)*100/float(i.total)
    bar = f"<b>{'━' * math.floor(perc/6.6)}{'─' * (15 - math.floor(perc/6.6))}</b>"
    now = time.time()
    speed = sts.divide(i.fetched, int(now - i.start))
    eta = get_readable_time(round(sts.divide(i.total - i.fetched, int(speed))))

    text = (
        f"<b>✨ Ultra Forwarding System</b>\n"
        f"<code>{bar}</code> <b>{int(perc)}%</b>\n\n"
        f"<b>📊 Progress Stats</b>\n"
        f" ├ <b>Processed:</b> <code>{i.fetched}</code> / <code>{i.total}</code>\n"
        f" ├ <b>Success:</b> <code>{i.total_files}</code>\n"
        f" ├ <b>Duplicates:</b> <code>{i.duplicate}</code>\n"
        f" └ <b>Deleted:</b> <code>{i.deleted}</code>\n\n"
        f"<b>🕒 Timing Details</b>\n"
        f" ├ <b>Status:</b> <code>{status if str(status).isalpha() else f'Sleeping {status}s'}</code>\n"
        f" └ <b>ETA:</b> <code>{eta}</code>"
    )

    try:
        await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"◈ {title} ◈", "status")]]))
    except MessageNotModified:
        pass

async def copy(bot, msg, m, sts):
    try:                                  
        if msg.get("media") and msg.get("caption"):
            await bot.send_cached_media(chat_id=sts.get('TO'), file_id=msg.get("media"), caption=msg.get("caption"), reply_markup=msg.get('button'), protect_content=msg.get("protect"))
        else:
            await bot.copy_message(chat_id=sts.get('TO'), from_chat_id=sts.get('FROM'), caption=msg.get("caption"), message_id=msg.get("msg_id"), reply_markup=msg.get('button'), protect_content=msg.get("protect"))
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await copy(bot, msg, m, sts)
    except Exception:
        sts.add('deleted')
        
async def forward(bot, msg, m, sts, protect):
    try:                             
        await bot.forward_messages(chat_id=sts.get('TO'), from_chat_id=sts.get('FROM'), protect_content=protect, message_ids=msg)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await forward(bot, msg, m, sts, protect)

def media(msg):
    if msg.media:
        obj = getattr(msg, msg.media.value, None)
        if obj: return getattr(obj, 'file_id', None)
    return None 

def custom_caption(msg, caption):
    if msg.media and (msg.video or msg.document or msg.audio or msg.photo):
        obj = getattr(msg, msg.media.value, None)
        if obj:
            fcap = getattr(msg, 'caption', '')
            if fcap: fcap = fcap.html
            if caption: return caption.format(filename=getattr(obj, 'file_name', ''), size=get_size(getattr(obj, 'file_size', '')), caption=fcap)
            return fcap
    return None

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size, idx = float(size), 0
    while size >= 1024.0 and idx < len(units):
        size /= 1024.0
        idx += 1
    return "%.2f %s" % (size, units[idx])
