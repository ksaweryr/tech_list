from .auth import bp as auth
from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__)
bp.register_blueprint(auth, url_prefix='/')


@bp.get('/')
def index():
    return render_template('index.html')
