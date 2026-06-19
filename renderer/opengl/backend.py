from sugi.gpu import RenderTargetPool

class OpenGLBackend:
    def __init__(self) -> None:
        self.targets = RenderTargetPool()
