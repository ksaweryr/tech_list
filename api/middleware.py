from .utils import error
from flask import g, request
from functools import wraps
from typing import Callable, Iterable


class allowed_content_types:
    def __init__(self, accepted: Iterable[str]):
        self.accepted = accepted

    def __call__(self, f: Callable) -> Callable:
        @wraps(f)
        def inner(*args, **kwargs):
            # startswith is used instead of __eq__ since multipart
            # content types include bound info which can be virtually any value
            if (
                request.content_type is not None
                and any(map(request.content_type.startswith, self.accepted))
            ):
                return f(*args, **kwargs)

            return error(
                f'Unsupported content type {request.content_type}. '
                f'Accepted content types are: {", ".join(self.accepted)}'
            ), 400

        return inner


def login_required(f: Callable) -> Callable:
    @wraps(f)
    def inner(*args, **kwargs):
        if g.user is None:
            return error('You must be authorized to perform this action'), 401

        return f(*args, **kwargs)

    return inner
