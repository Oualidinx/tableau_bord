from main_app import create_app, database
from flask_migrate import Migrate
from dotenv import load_dotenv
from main_app.models import *
import os
from flask import redirect, url_for
load_dotenv('.flaskenv')
app = create_app(os.environ.get('FLASK_ENV'))
m = Migrate(app=app, db=database)


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('auth_bp.login'))


@app.shell_context_processor
def make_shell_context():
    return dict(
        app=app,
        db=database,
        User=User,
        Service=Service,
        Value=Value,
        Aggregate=Aggregate
    )
