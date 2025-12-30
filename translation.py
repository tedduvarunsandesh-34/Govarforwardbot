# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import os
from config import Config

class Translation(object):
    
  START_TXT = """<b>✨ Welcome {} !</b>

I am an Advanced <b>Auto Forward Bot</b> designed to handle your bulk forwarding needs efficiently.

🚀 <b>Key Capabilities:</b>
│ • ⚡ <b>Fast Forwarding</b> (Public & Private)
│ • 🗑️ <b>Duplicate Removal</b>
│ • 📝 <b>Custom Captions & Buttons</b>
│ • 🛡️ <b>Content Protection</b>

<i>Click the <b>Help</b> button below to learn how to use me!</i>

<b>🤖 Bot Made By @Madflix_Bots</b>"""


  HELP_TXT = """<b>🛠️ <u>User Guide</u></b>

<b>📚 Available Commands:</b>
╭─── [ <b>Main Commands</b> ]
│ <b>/start</b> - Check Bot Status
│ <b>/forward</b> - Start Forwarding
│ <b>/unequify</b> - Remove Duplicates
│ <b>/settings</b> - Configure Settings
│ <b>/reset</b> - Reset All Settings
╰───────────────

<b>💎 Premium Features:</b>
│ • Forward from <b>Private Channels</b> (via Userbot)
│ • Forward from <b>Restricted Content</b> Channels
│ • <b>Smart Filtering</b> (Size, Extension, Keywords)
│ • <b>Custom Captions</b> with placeholders
│ • <b>Skip Duplicate</b> Media automatically

<i>💡 Tip: Use /settings to configure your Userbot and target channels first!</i>"""
  
  HOW_USE_TXT = """<b>⚠️ <u>Setup Instructions</u></b>
  
<b>1️⃣ Configuration:</b>
 • Use <b>/settings</b> to add your <b>Userbot</b> (Session String).
 • Add your <b>Target Channel</b> in settings.
 
<b>2️⃣ Permissions:</b>
 • <b>Target Channel:</b> Your Bot (or Userbot) <b>MUST</b> be an Admin.
 • <b>Source Channel:</b> 
   - If Public: Bot just needs link.
   - If Private: Userbot must be a member.

<b>3️⃣ Start Forwarding:</b>
 • Use <b>/forward</b> and follow the on-screen prompts.
"""
  
  ABOUT_TXT = """<b>🤖 Bot Information</b>
  
╭───────────────
│ <b>📛 Name:</b> {}
│ <b>📝 Language:</b> Python 3
│ <b>📚 Library:</b> Pyrogram 2.0
│ <b>🚀 Server:</b> Heroku / VPS
│ <b>📢 Channel:</b> <a href='https://t.me/Madflix_Bots'>Madflix Botz</a>
│ <b>👨‍💻 Developer:</b> <a href='https://t.me/CallAdminRobot'>Jishu Developer</a>
╰───────────────

<b>♻️ Powered By @Madflix_Bots</b>"""
  
  STATUS_TXT = """<b>📊 <u>System Status</u></b>
  
╭───────────────
│ <b>👥 Total Users:</b> <code>{}</code>
│ <b>🤖 Total Bots:</b> <code>{}</code>
│ <b>🔄 Total Forwards:</b> <code>{}</code>
╰───────────────
"""
  
  FROM_MSG = "<b>📥 <u>Set Source Chat</u></b>\n\nPlease forward the <b>Last Message</b> (or send its Link) from the Source Channel.\n\n<i>/cancel - To Stop</i>"
  
  TO_MSG = "<b>📤 <u>Choose Target Chat</u></b>\n\nSelect your destination channel from the buttons below.\n\n<i>/cancel - To Stop</i>"
  
  SKIP_MSG = "<b>⏭️ <u>Set Offset (Skip)</u></b>\n\nEnter the number of messages to <b>SKIP</b> from the beginning.\n\n<b>Example:</b>\n• Enter <code>0</code> = Forward everything from the start link.\n• Enter <code>100</code> = Skip first 100 messages.\n\n<i>/cancel - To Stop</i>"
  
  CANCEL = "<b>❌ Process Cancelled Successfully.</b>"
  
  BOT_DETAILS = "<b>🤖 <u>Bot Profile</u></b>\n\n<b>➢ Name:</b> <code>{}</code>\n<b>➢ ID:</b> <code>{}</code>\n<b>➢ Username:</b> @{}"
  
  USER_DETAILS = "<b>👤 <u>UserBot Profile</u></b>\n\n<b>➢ Name:</b> <code>{}</code>\n<b>➢ ID:</b> <code>{}</code>\n<b>➢ Username:</b> @{}"  
         
  # Formatting matches the 9 placeholders used in logic
  TEXT = """<b>🚀 <u>Forwarding In Progress</u></b>

<b>╭── [ 📊 Live Stats ]</b>
<b>│</b>
<b>├ 📂 Fetched:</b> <code>{}</code>
<b>├ ✅ Forwarded:</b> <code>{}</code>
<b>├ 👥 Duplicates:</b> <code>{}</code>
<b>├ 🗑️ Deleted:</b> <code>{}</code>
<b>├ ⏩ Skipped:</b> <code>{}</code>
<b>├ 🛡️ Filtered:</b> <code>{}</code>
<b>│</b>
<b>├ 📡 Status:</b> <code>{}</code>
<b>╰── 🔥 Progress:</b> <code>{}</code>%

{}
"""

  # Formatting matches the 9 placeholders used in logic
  TEXT1 = """<b>✅ <u>Task Completed</u></b>

<b>╭── [ 📊 Final Report ]</b>
<b>│</b>
<b>├ 📂 Total Fetched:</b> <code>{}</code>
<b>├ ✅ Successfully Forwarded:</b> <code>{}</code>
<b>├ 👥 Duplicates Found:</b> <code>{}</code>
<b>├ 🗑️ Deleted:</b> <code>{}</code>
<b>├ ⏩ Skipped:</b> <code>{}</code>
<b>│</b>
<b>├ 📡 Status:</b> <code>{}</code>
<b>├ ⏳ Total Time:</b> <code>{}</code>
<b>╰── 🏁 ETA:</b> <code>{}</code>

{}"""

  DUPLICATE_TEXT = """<b>🗑️ <u>Duplicate Removal</u></b>

<b>╭── [ 🧹 Cleaning Chat ]</b>
<b>│</b>
<b>├ 📂 Scanned Messages:</b> <code>{}</code>
<b>├ 🗑️ Deleted Duplicates:</b> <code>{}</code>
<b>╰────────────────</b>

{}
"""

  DOUBLE_CHECK = """<b>🛡️ <u>Final Verification</u></b>
  
Please review the details below before starting the task.

<b>🤖 Active Bot:</b> [{botname}](t.me/{botuname})
<b>📥 Source:</b> <code>{from_chat}</code>
<b>📤 Destination:</b> <code>{to_chat}</code>
<b>⏭️ Skip Offset:</b> <code>{skip}</code>

<b>⚠️ Requirements Check:</b>
1. [{botname}](t.me/{botuname}) is an <b>ADMIN</b> in the Target Chat (<code>{to_chat}</code>).
2. If Source is <b>Private</b>, your Userbot is a member there.

<b>Does everything look correct?</b>"""
  
