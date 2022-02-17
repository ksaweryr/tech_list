from db import create_user, DbConnector
from dotenv import load_dotenv
from os import environ
from secrets import token_hex


def setup_dotenv():
    envs = {
        'TOKEN': token_hex(),
        'ADMIN_PASSWORD': token_hex()
    }

    with open('.env', 'wt') as f:
        f.write('\n'.join(map(lambda x: f'{x[0]}={x[1]}', envs.items())))


def setup_db():
    load_dotenv()

    with DbConnector('db.sqlite3') as conn:
        c = conn.cursor()
        create_user(c, 'admin', environ['ADMIN_PASSWORD'], admin=True)


setup_dotenv()
setup_db()
