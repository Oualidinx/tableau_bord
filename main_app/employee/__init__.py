from flask import Blueprint

employee_bp = Blueprint('employee_bp', __name__, url_prefix='/employee', template_folder="/templates")

from main_app.employee import routes
