from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder="./templates")

from main_app.admin import routes
