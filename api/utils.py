from flask import jsonify, Response


def error(msg: str) -> Response:
    return jsonify({'error': msg})
