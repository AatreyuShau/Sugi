from sugi.assets import BUILT_IN_SHADERS, AssetCache

def resolve_shader(name: str, cache: AssetCache | None = None):
    cache = cache or AssetCache()
    return cache.load_shader(name)
