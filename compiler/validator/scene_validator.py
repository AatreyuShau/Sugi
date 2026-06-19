from sugi.scene import AstNode, SceneAst

def validate_scene(ast: SceneAst) -> tuple[str, ...]:
    seen: set[str] = set()
    diagnostics: list[str] = []
    def visit(node: AstNode) -> None:
        if node.id in seen:
            diagnostics.append(f"duplicate node id: {node.id}")
        seen.add(node.id)
        if not node.type:
            diagnostics.append(f"node {node.id} is missing type")
        for component in node.components:
            if "type" not in component:
                diagnostics.append(f"node {node.id} has component without type")
        for child in node.children:
            visit(child)
    visit(ast.root)
    return tuple(diagnostics)
