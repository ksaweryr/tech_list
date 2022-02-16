from argon2 import PasswordHasher
from dotenv import load_dotenv
from os import environ

import sqlite3


def setup_db():
    load_dotenv()
    ph = PasswordHasher()
    hash = ph.hash(environ['ADMIN_PASSWORD'])

    with sqlite3.connect('db.sqlite3') as conn:
        c = conn.cursor()
        c.execute(
            'INSERT INTO app_user(username, password, admin) VALUES(?, ?, ?);',
            ('admin', hash, True)
        )
        conn.commit()
