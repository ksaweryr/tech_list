from .middleware import login_required
from flask import Blueprint, render_template

bp = Blueprint('technology', __name__)


@bp.get('/<int:tid>')
def get_single(tid):
    return render_template('single.html', tid=tid)


@bp.get('/create')
@login_required
def create():
    return render_template('create.html')
