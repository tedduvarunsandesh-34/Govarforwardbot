

import os

class Config:
    # API_ID should be an integer for Pyrogram
    API_ID = int(os.environ.get("API_ID", 0)) 
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    BOT_SESSION = os.environ.get("BOT_SESSION", "forward-bot") 
    DB_URL = os.environ.get("DB_URL", "")
    DB_NAME = os.environ.get("DB_NAME", "madflixbotz")
    
    # Safely parse OWNER_ID (handles empty strings without crashing)
    owner = os.environ.get("OWNER_ID", "")
    OWNER_ID = [int(id) for id in owner.split()] if owner else []

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    CONFIGS = {} # Added missing dictionary to prevent crashes in 'reset' command
    
