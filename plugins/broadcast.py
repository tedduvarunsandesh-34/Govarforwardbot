# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import asyncio 
import time 
import datetime 
import logging
from database import db 
from config import Config
from pyrogram import Client, filters 
from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked

# Setup Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.command(["broadcast", "b"]) & filters.user(Config.OWNER_ID) & filters.reply)
async def broadcast(bot, message):
    users_cursor = await db.get_all_users()
    b_msg = message.reply_to_message
    
    sts = await message.reply_text(
        text='<b>🚀 Broadcasting Started...</b>'
    )
    
    start_time = time.time()
    total_users_count, _ = await db.total_users_bots_count()
    
    # Statistics
    done = 0
    blocked = 0
    deleted = 0
    failed = 0 
    success = 0
    
    # BATCHING SETUP
    BATCH_SIZE = 20 # Number of users to message simultaneously
    batch_tasks = []
    
    async for user in users_cursor:
        # Create a background task for each user
        task = asyncio.create_task(broadcast_messages(int(user['id']), b_msg))
        batch_tasks.append(task)
        
        # When batch is full, execute all tasks in parallel
        if len(batch_tasks) >= BATCH_SIZE:
            results = await asyncio.gather(*batch_tasks)
            
            # Process results
            for result, status_msg in results:
                if result:
                    success += 1
                elif status_msg == "Blocked":
                    blocked += 1
                elif status_msg == "Deleted":
                    deleted += 1
                elif status_msg == "Error":
                    failed += 1
            
            done += len(batch_tasks)
            batch_tasks = [] # Reset batch
            
            # Update Status Message every 20 users
            await sts.edit(
                f"<b><u>🚀 Broadcast In Progress :</u></b>\n\n"
                f"<b>👥 Total Users:</b> {total_users_count}\n"
                f"<b>✅ Completed:</b> {done} / {total_users_count}\n"
                f"<b>✅ Success:</b> {success}\n"
                f"<b>🚫 Blocked:</b> {blocked}\n"
                f"<b>🗑️ Deleted:</b> {deleted}\n"
                f"<b>❌ Failed:</b> {failed}"
            )

    # Process remaining tasks (if any left in the last batch)
    if batch_tasks:
        results = await asyncio.gather(*batch_tasks)
        for result, status_msg in results:
            if result:
                success += 1
            elif status_msg == "Blocked":
                blocked += 1
            elif status_msg == "Deleted":
                deleted += 1
            elif status_msg == "Error":
                failed += 1
        done += len(batch_tasks)

    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    
    await sts.edit(
        f"<b><u>✅ Broadcast Completed :</u></b>\n\n"
        f"<b>⏱️ Time Taken:</b> {time_taken}\n\n"
        f"<b>👥 Total Users:</b> {total_users_count}\n"
        f"<b>✅ Completed:</b> {done} / {total_users_count}\n"
        f"<b>✅ Success:</b> {success}\n"
        f"<b>🚫 Blocked:</b> {blocked}\n"
        f"<b>🗑️ Deleted:</b> {deleted}\n"
        f"<b>❌ Failed:</b> {failed}"
    )

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        # Smart Sleep: Wait exactly as long as Telegram needs, then retry
        await asyncio.sleep(e.value + 1)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Removed from Database (Deleted Account).")
        return False, "Deleted"
    except UserIsBlocked:
        logger.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except Exception as e:
        logger.error(f"Error broadcasting to {user_id}: {e}")
        return False, "Error"
        
