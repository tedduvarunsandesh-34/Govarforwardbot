# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import os
import re 
import sys
import typing
import asyncio 
import logging 
from database import db 
from config import Config, temp
from pyrogram import Client, filters
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait
from translation import Translation
from typing import Union, Optional, AsyncGenerator

# --- DEBUG LOGGING ENABLED ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:/{0,2}(.+?)(:same)?])")
BOT_TOKEN_TEXT = "1) Create A Bot Using @BotFather\n\n2) Then You Will Get A Message With Bot Token\n\n3) Forward That Message To Me"
SESSION_STRING_SIZE = 351

async def start_clone_bot(FwdBot, data=None):
   logger.info("DEBUG: Entering start_clone_bot function...")
   try:
       logger.info("DEBUG: Attempting to Connect to Telegram Servers...")
       # FIX: Added 25s Timeout. If it hangs here, it means IP is blocked or Session is invalid.
       await asyncio.wait_for(FwdBot.start(), timeout=25)
       logger.info("DEBUG: Connection Successful! Client started.")
   except asyncio.TimeoutError:
       logger.error("DEBUG: Connection Timed Out! (Telegram did not respond)")
       raise Exception("⚠️ Connection Timed Out!\n\nPossible Causes:\n1. Your Server IP is blocked by Telegram.\n2. The Session String/Token is invalid.\n3. Telegram is asking for 2FA Password.")
   except Exception as e:
       logger.error(f"DEBUG: Connection Failed with error: {e}")
       raise Exception(f"⚠️ Login Failed: {e}")

   # Define the iterator function
   async def iter_messages(
      self, 
      chat_id: Union[int, str], 
      limit: int, 
      offset: int = 0,
      search: str = None,
      filter: "types.TypeMessagesFilter" = None,
      ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially."""
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
   
   # Attach iterator to the bot instance
   FwdBot.iter_messages = iter_messages
   return FwdBot

class CLIENT: 
  def __init__(self):
     self.api_id = Config.API_ID
     self.api_hash = Config.API_HASH
    
  def client(self, data, user=None):
     # --- SPEED OPTIMIZATION: High Workers & Max Concurrent Transmissions ---
     worker_count = getattr(Config, 'WORKERS', 50)
     
     if user == None and data.get('is_bot') == False:
        return Client(
            "USERBOT", 
            self.api_id, 
            self.api_hash, 
            session_string=data.get('session'),
            workers=worker_count, 
            max_concurrent_transmissions=10
        )
     elif user == True:
        return Client(
            "USERBOT", 
            self.api_id, 
            self.api_hash, 
            session_string=data,
            workers=worker_count, 
            max_concurrent_transmissions=10
        )
     elif user != False:
        data = data.get('token')
     
     return Client(
         "BOT", 
         self.api_id, 
         self.api_hash, 
         bot_token=data, 
         in_memory=True,
         workers=worker_count, 
         max_concurrent_transmissions=10
     )

  async def add_bot(self, bot, message):
     user_id = int(message.from_user.id)
     msg = await bot.ask(chat_id=user_id, text=BOT_TOKEN_TEXT)
     if msg.text=='/cancel':
        return await msg.reply('Process Cancelled !')
     elif not msg.forward_date:
       return await msg.reply_text("This Is Not A Forward Message")
     
     # Regex to extract token
     bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
     bot_token = bot_token[0] if bot_token else None
     
     if not bot_token:
       return await msg.reply_text("There Is No Bot Token In That Message")
     
     try:
       logger.info("DEBUG: Initializing Bot Client...")
       _client = await start_clone_bot(self.client(bot_token, False), True)
     except Exception as e:
       await msg.reply_text(f"<b>Bot Error :</b> `{e}`")
       return 
       
     _bot = _client.me
     details = {
       'id': _bot.id,
       'is_bot': True,
       'user_id': user_id,
       'name': _bot.first_name,
       'token': bot_token,
       'username': _bot.username 
     }
     
     logger.info("DEBUG: Saving Bot to Database...")
     try:
         await asyncio.wait_for(db.add_bot(details), timeout=10)
         logger.info("DEBUG: Saved successfully.")
     except asyncio.TimeoutError:
         logger.error("DEBUG: Database Timeout! Check MongoDB Whitelist.")
         await msg.reply_text("<b>Error:</b> Database Timeout! Please check your MongoDB IP Whitelist.")
         return
         
     return True
    
  async def add_session(self, bot, message):
     user_id = int(message.from_user.id)
     text = "<b>⚠️ Disclaimer ⚠️</b>\n\nYou Can Use Your Session For Forward Message From Private Chat To Another Chat.\nPlease Add Your Pyrogram Session With Your Own Risk. Their Is A Chance To Ban Your Account. My Developer Is Not Responsible If Your Account May Get Banned."
     await bot.send_message(user_id, text=text)
     msg = await bot.ask(chat_id=user_id, text="<b>Send your pyrogram session.\nget it from @mdsessiongenbot\n\n/cancel - cancel the process</b>")
     if msg.text=='/cancel':
        return await msg.reply('Process Cancelled !')
     elif len(msg.text) < SESSION_STRING_SIZE:
        return await msg.reply('Invalid Session String')
     try:
       logger.info("DEBUG: Initializing Userbot Session...")
       client = await start_clone_bot(self.client(msg.text, True), True)
     except Exception as e:
       await msg.reply_text(f"<b>User Bot Error :</b> `{e}`")
       return
       
     user = client.me
     details = {
       'id': user.id,
       'is_bot': False,
       'user_id': user_id,
       'name': user.first_name,
       'session': msg.text,
       'username': user.username
     }
     
     logger.info("DEBUG: Saving Session to Database...")
     try:
         await asyncio.wait_for(db.add_bot(details), timeout=10)
         logger.info("DEBUG: Saved successfully.")
     except asyncio.TimeoutError:
         logger.error("DEBUG: Database Timeout! Check MongoDB Whitelist.")
         await msg.reply_text("<b>Error:</b> Database Timeout! Please check your MongoDB IP Whitelist.")
         return
         
     return True

@Client.on_message(filters.private & filters.command('reset'))
async def forward_tag(bot, m):
    default = await db.get_configs("01")
    temp.CONFIGS[m.from_user.id] = default
    await db.update_configs(m.from_user.id, default)
    await m.reply("Successfully Settings Reseted ✔️")

@Client.on_message(filters.command('resetall') & filters.user(Config.OWNER_ID))
async def resetall(bot, message):
  users = await db.get_all_users()
  sts = await message.reply("Processing")
  TEXT = "Total: {}\nSuccess: {}\nFailed: {}\nExcept: {}"
  total = success = failed = already = 0
  ERRORS = []
  async for user in users:
      user_id = user['id']
      default = await get_configs(user_id)
      default['db_uri'] = None
      total += 1
      if total %10 == 0:
         await sts.edit(TEXT.format(total, success, failed, already))
      try: 
         await db.update_configs(user_id, default)
         success += 1
      except Exception as e:
         ERRORS.append(e)
         failed += 1
  if ERRORS:
     await message.reply(ERRORS[:100])
  await sts.edit("Completed\n" + TEXT.format(total, success, failed, already))
  
async def get_configs(user_id):
  configs = await db.get_configs(user_id)
  return configs

async def update_configs(user_id, key, value):
  current = await db.get_configs(user_id)
  if key in ['caption', 'duplicate', 'db_uri', 'forward_tag', 'protect', 'file_size', 'size_limit', 'extension', 'keywords', 'button']:
     current[key] = value
  else: 
     current['filters'][key] = value
  await db.update_configs(user_id, current)
    
def parse_buttons(text, markup=True):
    buttons = []
    if not text: return None
    
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", "")))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(3).replace(" ", ""))])
    if markup and buttons:
       buttons = InlineKeyboardMarkup(buttons)
    return buttons if buttons else None

