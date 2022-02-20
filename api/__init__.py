from .auth import bp as auth
from flask import Blueprint

bp = Blueprint('api', __name__)
bp.register_blueprint(auth, url_prefix='/auth')
