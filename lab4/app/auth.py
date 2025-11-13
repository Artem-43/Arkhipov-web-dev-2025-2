from flask import Blueprint, Flask, render_template, session, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from .repositories.user_repository import UserRepository
from .db_instance import db

user_repository = UserRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пройдите аутентификацию, чтобы получить доступ к запрашиваемой странице.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, username, role_id):
        self.id = user_id
        self.username = username
        self.role_id = role_id

    def is_admin(self):
        return self.role_id == 1


@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user['id'], user['username'], user['role_id'])
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = user_repository.get_by_username_and_password(username, password)

        if user is not None:
            flash('Авторизация прошла успешно', 'success')
            login_user(User(user['id'], user['username'], user['role_id']), remember=remember_me)
            next_url = request.args.get('next', url_for('index'))
            return redirect(next_url)
        flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно прошли деаутентификацию!', 'success')
    return redirect(url_for('users.index'))
