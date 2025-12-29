# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
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
            "batch": True,
            "batch_size": 100,
            "batch_delay": 10,
            "last_id": skip,
            "paused": False,
            "mode": "batch"
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

    def set(self, key, value):
        if self.id in self.data:
            self.data[self.id][key] = value

    def add(self, key=None, value=1, time=False):
        if time:
            self.data[self.id]["start"] = tm.time()
            return
        self.data[self.id][key] = self.get(key) + value

    def divide(self, no, by):
        by = 1 if int(by) == 0 else by 
        return int(no) / by 

    def save_last(self, msg_id):
        self.data[self.id]["last_id"] = msg_id

    def get_last(self):
        return self.get("last_id")

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
                'offset': k.get_last(),
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
    if days: result += f"{int(days)}d"
    (hours, remainder) = divmod(remainder, 3600)
    if hours: result += f"{int(hours)}h"
    (minutes, seconds) = divmod(remainder, 60)
    if minutes: result += f"{int(minutes)}m"
    result += f"{int(seconds)}s"
    return result
