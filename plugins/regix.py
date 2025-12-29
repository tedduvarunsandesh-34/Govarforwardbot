# Jishu Developer 
# Optimized for Speed and Stability

import math, time, asyncio
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

    m = await message.message.edit("🚀 **Initializing Engine...**")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
    
    try:
        client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:
        return await m.edit(f"❌ Error: {e}")

    temp.lock[user] = True
    temp.IS_FRWD_CHAT.append(i.TO)
    sts.add(time=True)

    try:
        batch_counter = 0
        MSG = []
        # Iterating messages based on manual IDs
        async for msg in client.iter_messages(client, chat_id=i.FROM, limit=int(i.limit), offset_id=int(i.skip)):
            if temp.CANCEL.get(user): break
            
            sts.save_last(msg.id)
            sts.add('fetched')
            batch_counter += 1

            # Update UI every 15 messages to reduce CPU usage (Prevents Freezing)
            if batch_counter % 15 == 0: 
                await edit(m, 'Forwarding...', 10, sts)

            # Batch Delay Logic
            if mode == "batch" and batch_counter >= batch_limit:
                await edit(m, f'Sleeping {batch_sleep}s', batch_sleep, sts)
                await asyncio.sleep(batch_sleep)
                batch_counter = 0

            if msg.empty or msg.service:
                sts.add('deleted')
                continue

            # Execution logic
            try:
                if forward_tag:
                    MSG.append(msg.id)
                    if len(MSG) >= 10: # Forward in small groups of 10
                        await client.forward_messages(i.TO, i.FROM, MSG)
                        sts.add('total_files', len(MSG))
                        MSG = []
                        await asyncio.sleep(1) # Tiny pause to avoid flood
                else:
                    await client.copy_message(i.TO, i.FROM, msg.id, caption=caption, reply_markup=button)
                    sts.add('total_files')
                    await asyncio.sleep(1.5) # Safe delay for Single Mode
            except FloodWait as e:
                await edit(m, 'Flood Wait', e.value, sts)
                await asyncio.sleep(e.value)

    except Exception as e: 
        await m.edit(f"⚠️ Stopped: {e}")

    temp.lock[user] = False
    temp.IS_FRWD_CHAT.remove(i.TO)
    await edit(m, 'Completed ✅', "completed", sts)
    await client.stop()

# MATERIAL YOU PROGRESS UI
async def edit(msg, title, status, sts):
    i = sts.get(full=True)
    perc = float(i.fetched)*100/float(i.total) if i.total > 0 else 0
    bar = f"<b>{'━' * math.floor(perc/6.6)}{'─' * (15 - math.floor(perc/6.6))}</b>"
    
    # Speed Calculation
    now = time.time()
    diff = int(now - i.start)
    speed = sts.divide(i.fetched, diff)
    eta = get_readable_time(round(sts.divide(i.total - i.fetched, int(speed))))

    text = (
        f"<b>✨ Ultra Forwarding System</b>\n"
        f"<code>{bar}</code> <b>{int(perc)}%</b>\n\n"
        f"📊 <b>Progress:</b> <code>{i.fetched}</code>/<code>{i.total}</code>\n"
        f"✅ <b>Success:</b> <code>{i.total_files}</code>\n"
        f"🕒 <b>Status:</b> <code>{status if isinstance(status, str) else 'Sleeping...'}</code>\n"
        f"⏳ <b>ETA:</b> <code>{eta}</code>"
    )

    try:
        await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"◈ {title} ◈", "status")]]))
    except Exception: pass
