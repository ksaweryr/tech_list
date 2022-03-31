from flask import Blueprint, g, render_template

bp = Blueprint('user', __name__)
# wanted to ensure that every route in this blueprint starts with username,
# couldn't come up with a better way to do this
bp.route = lambda rule, **options: Blueprint.route(bp, '/<username>' + rule, **options)


@bp.get('/technologies')
def technologies(username):
    return render_template('technologies.html', author=username, editable=g.user.username == username)
