
def test_visit_log_contents_for_user(client, existing_user_for_logs):
    user = existing_user_for_logs['user']

    login_data = {
        'username': user.username,
        'password': user.password,
        'remember_me': 'y'
    }
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    visited_paths = [
        '/',
        f'/users/{user.id}',
        f'/users/{user.id}/edit',
    ]
    for path in visited_paths:
        assert client.get(path, follow_redirects=True).status_code == 200

    response = client.get('/session_log', follow_redirects=True)
    assert response.status_code == 200

    page_content = response.get_data(as_text=True)

    for path in visited_paths:
        expected_row = f"<td>{path}</td>"
        assert expected_row in page_content



def test_visit_log_report_pages_for_admin(client, existing_user_for_logs):
    admin = existing_user_for_logs['admin']
    target_user = existing_user_for_logs['user']

    login_data = {
        'username': admin.username,
        'password': admin.password,
        'remember_me': 'y'
    }
    response = client.post('/auth/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    visited_paths = [
        '/',
        f'/users/{target_user.id}',
        f'/users/{target_user.id}/edit',
    ]
    for path in visited_paths:
        assert client.get(path, follow_redirects=True).status_code == 200

    response = client.get('/session_log/report/pages', follow_redirects=True)
    assert response.status_code == 200
    page_content = response.get_data(as_text=True)

    assert 'Отчёт по страницам' in page_content

    expected_rows = [
        f"<td>{visited_paths[0]}</td>\n            <td>2</td>",
        f"<td>{visited_paths[1]}</td>\n            <td>1</td>",
        f"<td>{visited_paths[2]}</td>\n            <td>1</td>",
    ]

    for row in expected_rows:
        assert row in page_content



def test_visit_log_report_users(client, existing_user_for_logs):
    user = existing_user_for_logs['user']
    admin = existing_user_for_logs['admin']

    login_data_user = {
        'username': user.username,
        'password': user.password,
        'remember_me': 'y'
    }
    response = client.post('/auth/login', data=login_data_user, follow_redirects=True)
    assert response.status_code == 200

    user_paths = ['/', f'/users/{user.id}', f'/users/{user.id}/edit']
    for path in user_paths:
        assert client.get(path, follow_redirects=True).status_code == 200

    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200

    login_data_admin = {
        'username': admin.username,
        'password': admin.password,
        'remember_me': 'y'
    }
    response = client.post('/auth/login', data=login_data_admin, follow_redirects=True)
    assert response.status_code == 200

    admin_paths = ['/', f'/users/{admin.id}', f'/users/{admin.id}/edit']
    for path in admin_paths:
        assert client.get(path, follow_redirects=True).status_code == 200

    response = client.get('/session_log/report/users', follow_redirects=True)
    assert response.status_code == 200
    page_content = response.get_data(as_text=True)

    assert 'Отчёт по пользователям' in page_content

    full_name_user = f"{user.last_name} {user.first_name} {user.middle_name}"
    full_name_admin = f"{admin.last_name} {admin.first_name} {admin.middle_name}"

    assert full_name_user in page_content
    assert full_name_admin in page_content

    expected_rows = [
        f"<td>{full_name_admin}</td>\n            <td>6</td>",
        f"<td>{full_name_user}</td>\n            <td>5</td>",
    ]

    for row in expected_rows:
        assert row in page_content

