

import os
import logging
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

class Config:
    # --- Required Credentials ---
    # Fixed: Added a default '0' to prevent syntax and value errors
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # --- Database & Sessions ---
    DB_URL = os.environ.get("DB_URL", "")
    DB_NAME = os.environ.get("DB_NAME", "forward_bot_db")
    BOT_SESSION = os.environ.get("BOT_SESSION", "forward-bot")
    
    # --- Identity & Security ---
    OWNER_ID = [int(id) for id in os.environ.get("OWNER_ID", "8496419402").replace(',', ' ').split() if id.strip().isdigit()]
    
    # --- Channel & Storage Logic ---
    BIN_CHANNEL = int(os.environ.get("BIN_CHANNEL", -1003656791142)) 
    
    # --- Performance ---
    TG_WORKERS = int(os.environ.get("TG_WORKERS", "4")) 
    PORT = int(os.environ.get("PORT", "8080")) 

class Temp:
    """Runtime storage for task locks and tracking"""
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []

# ✅ THE FIX: This alias allows plugins to use 'from config import temp'
temp = Temp
