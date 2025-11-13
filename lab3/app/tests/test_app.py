import pytest
from flask import session, url_for
from flask_login import current_user
from app import app as flask_app, get_users

@pytest.fixture
def client():
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "292f3f43316d560603697f3b966fdc774357fd30111466462412bf5b405417f2"
    })
    with flask_app.test_client() as client:
        with client.session_transaction() as session:
            session.clear()
        yield client


def decode_response(response):
    return response.data.decode('utf-8')


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    decoded = decode_response(response)
    assert "Задание к 3-ей лабораторной работе" in decoded


def test_counter_session(client):
    response = client.get('/counter')
    with client.session_transaction() as sess:
        assert sess.get('counter') == 1

    response = client.get('/counter')
    with client.session_transaction() as sess:
        assert sess.get('counter') == 2


def test_successful_login(client):
    user = get_users()[0]
    response = client.post('/login', data={
        'username': user['login'],
        'password': user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    decoded = decode_response(response)
    assert "Вы успешно прошли аутентификацию" in decoded


def test_failed_login(client):
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wrong'
    })
    assert response.status_code == 200
    decoded = decode_response(response)
    assert "Пользователь не найден" in decoded


def test_secret_page_access_authenticated(client):
    user = get_users()[0]
    client.post('/login', data={
        'username': user['login'],
        'password': user['password']
    })
    response = client.get('/secret')
    assert response.status_code == 200
    decoded = decode_response(response)
    assert "Это секретная страница" in decoded


def test_secret_page_access_anonymous(client):
    response = client.get('/secret', follow_redirects=True)
    decoded = decode_response(response)
    assert "Пройдите аутентификацию" in decoded
    assert response.request.path == url_for('login')


def test_redirect_to_secret_after_login(client):
    user = get_users()[0]

    response = client.get('/secret', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

    login_url = f"{url_for('login')}?next=/secret"
    response = client.post(login_url, data={
        'username': user['login'],
        'password': user['password']
    }, follow_redirects=True)

    assert response.status_code == 200
    decoded = decode_response(response)
    assert "Задание к 3-ей лабораторной работе" in decoded

    secret_response = client.get('/secret')
    assert secret_response.status_code == 200
    assert "Это секретная страница" in decode_response(secret_response)


def test_remember_me_functionality(client):
    user = get_users()[0]
    response = client.post('/login', data={
        'username': user['login'],
        'password': user['password'],
        'remember_me': 'on'
    })
    assert 'remember_token' in response.headers.get('Set-Cookie', '')


def test_logout_functionality(client):
    user = get_users()[0]
    client.post('/login', data={
        'username': user['login'],
        'password': user['password']
    })
    response = client.get('/logout', follow_redirects=True)
    decoded = decode_response(response)
    assert "Вы успешно прошли деаутентификацию" in decoded


def test_navbar_links_authenticated(client):
    user = get_users()[0]
    client.post('/login', data={
        'username': user['login'],
        'password': user['password']
    })
    response = client.get('/')
    decoded = decode_response(response)
    assert 'href="/logout"' in decoded
    assert 'href="/secret"' in decoded
    assert 'href="/login"' not in decoded


def test_navbar_links_anonymous(client):
    response = client.get('/')
    decoded = decode_response(response)
    assert 'href="/login"' in decoded
    assert 'href="/logout"' not in decoded
    assert 'href="/secret"' not in decoded
    assert '3) "Секретная страница"' in decoded
    assert '<a class="nav-link" href="/secret">' not in decoded