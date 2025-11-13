from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
import mysql.connector as connector
from .form_errors import validate_user_data

from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .db_instance import db

user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def index():
    return render_template('users/index.html', users=user_repository.all())

@bp.route('/<int:user_id>')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user['role_id'])
    return render_template('users/show.html', user_data=user, user_role=getattr(user_role, 'name', ''))

@bp.route('/new', methods=['POST', 'GET'])
@login_required
def new():
    user_data = {}
    errors = {}
    if request.method == 'POST':
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        if user_data['role_id']:
            user_data['role_id'] = int(user_data['role_id'])

        errors = validate_user_data(user_data)

        if not errors:
            try:
                user_repository.create(**user_data)
                flash('Учётная запись успешно создана', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при создании записи.', 'danger')
                db.connect().rollback()

    return render_template('users/new.html', user_data=user_data, errors=errors, roles=role_repository.all())

@bp.route('/<int:user_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(user_id):
    user_repository.delete(user_id)
    flash('Учётная запись успешно удалена', 'success')
    return redirect(url_for('users.index'))


@bp.route('/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
def edit(user_id):
    errors = {}
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        update_data = {
            'first_name': request.form.get('first_name') or None,
            'middle_name': request.form.get('middle_name') or None,
            'last_name': request.form.get('last_name') or None,
            'role_id': int(request.form.get('role_id')) if request.form.get('role_id') else None
        }

        errors = validate_user_data({**user, **update_data}, check_username_password=False)

        if not errors:
            try:
                user_repository.update(
                    user_id=user_id,
                    first_name=update_data['first_name'],
                    middle_name=update_data['middle_name'],
                    last_name=update_data['last_name'],
                    role_id=update_data['role_id']
                )
                flash('Учётная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при изменении записи.', 'danger')
                db.connect().rollback()

        user.update(update_data)

    return render_template('users/edit.html', user_data=user, errors=errors, roles=role_repository.all())

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    errors = {}
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not user_repository.check_password(current_user.id, old_password):
            errors['old_password'] = 'Неверный старый пароль'

        validation_errors = validate_user_data({'password': new_password}, check_username_password=True)
        if 'password' in validation_errors:
            errors['new_password'] = validation_errors['password']

        if new_password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'

        if not errors:
            try:
                user_repository.update_password(current_user.id, new_password)
                flash('Пароль успешно изменён!', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Ошибка при изменении пароля.', 'danger')
                db.connect().rollback()

    return render_template('users/change_password.html', errors=errors)