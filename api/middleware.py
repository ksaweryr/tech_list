from .utils import error
from flask import request


def reject_non_json():
    if not request.is_json:
        return error('only json format is supported'), 400
