from dataclasses import dataclass


@dataclass
class User:
    username: str
    uid: int
    admin: bool
