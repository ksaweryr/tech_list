from .api import bp as api
from .frontend import bp as frontend
from .utils import User
from dotenv import load_dotenv
from flask import Flask, g, request
from jwt.exceptions import InvalidTokenError
from os import environ

import jwt

load_dotenv()

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(frontend, url_prefix='/')


@app.before_request
def set_g_user():
    g.user = None
    token = request.cookies.get('token')

    if token is None:
        return

    try:
        token = jwt.decode(token, environ['TOKEN'], algorithms=['HS256'],
            options={
                'require': ['username', 'admin', 'iat']
            }
        )
    except InvalidTokenError:
        return

    g.user = User(token['username'], token['admin'])


@app.get('/ping')
def ping_pong():
    return 'Pong!'
