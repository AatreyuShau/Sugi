from sugi.assets import AssetCache

def load_texture(source: str, cache: AssetCache | None = None):
    cache = cache or AssetCache()
    return cache.load_image(source)
