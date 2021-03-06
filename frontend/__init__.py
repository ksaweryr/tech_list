from .auth import bp as auth
from .technology import bp as technology
from .user import bp as user
from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__)
bp.register_blueprint(auth, url_prefix='/')
bp.register_blueprint(technology, url_prefix='/technology')
bp.register_blueprint(user, url_prefix='/user')


@bp.get('/')
def index():
    return render_template('technologies.html')
