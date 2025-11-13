def test_user_access_denied_for_report_users(client, existing_user_for_logs):
    user = existing_user_for_logs['user']

    login_data = {
        'username': user.username,
        'password': user.password,
        'remember_me': 'y'
    }

    response = client.get('/auth/login')
    assert response.status_code == 200

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/session_log/report/users', follow_redirects=True)

    assert response.request.path == '/'
    assert 'У вас недостаточно прав для доступа к данной странице.' in response.get_data(as_text=True)


def test_user_access_denied_for_report_pages(client, existing_user_for_logs):
    user = existing_user_for_logs['user']

    login_data = {
        'username': user.username,
        'password': user.password,
        'remember_me': 'y'
    }

    response = client.get('/auth/login')
    assert response.status_code == 200

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/session_log/report/pages', follow_redirects=True)

    assert response.request.path == '/'
    assert 'У вас недостаточно прав для доступа к данной странице.' in response.get_data(as_text=True)


def test_admin_access_allowed_for_report_users(client, existing_user_for_logs):
    admin = existing_user_for_logs['admin']

    login_data = {
        'username': admin.username,
        'password': admin.password,
        'remember_me': 'y'
    }

    response = client.get('/auth/login')
    assert response.status_code == 200

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/session_log/report/users', follow_redirects=True)
    assert response.status_code == 200
    assert 'Отчёт по пользователям' in response.get_data(as_text=True)


def test_admin_access_allowed_for_report_pages(client, existing_user_for_logs):
    admin = existing_user_for_logs['admin']

    login_data = {
        'username': admin.username,
        'password': admin.password,
        'remember_me': 'y'
    }

    response = client.get('/auth/login')
    assert response.status_code == 200

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/session_log/report/pages', follow_redirects=True)
    assert response.status_code == 200
    assert 'Отчёт по страницам' in response.get_data(as_text=True)


def test_user_can_only_view_own_profile(client, existing_user_for_logs):
    user = existing_user_for_logs['user']
    admin = existing_user_for_logs['admin']

    login_data = {
        'username': user.username,
        'password': user.password,
        'remember_me': 'y'
    }

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get(f'/users/{user.id}', follow_redirects=True)
    assert response.status_code == 200
    assert 'Просмотр учётной записи' in response.get_data(as_text=True)
    assert user.username in response.get_data(as_text=True)

    response = client.get(f'/users/{admin.id}', follow_redirects=True)
    assert response.request.path == '/'
    assert 'У вас недостаточно прав для доступа к данной странице.' in response.get_data(as_text=True)


def test_admin_can_view_other_user_profile(client, existing_user_for_logs):
    admin = existing_user_for_logs['admin']
    user = existing_user_for_logs['user']

    login_data = {
        'username': admin.username,
        'password': admin.password,
        'remember_me': 'y'
    }

    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    response = client.get(f'/users/{user.id}', follow_redirects=True)
    assert response.status_code == 200
    assert 'Просмотр учётной записи' in response.get_data(as_text=True)
    assert user.username in response.get_data(as_text=True)
