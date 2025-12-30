

import logging
import logging.config

# Get logging configurations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from keep_alive import start
from bot import Bot

# Start the Web Server (for Render/UptimeRobot)
start()

# Initialize and Run the Bot
app = Bot()
app.run()

