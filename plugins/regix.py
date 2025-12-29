import math, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import STS, get_readable_time
from config import temp

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user, fid = message.from_user.id, message.data.split("_")[2]
    sts = STS(fid)
    if not sts.verify(): return
    
    # Load User Configs
    i = sts.get(full=True)
    batch_limit = sts.get("batch_size") or 100
    batch_sleep = sts.get("batch_delay") or 10
    mode = sts.get("mode") or "batch"

    m = await message.message.edit("🚀 **Connecting Engine...**")
    _bot, caption, forward_tag, button, protect = await sts.get_data(user)
    
    from .test import start_clone_bot, CLIENT
    client = await start_clone_bot(CLIENT().client(_bot))
    
    temp.lock[user] = True
    sts.add(time=True)

    try:
        count = 0
        async for msg in client.iter_messages(i.FROM, limit=i.total, offset_id=i.get_last()):
            if temp.CANCEL.get(user): break
            
            # Save progress for auto-resume
            sts.save_last(msg.id)
            sts.add('fetched')
            count += 1

            # Update UI every 15 msgs to prevent freezing
            if count % 15 == 0: await edit_progress(m, "Forwarding", sts)

            # Batch Sleep Logic
            if mode == "batch" and count >= batch_limit:
                await edit_progress(m, f"Sleeping {batch_sleep}s", sts)
                await asyncio.sleep(batch_sleep)
                count = 0

            if msg.empty or msg.service: continue

            try:
                await client.copy_message(i.TO, i.FROM, msg.id, caption=caption, reply_markup=button, protect_content=protect)
                sts.add('total_files')
                await asyncio.sleep(1.2) # Minimum safe delay
            except Exception: 
                sts.add('deleted')

    except Exception as e: 
        await m.edit(f"❌ Error: {e}")
    finally:
        temp.lock[user] = False
        await edit_progress(m, "Finished ✅", sts)
        await client.stop()

async def edit_progress(msg, status, sts):
    i = sts.get(full=True)
    total = i.total if i.total > 0 else 1
    perc = (i.fetched * 100) / total
    bar = f"<b>{'━' * math.floor(perc/6.6)}{'─' * (15 - math.floor(perc/6.6))}</b>"
    
    now = time.time()
    diff = int(now - i.start)
    speed = sts.divide(i.fetched, diff)
    eta = get_readable_time(round(sts.divide(i.total - i.fetched, int(speed))))

    text = (
        f"<b>✨ Ultra Forwarding System</b>\n"
        f"<code>{bar}</code> <b>{int(perc)}%</b>\n\n"
        f"📊 **Forwarded:** <code>{i.total_files}</code>\n"
        f"🕒 **Status:** <code>{status}</code>\n"
        f"⏳ **ETA:** <code>{eta}</code>"
    )
    try:
        await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◈ Status ◈", "status")]]))
    except: pass
