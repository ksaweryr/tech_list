from .auth import bp as auth
from .middleware import reject_non_json
from flask import Blueprint

bp = Blueprint('api', __name__)
bp.before_request(reject_non_json)
bp.register_blueprint(auth, url_prefix='/auth')
