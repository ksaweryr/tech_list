from flask import jsonify, Response


def error(msg: str) -> Response:
    return jsonify({'error': msg})


def parse_or_default(s: str | None, default: int) -> int:
    if s is not None and s.isdigit():
        return int(s)
    else:
        return default
