from ..db import DbConnector, get_technology_creator
from .middleware import login_required
from flask import Blueprint, g, render_template

bp = Blueprint('technology', __name__)


@bp.get('/<int:tid>')
def get_single(tid):
    return render_template('single.html', tid=tid)


@bp.get('/create')
@login_required
def create():
    return render_template('create_or_update.html', action='create')


@bp.get('/edit/<int:tid>')
@login_required
def edit(tid):
    with DbConnector() as conn:
        if (
            not g.user.admin
            and get_technology_creator(conn.cursor(), tid) != g.user.uid
        ):
            return 'You don\'t have permission to modify this record', 403
        
        data = conn.execute('SELECT name, description, link FROM technology WHERE tid = ?;', (tid,)).fetchone()
    
    return render_template('create_or_update.html', action='update', data=data, tid=tid)