SUPPORTED_EMITTERS = {"rain","snow","leaves","embers","dust","fireflies","sparks","smoke"}

def emitter_defaults(effect: str) -> dict[str, float | str]:
    if effect not in SUPPORTED_EMITTERS:
        raise ValueError(f"unsupported emitter: {effect}")
    return {"effect": effect, "rate": 60.0, "lifetime": 2.0, "gravity": 0.0, "wind": 0.0}
