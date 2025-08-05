import os
import redis
import json

class Cache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", None)
        if redis_url:
            self.client = redis.Redis.from_url(redis_url)
            self.use_redis = True
        else:
            self.client = {}
            self.use_redis = False
    
    def get(self, key):
        if self.use_redis:
            val = self.client.get(key)
            return json.loads(val) if val else None
        return self.client.get(key)
    
    def set(self, key, val, expires=300):
        if self.use_redis:
            self.client.set(key, json.dumps(val), ex=expires)
        else:
            self.client[key] = val