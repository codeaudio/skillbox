from dataclasses import dataclass


@dataclass(slots=True)
class Email:
    to: str
    context: dict
    username: str = None
