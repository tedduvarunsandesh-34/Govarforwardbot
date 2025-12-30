import logging
import logging.config

# Load the external logging configuration
logging.config.fileConfig('logging.conf')

# Silence Pyrogram's noisy logs (keep only Warnings/Errors)
# This ensures your console only shows YOUR bot's important logs
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from keep_alive import start
from bot import Bot

# Start the Web Server (for Render/UptimeRobot)
start()

# Initialize and Run the Bot
app = Bot()
app.run()

