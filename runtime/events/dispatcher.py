from sugi.vm import SugiVM

def dispatch(vm: SugiVM, node: int, event: str, payload=None):
    return vm.dispatch_event(node, event, payload)
