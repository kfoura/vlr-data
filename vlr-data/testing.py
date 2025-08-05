import cache

cache = cache.Cache()

cache.set("example key", "example value")

print(cache.get("example key"))
print(cache.get("unexistent"))