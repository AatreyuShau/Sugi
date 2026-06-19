from sugi.vm import SugiVM

def play(vm: SugiVM, node: int, animation: str) -> None:
    vm.play_animation(node, animation)
