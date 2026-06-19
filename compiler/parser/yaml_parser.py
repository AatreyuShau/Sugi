from sugi.compiler import _simple_yaml_load
try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    yaml = None

def parse_yaml_scene(source: str):
    return yaml.safe_load(source) if yaml is not None else _simple_yaml_load(source)
