from ..db import DbConnector, get_technology_creator
from .middleware import allowed_content_types, login_required
from .utils import error, parse_or_default
from flask import Blueprint, g, jsonify, request
from io import BytesIO
from json.decoder import JSONDecodeError
from operator import itemgetter
from pathlib import Path
from PIL import Image
from sqlite3 import IntegrityError
from typing import Tuple
from uuid import uuid4
from werkzeug.datastructures import FileStorage

import imghdr
import json
import os

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

    try:
        with DbConnector() as conn:
            c = conn.cursor()
            (tid,) = c.execute('''
                INSERT INTO technology(
                    uid, name, description, logo_filename, link
                )
                VALUES(
                    ?, ?, ?, ?, ?
                )
                RETURNING tid;
            ''', (g.user.uid, name, description, filename, link)
            ).fetchone()
    except IntegrityError:
        os.remove(Path('uploads') / filename)
        return error('Technology with this name already exists'), 403

    return jsonify({'tid': tid})


@bp.get('')
def get_list():
    ORDERINGS = ('creation_date', 'likes')
    COLUMNS = (
        't.tid', 't.logo_filename', 't.name', 't.description',
        't.link', 't.creation_date', 't.update_date', 't.likes', 'u.username'
    )
    offset = parse_or_default(request.args.get('off'), 0)
    count = parse_or_default(request.args.get('size'), 10)
    author = request.args.get('author')
    ordering = request.args.get('ord', 'creation_date')

    if ordering[0] == '-':
        dir = 'DESC'
        ordering = ordering[1:]
    else:
        dir = 'ASC'

    if ordering not in ORDERINGS:
        ordering = 'creation_date'

    secondary_ordering = 'creation_date' if ordering == 'likes' else 'likes'

    with DbConnector() as conn:
        c = conn.cursor()

        if author is not None:
            author_exists = c.execute('SELECT * FROM app_user WHERE username = ?;', (author,)).fetchone() is not None

            if not author_exists:
                return error(f'User {author} doesn\'t exist'), 404

        rows = c.execute(f'''
            SELECT {', '.join(COLUMNS)},
            EXISTS(SELECT 1 FROM liked WHERE tid = t.tid AND uid = :uid)
            FROM technology t NATURAL JOIN app_user u
            {'NATURAL JOIN app_user WHERE username = :author' if author is not None else ''}
            ORDER BY {ordering} {dir}, {secondary_ordering} {dir}
            LIMIT :count OFFSET :offset;
        ''', {
                'uid': g.user.uid if g.user is not None else -1,
                'count': count,
                'offset': offset,
                'author': author
            }).fetchall()

        more = c.execute(f'''
            SELECT COUNT(*) FROM technology
            {'NATURAL JOIN app_user WHERE username = :author' if author is not None else ''};
        ''', {'author': author}).fetchone()[0] > offset + count

    return jsonify({
        'results': [
            dict(zip((*map(itemgetter(slice(2, None)), COLUMNS), 'liked'), row))
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
            SELECT {", ".join(COLUMNS)},
            EXISTS(SELECT 1 FROM liked WHERE tid = :tid AND uid = :uid )
            FROM technology t NATURAL JOIN app_user u
            WHERE tid = :tid;
        ''', {'tid': tid, 'uid': g.user.uid if g.user is not None else -1}
        ).fetchone()

    if row is None:
        return error('Technology not found'), 404

    return jsonify(dict(zip((*map(itemgetter(slice(2, None)), COLUMNS), 'liked'), row)))


@bp.patch('/<int:tid>')
@allowed_content_types(['multipart/form-data', 'application/json'])
@login_required
def update(tid):
    UPDATABLES = ('name', 'description', 'link')
    with DbConnector() as conn:
        if (
            not g.user.admin
            and get_technology_creator(conn.cursor(), tid) != g.user.uid
        ):
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

    for field, mlen in zip(('name', 'description'), (20, 200)):
        if body.get(field) is not None and len(body[field]) > mlen:
            return (error(f'{field} musn\'t be longer than {mlen} characters'),
                    400)

    if logo is not None:
        success, msg = save_logo(logo)
        if not success:
            return error(msg), 400
        else:
            body['logo_filename'] = msg

    items = body.items()

    with DbConnector() as conn:
        try:
            c = conn.cursor()
            (old_filename,) = c.execute('''
                SELECT logo_filename
                FROM technology
                WHERE tid = ?;
            ''', (tid,)).fetchone()
            c.execute(f'''
                UPDATE technology
                SET {", ".join(map(lambda x: f"{x[0]} = ?", items))}
                WHERE tid = ?;
            ''', [*map(itemgetter(1), items), tid])

            if body.get('logo_filename') is not None:
                os.remove(Path('uploads') / old_filename)
        except IntegrityError:
            os.remove(Path('uploads') / body['logo_filename'])
            return error('Technology with this name already exists')

    return jsonify({'msg': 'ok'})


@bp.delete('/<int:tid>')
@login_required
def delete(tid):
    with DbConnector() as conn:
        c = conn.cursor()
        if (
            not g.user.admin
            and get_technology_creator(c, tid) != g.user.uid
        ):
            return (error('You don\' have permission to modify this record'),
                    403)

        (filename,) = c.execute('''
            DELETE FROM technology
            WHERE tid = ?
            RETURNING logo_filename;
        ''', (tid,)).fetchone()

        os.remove(Path('uploads') / filename)

    return jsonify({'msg': 'ok'})


@bp.post('/like/<int:tid>')
@login_required
def like(tid):
    uid = g.user.uid
    with DbConnector() as conn:
        c = conn.cursor()
        (liked,) = c.execute('''
            SELECT COUNT(*) FROM liked WHERE tid = ? AND uid = ?;
        ''', (tid, uid)).fetchone()
        liked = bool(liked)

        if not liked:
            c.execute('''
                INSERT INTO liked(tid, uid)
                VALUES(?, ?);
            ''', (tid, uid))
        else:
            c.execute('''
                DELETE FROM liked WHERE tid = ? AND uid = ?;
            ''', (tid, uid))

    return jsonify({'state': not liked})
