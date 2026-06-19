from sugi.gpu import RenderTargetPool

class WebGLBackend:
    def __init__(self) -> None:
        self.targets = RenderTargetPool()
