import re

def validate_user_data(data, check_username_password=True):
    errors = {}

    if not data.get('first_name'):
        errors['first_name'] = 'Имя не может быть пустым.'

    if not data.get('last_name'):
        errors['last_name'] = 'Фамилия не может быть пустой.'

    if check_username_password:
        username = data.get('username', '')
        password = data.get('password', '')

        if not username:
            errors['username'] = 'Логин не может быть пустым.'
        elif not re.fullmatch(r'[A-Za-z0-9]{5,}', username):
            errors['username'] = 'Логин должен быть не короче 5 символов и содержать только латинские буквы и цифры.'

        if not password:
            errors['password'] = 'Пароль не может быть пустым.'
        else:
            if len(password) < 8 or len(password) > 128:
                errors['password'] = 'Пароль должен быть от 8 до 128 символов.'
                return errors
            if not re.search(r'[A-ZА-Я]', password):
                errors['password'] = 'Пароль должен содержать хотя бы одну заглавную букву.'
                return errors
            if not re.search(r'[a-zа-я]', password):
                errors['password'] = 'Пароль должен содержать хотя бы одну строчную букву.'
                return errors
            if not re.search(r'\d', password):
                errors['password'] = 'Пароль должен содержать хотя бы одну цифру.'
                return errors
            if re.search(r'\s', password):
                errors['password'] = 'Пароль не должен содержать пробелов.'
                return errors
            if not re.fullmatch(r'[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+\(\)\[\]\{\}><\/\\|"\'.,:;]+', password):
                errors['password'] = 'Пароль содержит недопустимые символы.'
                return errors

    return errors