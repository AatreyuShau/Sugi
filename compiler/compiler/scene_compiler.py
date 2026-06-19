from sugi.compiler import Compiler
from sugi.scene import CompiledScene

def compile_yaml_scene(source: str) -> CompiledScene:
    return Compiler().compile_scene(source, source_format="yaml")

def compile_json_scene(source: str) -> CompiledScene:
    return Compiler().compile_scene(source, source_format="json")
