# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Developer @JishuDeveloper

import math
import time
import asyncio 
import logging
from .utils import STS
from database import db 
from .test import CLIENT , start_clone_bot
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    
    if temp.lock.get(user):
        return await message.answer("Please Wait Until Previous Task Completes", show_alert=True)
    
    sts = STS(frwd_id)
    if not sts.verify():
        return await message.answer("Old Button / Session Expired", show_alert=True)
      
    i = sts.get(full=True)
    if i.TO in temp.IS_FRWD_CHAT:
        return await message.answer("Task already in progress for this Target Chat.", show_alert=True)

    # Fetch User Choices from STS
    batch_limit = sts.get("batch_size") or 100
    batch_delay = sts.get("batch_delay") or 10
    mode = sts.get("mode") or "batch"

    m = await message.message.edit("Verifying Data, Please Wait...")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
    
    try:
        client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:  
        return await m.edit(f"Bot Error: {e}")

    temp.forwardings += 1
    await db.add_frwd(user)
    sts.add(time=True)
    
    individual_delay = 1 if _bot['is_bot'] else 5 
    
    temp.IS_FRWD_CHAT.append(i.TO)
    temp.lock[user] = True
    
    try:
        MSG = []
        pling = 0
        batch_counter = 0 
        
        async for msg in client.iter_messages(
            client,
            chat_id=i.FROM, 
            limit=int(i.limit), 
            offset=sts.get_last()
        ):
            if temp.CANCEL.get(user):
                break
            
            sts.save_last(msg.id) # Auto-resume tracker
            if pling % 20 == 0: 
                await edit(m, 'Progressing', 10, sts)
            pling += 1
            sts.add('fetched')

            if mode == "batch" and batch_counter >= batch_limit:
                await edit(m, 'Sleeping', batch_sleep, sts)
                await asyncio.sleep(batch_sleep)
                batch_counter = 0

            if msg.empty or msg.service:
                sts.add('deleted')
                continue

            if forward_tag:
                MSG.append(msg.id)
                if len(MSG) >= batch_limit or (int(i.limit) - pling) <= 0: 
                    await forward(client, MSG, m, sts, protect)
                    sts.add('total_files', len(MSG))
                    await asyncio.sleep(batch_sleep)
                    MSG = []
                    batch_counter = 0
            else:
                await copy(client, {"msg_id": msg.id, "media": media(msg), "caption": custom_caption(msg, caption), 'button': button, "protect": protect}, m, sts)
                sts.add('total_files')
                batch_counter += 1
                await asyncio.sleep(individual_delay) 

    except Exception as e:
        await m.edit(f"<b>Stopped with Error:</b>\n<code>{e}</code>")
        
    temp.IS_FRWD_CHAT.remove(i.TO)
    temp.lock[user] = False
    await edit(m, 'Completed', "completed", sts) 
    await client.stop()

# ================= HELPER FUNCTIONS ================= #

async def copy(bot, msg, m, sts):
    try:                                  
        if msg.get("media") and msg.get("caption"):
            await bot.send_cached_media(chat_id=sts.get('TO'), file_id=msg.get("media"), 
                                        caption=msg.get("caption"), reply_markup=msg.get('button'), 
                                        protect_content=msg.get("protect"))
        else:
            await bot.copy_message(chat_id=sts.get('TO'), from_chat_id=sts.get('FROM'),    
                                   caption=msg.get("caption"), message_id=msg.get("msg_id"), 
                                   reply_markup=msg.get('button'), protect_content=msg.get("protect"))
    except FloodWait as e:
        await edit(m, 'FloodWait', e.value, sts)
        await asyncio.sleep(e.value)
        await copy(bot, msg, m, sts)
    except Exception:
        sts.add('deleted')
        
async def forward(bot, msg, m, sts, protect):
    try:                             
        await bot.forward_messages(chat_id=sts.get('TO'), from_chat_id=sts.get('FROM'), 
                                   protect_content=protect, message_ids=msg)
    except FloodWait as e:
        await edit(m, 'FloodWait', e.value, sts)
        await asyncio.sleep(e.value)
        await forward(bot, msg, m, sts, protect)

async def edit(msg, title, status, sts):
    i = sts.get(full=True)
    status_text = 'Forwarding' if status == 10 else f"Sleeping {status}s" if str(status).isnumeric() else status
    percentage_raw = float(i.fetched)*100/float(i.total)
    percentage = "{:.0f}".format(percentage_raw)
    
    now = time.time()
    speed = sts.divide(i.fetched, int(now - i.start))
    eta = Translation.TimeFormatter(milliseconds=round(sts.divide(i.total - i.fetched, int(speed))) * 1000)
    
    # Corrected indentation for Material You Progress Bar
    bar = f"<b>{'━' * math.floor(percentage_raw/6.6)}{'─' * (15 - math.floor(percentage_raw/6.6))}</b>"

    text = Translation.TEXT.format(i.fetched, i.total_files, i.duplicate, i.deleted, i.total, status_text, percentage, eta, bar)
    
    try:
        await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"◈ {title} ◈", "status")]]))
    except MessageNotModified:
        pass

def media(msg):
    if msg.media:
        media_obj = getattr(msg, msg.media.value, None)
        if media_obj:
            return getattr(media_obj, 'file_id', None)
    return None 

def custom_caption(msg, caption):
    if msg.media:
        if (msg.video or msg.document or msg.audio or msg.photo):
            media_obj = getattr(msg, msg.media.value, None)
            if media_obj:
                file_name = getattr(media_obj, 'file_name', '')
                file_size = getattr(media_obj, 'file_size', '')
                fcaption = getattr(msg, 'caption', '')
                if fcaption:
                    fcaption = fcaption.html
                if caption:
                    return caption.format(filename=file_name, size=get_size(file_size), caption=fcaption)
                return fcaption
    return None

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    idx = 0
    while size >= 1024.0 and idx < len(units):
        idx += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[idx])
