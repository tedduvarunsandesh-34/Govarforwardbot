# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import time as tm
import asyncio 
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
        # We store the 'limit' as the total count to process
        # We store 'skip' as the starting offset
        self.data[self.id] = {
            "FROM": From, 
            'TO': to, 
            'total_files': 0, 
            'skip': skip, 
            'limit': limit,
            'fetched': skip, 
            'filtered': 0, 
            'deleted': 0, 
            'duplicate': 0, 
            'total': limit + skip, # Total calculation fixed for progress bar accuracy
            'start': 0
        }
        self.get(full=True)
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.data.get(self.id)
        if not full:
           return values.get(value)
        for k, v in values.items():
            setattr(self, k, v)
        return self

    def add(self, key=None, value=1, time=False):
        if time:
          return self.data[self.id].update({'start': tm.time()})
        current_val = self.get(key)
        self.data[self.id].update({key: current_val + value}) 
    
    def divide(self, no, by):
       by = 1 if int(by) == 0 else by 
       return int(no) / by 
    
    async def get_data(self, user_id):
        # --- SPEED OPTIMIZATION: Parallel Database Fetching ---
        # Instead of waiting for DB 3 times sequentially, we fetch all at once.
        task1 = db.get_bot(user_id)
        task2 = db.get_filters(user_id)
        task3 = db.get_configs(user_id)
        
        # Run all 3 DB queries together
        bot, filters, (_, configs) = await asyncio.gather(task1, task2, task3)
        # ------------------------------------------------------
        
        size = None
        duplicate = False
        
        if configs['duplicate']:
           duplicate = [configs['db_uri'], self.TO]
        
        button = parse_buttons(configs['button'] if configs['button'] else '')
        
        if configs['file_size'] != 0:
            size = [configs['file_size'], configs['size_limit']]
            
        return bot, configs['caption'], configs['forward_tag'], {
            'chat_id': self.FROM, 
            'limit': self.limit, 
            'offset': self.skip, 
            'filters': filters,
            'keywords': configs['keywords'], 
            'media_size': size, 
            'extensions': configs['extension'], 
            'skip_duplicate': duplicate
        }, configs['protect'], button
        

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

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

