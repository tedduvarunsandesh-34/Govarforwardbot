from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import STS

@Client.on_message(filters.private & filters.command("forward"))
async def run(bot, message):
    user_id = message.from_user.id
    
    # 1. Manual ID Entry
    src = await bot.ask(message.chat.id, "🆔 **Enter Source Chat ID:**")
    dest = await bot.ask(message.chat.id, "🆔 **Enter Destination Chat ID:**")
    skip = await bot.ask(message.chat.id, "🔢 **Enter Start Message ID:**")
    lim = await bot.ask(message.chat.id, "📊 **How many messages to forward?**")

    fid = f"{user_id}-{message.id}"
    STS(fid).store(src.text, dest.text, int(skip.text), int(lim.text))

    buttons = [[
        InlineKeyboardButton("⚡ Single", callback_data=f"mode_single_{fid}"),
        InlineKeyboardButton("📦 Batch", callback_data=f"mode_batch_{fid}")
    ]]
    await message.reply("📋 **Select Mode:**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^mode_"))
async def set_mode(bot, q):
    _, mode, fid = q.data.split("_")
    STS(fid).set("mode", mode)
    btns = [[
        InlineKeyboardButton("50/5s", f"speed_{fid}_50_5"),
        InlineKeyboardButton("100/10s", f"speed_{fid}_100_10")
    ],[
        InlineKeyboardButton("▶️ START", f"start_public_{fid}")
    ]]
    await q.message.edit("🚀 **Select Speed:**", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex("^speed_"))
async def set_speed(bot, q):
    _, fid, sz, dl = q.data.split("_")
    STS(fid).set("batch_size", int(sz))
    STS(fid).set("batch_delay", int(dl))
    await q.answer("Speed set!", show_alert=True)
