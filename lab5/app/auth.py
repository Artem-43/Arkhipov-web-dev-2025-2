from flask import Blueprint, Flask, render_template, session, request, url_for, redirect, flash, abort
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .db_instance import db
from functools import wraps

ROLE_PERMISSIONS = {
    'admin': {'view_logs', 'create_users', 'edit_users', 'view_profile', 'delete_users'},
    'user': {'edit_users_own', 'view_profile_own', 'view_logs_own'}
}

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

def check_rights(*permissions):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user_role = getattr(current_user, 'role', 'user')
            role_perms = ROLE_PERMISSIONS.get(user_role, set())

            # Проверяем, есть ли хотя бы одно из прав
            has_permission = any(perm in role_perms for perm in permissions)
            if not has_permission:
                flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                return redirect(url_for('index'))

            # Если у пользователя нет глобального права, но есть *_own — делаем проверку на владельца
            for perm in permissions:
                if perm in role_perms and perm.endswith('_own'):
                    user_id = kwargs.get('user_id')
                    if user_id is not None and user_id != current_user.id:
                        flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                        return redirect(url_for('index'))

            return view(*args, **kwargs)
        return wrapped_view
    return decorator


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

    @property
    def role(self):
        role = role_repository.get_by_id(self.role_id)
        return role['name'] if role else 'user'

    @property
    def permissions(self):
        return ROLE_PERMISSIONS.get(self.role, set())


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
