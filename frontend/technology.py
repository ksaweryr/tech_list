from flask import Blueprint, render_template

bp = Blueprint('technology', __name__)


@bp.get('/<int:tid>')
def get_single(tid):
    return render_template('single.html', tid=tid)
