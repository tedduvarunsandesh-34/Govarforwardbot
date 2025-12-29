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
            "FROM": From, "TO": to, "skip": skip, "limit": limit,
            "fetched": skip, "total_files": 0, "filtered": 0, "deleted": 0,
            "duplicate": 0, "total": limit, "start": tm.time(),
            "batch_size": 100, "batch_delay": 10, "last_id": skip, "mode": "batch"
        }
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.data.get(self.id)
        if not values: return None
        if not full: return values.get(value)
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
        self.data[self.id][key] = self.get(key, 0) + value

    def divide(self, no, by):
        return int(no) / (by if int(by) != 0 else 1)

    def save_last(self, msg_id):
        self.data[self.id]["last_id"] = msg_id

    def get_last(self):
        return self.get("last_id")

    async def get_data(self, user_id):
        bot = await db.get_bot(user_id)
        configs = await db.get_configs(user_id)
        button = parse_buttons(configs['button'] if configs['button'] else '')
        return bot, configs['caption'], configs['forward_tag'], button, configs['protect']

def get_readable_time(seconds: int) -> str:
    (days, r) = divmod(seconds, 86400)
    (hours, r) = divmod(r, 3600)
    (mins, secs) = divmod(r, 60)
    return f"{int(days)}d {int(hours)}h {int(mins)}m {int(secs)}s"
