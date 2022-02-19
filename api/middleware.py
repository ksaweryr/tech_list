from .utils import error
from flask import g, request
from functools import wraps
from typing import Callable


def reject_non_json():
    if not request.is_json:
        return error('Only json format is supported'), 400


def login_required(f: Callable) -> Callable:
    @wraps(f)
    def inner(*args, **kwargs):
        if g.user is None:
            return error('You must be authorized to perform this action'), 401

        return f(*args, **kwargs)

    return inner
