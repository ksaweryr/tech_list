from ..db import DbConnector, get_technology_creator
from .middleware import allowed_content_types, login_required
from .utils import error, parse_or_default
from flask import Blueprint, g, jsonify, request
from io import BytesIO
from json.decoder import JSONDecodeError
from operator import itemgetter
from pathlib import Path
from PIL import Image
from typing import Tuple
from uuid import uuid4
from werkzeug.datastructures import FileStorage

import imghdr
import json

bp = Blueprint('technology', __name__)


def save_logo(logo: FileStorage | None) -> Tuple[bool, str]:
    if logo is None:
        return False, 'Missing logo'
    data = logo.read()
    if imghdr.what('', h=data) not in ('bmp', 'jpeg', 'png', 'webp'):
        return False, 'Invalid logo format'

    filename = f'{uuid4()}.png'

    img = Image.open(BytesIO(data))
    img.save(Path('uploads') / filename)
    img.close()

    return True, filename


@bp.post('')
@allowed_content_types(['multipart/form-data'])
@login_required
def create():
    body = request.form.get('body')
    logo = request.files.get('logo')

    # validate body
    if body is None:
        return error('Missing form-data field `body`'), 400

    try:
        body = json.loads(body)
    except JSONDecodeError:
        return error('Field `body` must be a valid JSON object'), 400

    if len(missing_fields := [
        x for x in ('name', 'description', 'link') if x not in body
    ]) > 0:
        return error(f'Missing fields: {", ".join(missing_fields)}'), 400

    for field, mlen in zip(('name', 'description'), (20, 200)):
        if len(body[field]) > mlen:
            return (error(f'{field} musn\'t be longer than {mlen} characters'),
                    400)

    name, description, link = itemgetter('name', 'description', 'link')(body)

    if not link.startswith('http'):
        link = 'http://' + link

    success, msg = save_logo(logo)
    if not success:
        return error(msg), 400
    else:
        filename = msg

    with DbConnector() as conn:
        c = conn.cursor()
        (tid,) = c.execute('''
            INSERT INTO technology(uid, name, description, logo_filename, link)
            VALUES((SELECT uid FROM app_user WHERE username = ?), ?, ?, ?, ?)
            RETURNING tid;
        ''', (g.user.username, name, description, filename, link)).fetchone()

    return jsonify({'tid': tid})


@bp.get('')
def get_list():
    ORDERINGS = ('creation_date', 'likes')
    COLUMNS = (
        't.tid', 't.logo_filename', 't.name', 't.description',
        't.link', 't.creation_date', 't.likes', 'u.username'
    )
    offset = parse_or_default(request.args.get('off'), 0)
    count = parse_or_default(request.args.get('size'), 10)
    ordering = request.args.get('ord', 'creation_date')

    if not ((ordering[0] == '-' and ordering[1:] in ORDERINGS)
            or ordering in ORDERINGS):
        ordering = 'creation_date'

    with DbConnector() as conn:
        c = conn.cursor()

        rows = c.execute(f'''
            SELECT {", ".join(COLUMNS)}
            FROM technology t NATURAL JOIN app_user u
            ORDER BY ? LIMIT ? OFFSET ?;''',
            (ordering, count, offset)).fetchall()

        more = c.execute(
            'SELECT COUNT(*) FROM technology'
            ).fetchone()[0] > offset + count

    return jsonify({
        'results': [
            dict(zip(map(itemgetter(slice(2, None)), COLUMNS), row))
            for row in rows
        ],
        'more': more
    })


@bp.get('/<int:tid>')
def get_single(tid):
    COLUMNS = (
        't.logo_filename', 't.name', 't.description', 't.link',
        't.creation_date', 't.update_date', 't.likes', 'u.username'
    )
    with DbConnector() as conn:
        c = conn.cursor()
        row = c.execute(f'''
        SELECT {", ".join(COLUMNS)}
        FROM technology t NATURAL JOIN app_user u
        WHERE tid = ?;''', (tid,)).fetchone()

    if row is None:
        return error('Technology not found'), 404

    return jsonify(dict(zip(map(itemgetter(slice(2, None)), COLUMNS), row)))


@bp.patch('/<int:tid>')
@allowed_content_types(['multipart/form-data', 'application/json'])
@login_required
def update(tid):
    UPDATABLES = ('name', 'description', 'link')
    with DbConnector() as conn:
        if (not g.user.admin
            and get_technology_creator(conn.cursor(), tid) != g.user.username):
            return (error('You don\' have permission to modify this record'),
                    403)

    if request.content_type.startswith('multipart/form-data'):
        logo = request.files.get('logo')
        try:
            body: dict[str, str] = json.loads(request.form.get('body', ''))
        except JSONDecodeError:
            return error('Field `body` must be a valid JSON object'), 400
    else:   # Content-type: application/json
        logo = None
        body = request.json

    body = {k: v for k, v in body.items() if k in UPDATABLES}

    if logo is not None:
        success, msg = save_logo(logo)
        if not success:
            return error(msg), 400
        else:
            body['logo_filename'] = msg

    items = body.items()

    with DbConnector() as conn:
        c = conn.cursor()
        c.execute(f'''
        UPDATE technology
        SET {", ".join(map(lambda x: f"{x[0]} = ?", items))}
        WHERE tid = ?;''', [*map(itemgetter(1), items), tid])

    return jsonify({'msg': 'ok'})


@bp.delete('/<int:tid>')
@login_required
def delete(tid):
    with DbConnector() as conn:
        c = conn.cursor()
        if (not g.user.admin
            and get_technology_creator(c, tid) != g.user.username):
            return (error('You don\' have permission to modify this record'),
                    403)

        c.execute('''DELETE FROM technology WHERE tid = ?;''', (tid,))

    return jsonify({'msg': 'ok'})
