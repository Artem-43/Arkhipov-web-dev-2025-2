import pytest
from app.form_errors import validate_user_data


def test_valid_user_data():
    data = {
        'first_name': 'Иван',
        'last_name': 'Петров',
        'username': 'Ivan123',
        'password': 'Qwerty123'
    }
    errors = validate_user_data(data)
    assert errors == {}



def test_empty_username():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': '',
        'password': 'Password1'
    }
    errors = validate_user_data(data)
    assert 'Логин не может быть пустым.' in errors['username']


def test_short_username():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Us',
        'password': 'Password1'
    }
    errors = validate_user_data(data)
    assert 'Логин должен быть не короче 5 символов и содержать только латинские буквы и цифры.' in errors['username']


def test_rus_username():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Юзернейм',
        'password': 'Password1'
    }
    errors = validate_user_data(data)
    assert 'Логин должен быть не короче 5 символов и содержать только латинские буквы и цифры.' in errors['username']


def test_empty_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': ''
    }
    errors = validate_user_data(data)
    assert 'Пароль не может быть пустым.' in errors['password']


def test_short_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': 'Pas1'
    }
    errors = validate_user_data(data)
    assert 'Пароль должен быть от 8 до 128 символов.' in errors['password']


def test_no_capital_letter_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': 'password1'
    }
    errors = validate_user_data(data)
    assert 'Пароль должен содержать хотя бы одну заглавную букву.' in errors['password']


def test_no_lowercase_letter_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': 'PASSWORD1'
    }
    errors = validate_user_data(data)
    assert 'Пароль должен содержать хотя бы одну строчную букву.' in errors['password']


def test_no_number_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': 'Password'
    }
    errors = validate_user_data(data)
    assert 'Пароль должен содержать хотя бы одну цифру.' in errors['password']


def test_with_enter_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': ' Pas123Pds34'
    }
    errors = validate_user_data(data)
    assert 'Пароль не должен содержать пробелов.' in errors['password']


def test_with_invalid_character_password():
    data = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Username',
        'password': 'Pas123人Pds34'
    }
    errors = validate_user_data(data)
    assert 'Пароль содержит недопустимые символы.' in errors['password']


