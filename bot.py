

import asyncio
import logging 
import logging.config
from database import db 
from config import Config  
from pyrogram import Client, __version__
from pyrogram.raw.all import layer 
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait 

# Setup Logging based on your logging.conf
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR) # Keep pyrogram quiet

class Bot(Client): 
    def __init__(self):
        super().__init__(
            Config.BOT_SESSION,
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins={
                "root": "plugins"
            },
            workers=50, # High worker count for speed
            max_concurrent_transmissions=10, # Allow multiple media transfers at once
            bot_token=Config.BOT_TOKEN
        )
        self.log = logging

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        self.id = me.id
        self.username = me.username
        self.first_name = me.first_name
        self.set_parse_mode(ParseMode.DEFAULT)
        
        text = "**Bot Restarted !**"
        logging.info(text)
        
        # --- OPTIMIZED RESTART NOTIFICATION ---
        # Fetch all users who were forwarding before restart
        users_cursor = await db.get_all_frwd()
        users_list = [user async for user in users_cursor]
        
        if users_list:
            success = 0
            failed = 0
            
            # Helper function to send notification safely
            async def notify_user(user_data):
                chat_id = user_data['user_id']
                try:
                    await self.send_message(chat_id, text)
                    return True
                except FloodWait as e:
                    await asyncio.sleep(e.value + 1)
                    await self.send_message(chat_id, text)
                    return True
                except Exception:
                    return False

            # Notify all users simultaneously (Batching)
            tasks = [notify_user(u) for u in users_list]
            results = await asyncio.gather(*tasks)
            
            success = results.count(True)
            failed = results.count(False)
            
            # Clear the list after notifying
            await db.rmve_frwd(all=True)
            logging.info(f"Restart Notification Stats - Success: {success}, Failed: {failed}")

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        logging.info(msg)
        
