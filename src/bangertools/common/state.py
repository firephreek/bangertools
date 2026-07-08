from dataclasses import dataclass


@dataclass
class AppState:
    verbose: bool = False


appstate = AppState()
