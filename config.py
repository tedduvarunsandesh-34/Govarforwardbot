# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import os

class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    BOT_SESSION = os.environ.get("BOT_SESSION", "forward-bot") 
    DB_URL = os.environ.get("DB_URL", "")
    DB_NAME = os.environ.get("DB_NAME", "filetolink")
    
    # NEW: Worker Count (Default to 50 for 10x  Speed)
    WORKERS = int(os.environ.get("WORKERS", 5))

    # Safe Owner ID Parsing
    owner = os.environ.get("OWNER_ID", "")
    OWNER_ID = [int(id) for id in owner.split()] if owner else []

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    CONFIGS = {}
    
