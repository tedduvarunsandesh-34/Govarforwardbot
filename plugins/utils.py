# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import time as tm
from database import db 
from .test import parse_buttons

STATUS = {}

class STS:
    def __init__(self, id):
        self.id = id
        self.data = STATUS
    
    def verify(self):
        return self.data.get(self.id)
    
    def store(self, From, to, skip, limit):
        self.data[self.id] = {
            "FROM": From,
            "TO": to,
            "skip": skip,
            "limit": limit,
            "fetched": skip,
            "total_files": 0,
            "filtered": 0,
            "deleted": 0,
            "duplicate": 0,
            "total": limit,
            "start": tm.time(),

            # Forward engine (RAM only)
            "batch": True,
            "batch_size": 100,
            "batch_delay": 10,
            "last_id": skip,
            "paused": False
        }
        self.get(full=True)
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.data.get(self.id)
        if not values:
            return None
        if not full:
            return values.get(value)
        for k, v in values.items():
            setattr(self, k, v)
        return self

    def add(self, key=None, value=1, time=False):
        if time:
            self.data[self.id]["start"] = tm.time()
            return
        self.data[self.id][key] = self.get(key) + value

    def divide(self, no, by):
        by = 1 if int(by) == 0 else by 
        return int(no) / by 

    # -------- Auto Resume / Pause --------
    def pause(self):
        self.data[self.id]["paused"] = True

    def resume(self):
        self.data[self.id]["paused"] = False

    def is_paused(self):
        return self.get("paused")

    def save_last(self, msg_id):
        self.data[self.id]["last_id"] = msg_id

    def get_last(self):
        return self.get("last_id")

    # ------------------------------------

    async def get_data(self, user_id):
        bot = await db.get_bot(user_id)
        k, filters = self, await db.get_filters(user_id)
        size, configs = None, await db.get_configs(user_id)

        if configs['duplicate']:
            duplicate = [configs['db_uri'], self.TO]
        else:
            duplicate = False

        button = parse_buttons(configs['button'] if configs['button'] else '')

        if configs['file_size'] != 0:
            size = [configs['file_size'], configs['size_limit']]

        return (
            bot,
            configs['caption'],
            configs['forward_tag'],
            {
                'chat_id': k.FROM,
                'limit': k.limit,
                'offset': k.get_last(),   # auto-resume offset
                'filters': filters,
                'keywords': configs['keywords'],
                'media_size': size,
                'extensions': configs['extension'],
                'skip_duplicate': duplicate
            },
            configs['protect'],
            button
        )


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m"
    seconds = int(seconds)
    result += f"{seconds}s"
    return result
