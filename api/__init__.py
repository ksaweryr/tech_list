from .auth import bp as auth
from .technology import bp as tech
from flask import Blueprint

bp = Blueprint('api', __name__)
bp.register_blueprint(auth, url_prefix='/auth')
bp.register_blueprint(tech, url_prefix='/technology')
