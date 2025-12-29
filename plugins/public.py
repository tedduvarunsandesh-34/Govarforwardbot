from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import STS

@Client.on_message(filters.private & filters.command("forward"))
async def run(bot, message):
    user_id = message.from_user.id
    
    # Check if bot exists
    _bot = await db.get_bot(user_id)
    if not _bot: return await message.reply("Add a bot in /settings first!")

    # Manual ID Prompts
    src = await bot.ask(message.chat.id, "🆔 **Enter Source Chat ID:**\n(e.g. -100123456789 or @username)")
    dest = await bot.ask(message.chat.id, "🆔 **Enter Destination Chat ID:**\n(e.g. -100987654321 or @username)")
    skip = await bot.ask(message.chat.id, "🔢 **Enter Start Message ID:**\n(Number only)")
    lim = await bot.ask(message.chat.id, "📊 **How many messages to forward?**")

    if not skip.text.isdigit() or not lim.text.isdigit():
        return await message.reply("Error: Start ID and Limit must be numbers!")

    fid = f"{user_id}-{message.id}"
    STS(fid).store(src.text, dest.text, int(skip.text), int(lim.text))

    buttons = [[
        InlineKeyboardButton("⚡ Single Mode", callback_data=f"mode_single_{fid}"),
        InlineKeyboardButton("📦 Batch Mode", callback_data=f"mode_batch_{fid}")
    ]]
    await message.reply("📋 **Step 1: Select Forwarding Mode**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^mode_"))
async def set_mode(bot, q):
    _, mode, fid = q.data.split("_")
    STS(fid).set("mode", mode)
    btns = [[
        InlineKeyboardButton("50/5s", f"speed_{fid}_50_5"),
        InlineKeyboardButton("100/10s", f"speed_{fid}_100_10"),
        InlineKeyboardButton("200/20s", f"speed_{fid}_200_20")
    ],[
        InlineKeyboardButton("▶️ START FORWARDING", f"start_public_{fid}")
    ]]
    await q.message.edit("🚀 **Step 2: Select Speed & Start**", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex("^speed_"))
async def set_speed(bot, q):
    _, fid, sz, dl = q.data.split("_")
    STS(fid).set("batch_size", int(sz))
    STS(fid).set("batch_delay", int(dl))
    await q.answer(f"Speed set to {sz} per {dl}s", show_alert=True)
