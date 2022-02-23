from argon2 import PasswordHasher
from sqlite3 import Connection, Cursor
from typing import Any


class DbConnector(Connection):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__('db.sqlite3', *args, **kwargs)
        c = self.cursor()
        c.execute('PRAGMA foreign_keys = ON;').close()


def create_user(c: Cursor, username: str, password: str,
                *, admin: bool = False) -> None:
    ph = PasswordHasher()
    hashed = ph.hash(password)
    c.execute(
        'INSERT INTO app_user(username, password, admin) VALUES(?, ?, ?);',
        (username, hashed, admin)
    )


def get_technology_creator(c: Cursor, tid: int) -> str | None:
    (creator,) = c.execute('''
        SELECT u.username
        FROM technology t
        NATURAL JOIN app_user u
        WHERE t.tid = ?;''',
        (tid,)).fetchone() or (None,)

    return creator
