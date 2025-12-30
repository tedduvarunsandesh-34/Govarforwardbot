# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import re
import asyncio
from database import db
from config import temp
from .test import CLIENT , start_clone_bot
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()
COMPLETED_BTN = InlineKeyboardMarkup(
   [
      [InlineKeyboardButton('📢 Updates', url='https://t.me/Madflix_Bots')],
      [InlineKeyboardButton('💬 Support', url='https://t.me/MadflixBots_Support')]
   ]
)

CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton('✖️ Cancel ✖️', 'terminate_frwd')]])

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify(client, message):
   user_id = message.from_user.id
   temp.CANCEL[user_id] = False
   
   if temp.lock.get(user_id) and str(temp.lock.get(user_id))=="True":
      return await message.reply("Please Wait Until Previous Task Complete")
   
   _bot = await db.get_bot(user_id)
   if not _bot or _bot['is_bot']:
      return await message.reply("Need Userbot To Do This Process. Please Add A Userbot Using /settings")
   
   target = await client.ask(user_id, text="Forward The Last Message From Target Chat Or Send Last Message Link.\n/cancel - To Cancel This Process")
   
   if target.text and target.text.startswith("/"):
      return await message.reply("Process Cancelled !")
      
   chat_id = None
   
   if target.text:
      regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
      match = regex.match(target.text.replace("?single", ""))
      if not match:
         return await message.reply('Invalid Link')
      chat_id = match.group(4)
      if chat_id.isnumeric():
         chat_id  = int(("-100" + chat_id))
         
   # FIX: Changed 'fromid' to 'target' (Variable name fix)
   elif target.forward_from_chat: 
        chat_id = target.forward_from_chat.id
   else:
        return await message.reply_text("Invalid! Please send a Link or Forward a message from a Channel.")
   
   confirm = await client.ask(user_id, text="Send /yes To Start The Process And /no To Cancel This Process")
   if confirm.text.lower() == '/no':
      return await confirm.reply("Process Cancelled !")
   
   sts = await confirm.reply("Processing..")
   
   try:
      bot = await start_clone_bot(CLIENT.client(_bot))
   except Exception as e:
      return await sts.edit(f"Error starting bot: {e}")
      
   try:
       # Verify permissions
       k = await bot.send_message(chat_id, text="testing")
       await k.delete()
   except:
       await sts.edit(f"Please Make Your [Userbot](t.me/{_bot['username']}) Admin In Target Chat With Full Permissions")
       return await bot.stop()
   
   # OPTIMIZATION: Use a SET for unique IDs (O(1) lookup speed)
   MESSAGES = set() 
   DUPLICATE = []
   total = 0
   deleted = 0
   
   temp.lock[user_id] = True
   
   try:
     await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Progressing"), reply_markup=CANCEL_BTN)
     
     # Use Pyrogram Enum for filter
     async for message in bot.search_messages(chat_id=chat_id, filter=enums.MessagesFilter.DOCUMENT):
        if temp.CANCEL.get(user_id) == True:
           await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Cancelled"), reply_markup=COMPLETED_BTN)
           return await bot.stop()
        
        if message.document:
            # FIX: Use 'file_unique_id' (Native & Fast) instead of external 'unpack_new_file_id'
            file_unique_id = message.document.file_unique_id
            
            if file_unique_id in MESSAGES:
               DUPLICATE.append(message.id)
            else:
               MESSAGES.add(file_unique_id)
            
            total += 1
            
            if total % 1000 == 0: # Update UI every 1000 msgs to save API calls
               await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Progressing"), reply_markup=CANCEL_BTN)
            
            # Batch Delete (100 is Telegram's limit per call)
            if len(DUPLICATE) >= 100:
               await bot.delete_messages(chat_id, DUPLICATE)
               deleted += 100
               await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Deleting..."), reply_markup=CANCEL_BTN)
               DUPLICATE = []

     # Delete remaining duplicates after loop ends
     if DUPLICATE:
        await bot.delete_messages(chat_id, DUPLICATE)
        deleted += len(DUPLICATE)
        
   except Exception as e:
       temp.lock[user_id] = False 
       await sts.edit(f"**Error**\n\n`{e}`")
       return await bot.stop()
       
   temp.lock[user_id] = False
   await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "Completed"), reply_markup=COMPLETED_BTN)
   await bot.stop()
   
