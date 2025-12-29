# Jishu Developer 
# Patched regix.py

import math, time, asyncio
from .utils import STS
from database import db 
from .test import CLIENT , start_clone_bot
from config import temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    
    sts = STS(frwd_id)
    if not sts.verify(): return await message.answer("Session Expired", show_alert=True)
    
    i = sts.get(full=True)
    # READ USER SETTINGS
    batch_limit = sts.get("batch_size") or 100
    batch_sleep = sts.get("batch_delay") or 10
    mode = sts.get("mode") or "batch"

    m = await message.message.edit("Verifying Data...")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
    
    try: client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e: return await m.edit(f"Error: {e}")

    temp.IS_FRWD_CHAT.append(i.TO)
    temp.lock[user] = True
    await db.add_frwd(user)
    sts.add(time=True)

    try:
        MSG, pling, batch_counter = [], 0, 0
        async for msg in client.iter_messages(client, chat_id=i.FROM, limit=int(i.limit), offset=int(i.skip) or 0):
            if temp.CANCEL.get(user): break
            if pling % 20 == 0: await edit(m, 'Progressing', 10, sts)
            pling += 1
            sts.add('fetched')

            # BATCH SLEEP LOGIC
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
                await copy(client, {"msg_id": msg.id, "media": media(msg), "caption": custom_caption(msg, caption), 'button': button, "protect": protect}, m, sts)
                sts.add('total_files')
                batch_counter += 1
                await asyncio.sleep(1 if _bot['is_bot'] else 5)

    except Exception as e: await m.edit(f"Error: {e}")

    temp.IS_FRWD_CHAT.remove(i.TO)
    temp.lock[user] = False
    await edit(m, 'Completed', "completed", sts) 
    await client.stop()

# MATERIAL YOU UI
async def edit(msg, title, status, sts):
    i = sts.get(full=True)
    status_text = 'Forwarding' if status == 10 else f"Sleeping {status}s" if str(status).isnumeric() else status
    perc = float(i.fetched)*100/float(i.total)
    
    bar = f"<b>{'━' * math.floor(perc/6.6)}{'─' * (15 - math.floor(perc/6.6))}</b>"
    now = time.time()
    speed = sts.divide(i.fetched, int(now - i.start))
    eta = TimeFormatter(milliseconds=round(sts.divide(i.total - i.fetched, int(speed))) * 1000)

    text = Translation.TEXT.format(i.fetched, i.total_files, i.duplicate, i.deleted, i.total, status_text, int(perc), eta, bar)
    await msg.edit(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"◈ {title} ◈", "status")]]))

# Helper functions: copy, forward, custom_caption, media, TimeFormatter, etc. stay as they are.

   text = (
       f"<b>✨ Ultra Forwarding System</b>\n"
       f"<code>{progress_bar}</code> <b>{percentage}%</b>\n\n"
       f"<b>📊 Progress Stats</b>\n"
       f" ├ <b>Processed:</b> <code>{i.fetched}</code> / <code>{i.total}</code>\n"
       f" ├ <b>Success:</b> <code>{i.total_files}</code>\n"
       f" ├ <b>Duplicates:</b> <code>{i.duplicate}</code>\n"
       f" └ <b>Deleted:</b> <code>{i.deleted}</code>\n\n"
       f"<b>🕒 Timing Details</b>\n"
       f" ├ <b>Status:</b> <code>{status_text}</code>\n"
       f" └ <b>ETA:</b> <code>{TimeFormatter(milliseconds=estimated_total_time)}</code>"
   )

   button = [[InlineKeyboardButton(f"◈ {title} ◈", f'fwrdstatus#{status_text}#{estimated_total_time}#{percentage}#{i.id}')]]
   
   if status in ["cancelled", "completed"]:
      button.append([
         InlineKeyboardButton('📢 Updates', url='https://t.me/Madflix_Bots'),
         InlineKeyboardButton('💬 Support', url='https://t.me/MadflixBots_Support')
      ])
   else:
      button.append([InlineKeyboardButton('✖️ Terminate Process ✖️', 'terminate_frwd')])
   
   await msg_edit(msg, text, InlineKeyboardMarkup(button))

async def is_cancelled(client, user, msg, sts):
   if temp.CANCEL.get(user)==True:
      if sts.TO in temp.IS_FRWD_CHAT:
          temp.IS_FRWD_CHAT.remove(sts.TO)
      await edit(msg, "Cancelled", "completed", sts)
      await send(client, user, "❌ Forwarding Process Cancelled")
      await stop(client, user)
      return True 
   return False 

async def stop(client, user):
   try:
     await client.stop()
   except:
     pass 
   await db.rmve_frwd(user)
   temp.forwardings -= 1
   temp.lock[user] = False 
    
async def send(bot, user, text):
   try:
      await bot.send_message(user, text=text)
   except:
      pass 
     
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

def media(msg):
  if msg.media:
     media_obj = getattr(msg, msg.media.value, None)
     if media_obj:
        return getattr(media_obj, 'file_id', None)
  return None 

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def retry_btn(id):
    return InlineKeyboardMarkup([[InlineKeyboardButton('♻️ Retry ♻️', f"start_public_{id}")]])

@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    await m.answer("Forwarding Cancelled !", show_alert=True)

@Client.on_callback_query(filters.regex(r'^fwrdstatus'))
async def status_msg(bot, msg):
    _, status, est_time, percentage, frwd_id = msg.data.split("#")
    sts = STS(frwd_id)
    if not sts.verify():
       fetched = forwarded = remaining = 0
    else:
       fetched, forwarded = sts.get('fetched'), sts.get('total_files')
       remaining = fetched - forwarded 
    est_time_str = TimeFormatter(milliseconds=est_time)
    est_time_str = est_time_str if (est_time_str != '' or status not in ['completed', 'cancelled']) else '0 s'
    progress_details = (
        f"📊 Percentage: {percentage}%\n"
        f"♻️ Fetched: {fetched}\n"
        f"🔥 Forwarded: {forwarded}\n"
        f"🫠 Remaining: {remaining}\n"
        f"📊 Status: {status}\n"
        f"⏳️ ETA: {est_time_str}"
    )
    return await msg.answer(progress_details, show_alert=True)

@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
    if update.message.reply_to_message:
        await update.message.reply_to_message.delete()
