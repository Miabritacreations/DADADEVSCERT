from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
web_bp = Blueprint("web", __name__)

