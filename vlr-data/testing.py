import cache

cache = cache.Cache()

cache.set("example key", {"more": "examples"})

print(cache.get("example key")['more'])
print(cache.get("unexistent"))