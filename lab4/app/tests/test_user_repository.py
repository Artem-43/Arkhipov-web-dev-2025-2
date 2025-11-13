def test_get_user_by_id(user_repository, existing_user):
    user = user_repository.get_by_id(existing_user.id)
    assert user is not None
    assert user['username'] == existing_user.username
    assert user['first_name'] == existing_user.first_name


def test_get_user_by_username_and_password(user_repository, existing_user):
    user = user_repository.get_by_username_and_password(existing_user.username, existing_user.password)
    assert user is not None
    assert user['id'] == existing_user.id


def test_get_user_by_wrong_password_returns_none(user_repository, existing_user):
    user = user_repository.get_by_username_and_password(existing_user.username, "WrongPass123")
    assert user is None


def test_create_user(user_repository, db_connector, example_role):
    username = "newuser"
    password = "NewPass123"
    user_repository.create(username, password, "Алексей", "Петрович", "Сидоров", example_role.id)

    connection = db_connector.connect()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        assert user is not None
        assert user["first_name"] == "Алексей"

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        connection.commit()


def test_update_user(user_repository, db_connector, existing_user, example_role):
    new_first_name = "Обновлённый"
    user_repository.update(existing_user.id, new_first_name, existing_user.middle_name, existing_user.last_name, existing_user.role_id)

    connection = db_connector.connect()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT first_name FROM users WHERE id = %s", (existing_user.id,))
        user = cursor.fetchone()
        assert user["first_name"] == new_first_name


def test_delete_user(user_repository, db_connector, example_role):
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (id, username, password_hash, first_name, middle_name, last_name, role_id) "
            "VALUES (999, 'todelete', SHA2('Temp1234', 256), 'Имя', 'Отчество', 'Фамилия', %s)",
            (example_role.id,)
        )
        connection.commit()

    user_repository.delete(999)

    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (999,))
        user = cursor.fetchone()
        assert user is None
