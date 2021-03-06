from ..db import create_user, DbConnector
from .middleware import allowed_content_types
from .utils import error
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, jsonify, make_response, request
from os import environ
from sqlite3 import IntegrityError
from time import time

import jwt
import re

username_pattern = re.compile(r'^[\w\d_]{4,20}$')
password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{12,64}$')

bp = Blueprint('auth', __name__)


@bp.before_request
@allowed_content_types(['application/json'])
def _(): pass


def create_token(username: str, uid: int, admin: bool) -> str:
    return jwt.encode(
        {'username': username, 'uid': uid, 'admin': admin, 'iat': int(time())},
        environ['TOKEN'], algorithm='HS256'
    )


@bp.post('/register')
def register():
    body = request.json
    username = body.get('username')
    password = body.get('password')

    if username is None or password is None:
        return error('Body must contain username and password'), 400

    if not username_pattern.match(username):
        return error('Username must consist of 4-20 letters, digits or underscores'), 400

    if not password_pattern.match(password):
        return error('Password must consist of 12-64 characters and contain at least one uppercase letter, lowercase letter and a digit'), 400

    with DbConnector() as conn:
        c = conn.cursor()
        try:
            uid = create_user(c, username, password)
        except IntegrityError:
            return error('User already exists'), 402

    resp = make_response(jsonify({'msg': 'ok'}))
    resp.set_cookie('token', create_token(username, uid, False))

    return resp


@bp.post('/login')
def login():
    body = request.json
    username = body.get('username')
    password = body.get('password')

    if username is None or password is None:
        return error('Body must contain username and password'), 400

    with DbConnector() as conn:
        c = conn.cursor()
        (hashed, uid, admin) = c.execute(
            'SELECT password, uid, admin FROM app_user WHERE username=?;',
            (username,)
        ).fetchone() or (None, None, None)

    if hashed is None:
        return error('User doesn\'t exist'), 400

    ph = PasswordHasher()
    try:
        ph.verify(hashed, password)
    except VerifyMismatchError:
        return error('Invalid password'), 400

    resp = make_response(jsonify({'msg': 'ok'}))
    resp.set_cookie('token', create_token(username, uid, bool(admin)))

    return resp
