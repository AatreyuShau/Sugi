from sugi.assets import AssetCache


def resolve_shader(path: str, cache: AssetCache | None = None):
    cache = cache or AssetCache()
    return cache.load_shader(path)


def resolve_material(name: str, vertex: str, fragment: str, uniforms=None, cache: AssetCache | None = None):
    cache = cache or AssetCache()
    return cache.load_material(name, vertex, fragment, uniforms)
