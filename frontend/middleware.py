from flask import g, redirect, url_for
from functools import wraps
from typing import Callable


def login_required(f: Callable) -> Callable:
    @wraps(f)
    def inner(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('frontend.auth.login'))

        return f(*args, **kwargs)

    return inner
