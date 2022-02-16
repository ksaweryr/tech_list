from secrets import token_hex


def setup_dotenv():
    envs = {
        'TOKEN': token_hex(),
        'ADMIN_PASSWORD': token_hex()
    }

    with open('.env', 'wt') as f:
        f.write('\n'.join(map(lambda x: f'{x[0]}={x[1]}', envs.items())))
