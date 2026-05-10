from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_login import login_user, logout_user
from models import User
from extensions import db
from forms_auth import LoginForm, RegisterForm


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)  # 🔥 ESTO ES LO IMPORTANTE

            flash('Login correcto', 'success')
            #return redirect(url_for('index'))
            return redirect(url_for('camaras'))

        flash('Credenciales incorrectas', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role='USER'
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.login'))

'''@auth_bp.route('/logout')
def logout():
    #session.clear()
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))
'''
