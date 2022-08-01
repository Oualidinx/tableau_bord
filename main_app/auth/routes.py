from flask import url_for, redirect, request, render_template, flash, abort
from main_app.auth import auth_bp
from main_app.models import User
from flask_login import login_required, login_user, logout_user, current_user
from main_app.forms import LoginForm, RegisterForm
from werkzeug.security import check_password_hash, generate_password_hash
from main_app import database


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).filter_by(is_deleted=0).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=False)
                nex_page = request.args.get('next')
                if nex_page:
                    return redirect(nex_page)
                if user.role == "Master":
                    return redirect(url_for('admin_bp.index'))
                return redirect(url_for('employee_bp.index'))
            else:
                flash('Veuillez vérifier les informations', 'danger')
                return redirect(url_for('auth_bp.login'))
        else:
            flash('veuillez verifier les informations', 'danger')
            return redirect(url_for('auth_bp.login'))
    return render_template('login.html', form=form)


@auth_bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))
