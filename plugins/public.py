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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

#===================Run Function===================#

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    
    # 1. Check if user has added a bot
    _bot = await db.get_bot(user_id)
    if not _bot:
      return await message.reply("You Did Not Added Any Bot. Please Add A Bot Using /settings !")
    
    # 2. Check destination channels
    channels = await db.get_user_channels(user_id)
    if not channels:
       return await message.reply_text("Please Set A To Channel In /settings Before Forwarding")
    
    # 3. Handle multiple destination channels
    if len(channels) > 1:
       for channel in channels:
          buttons.append([KeyboardButton(f"{channel['title']}")])
          btn_data[channel['title']] = channel['chat_id']
       buttons.append([KeyboardButton("cancel")]) 
       _toid = await bot.ask(message.chat.id, Translation.TO_MSG.format(_bot['name'], _bot['username']), reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
       if _toid.text.startswith(('/', 'cancel')):
          return await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())
       to_title = _toid.text
       toid = btn_data.get(to_title)
       if not toid:
          return await message.reply_text("Wrong Channel Choosen !", reply_markup=ReplyKeyboardRemove())
    else:
       toid = channels[0]['chat_id']
       to_title = channels[0]['title']
    
    # 4. Ask for Source Link
    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return 
    
    # 5. Parse the Link / Forward
    chat_id = None
    last_msg_id = None

    if fromid.text and not fromid.forward_date:
        # Regex to handle t.me/c/ID/MSG_ID and t.me/USERNAME/MSG_ID
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid Link. Please send a valid post link.')
        
        chat_id_raw = match.group(4)
        last_msg_id = int(match.group(5))
        
        if chat_id_raw.isnumeric():
            chat_id = int(("-100" + chat_id_raw))
        else:
            chat_id = chat_id_raw # Username case
            
    elif fromid.forward_from_chat and fromid.forward_from_chat.type in [enums.ChatType.CHANNEL]:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if last_msg_id is None:
           return await message.reply_text("Could not get message ID. Please send the Link of the last message instead.")
    else:
        await message.reply_text("Invalid Source! Send a Channel Link or Forward a message from a Channel.")
        return 

    # 6. Validate Source Chat Access
    try:
        chat_info = await bot.get_chat(chat_id)
        title = chat_info.title
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "Private Channel"
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link Specified.')
    except Exception as e:
        # If bot isn't admin or can't see chat, we assume userbot will handle it later
        title = "Private/Unknown"

    # 7. Ask for Skip Count
    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return
    
    try:
        skip_count = int(skipno.text)
    except ValueError:
        return await message.reply("Please enter a valid number for skipping.")

    # 8. LOGIC FIX FOR BATCH ENGINE
    # We calculate exactly how many messages to process
    # Limit = (The message ID you sent) - (The skip count)
    real_limit = last_msg_id - skip_count

    if real_limit <= 0:
        return await message.reply(f"<b>Error:</b> Your skip number ({skip_count}) is equal to or greater than the Last Message ID ({last_msg_id}).\nNothing to forward.")

    forward_id = f"{user_id}-{skipno.id}"
    
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        text=Translation.DOUBLE_CHECK.format(
            botname=_bot['name'], 
            botuname=_bot['username'], 
            from_chat=title, 
            to_chat=to_title, 
            skip=skipno.text
        ) + f"\n\n<b>Total Files to Forward:</b> {real_limit}",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    
    # Store: (Source, Target, Start_Offset, Count_To_Process)
    STS(forward_id).store(chat_id, toid, skip_count, real_limit)
 
