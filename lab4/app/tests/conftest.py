from functools import reduce
from collections import namedtuple
import logging
import pytest
import mysql.connector
from app import create_app
from app.db import DBConnector
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

TEST_DB_CONFIG = {
    'MYSQL_USER': os.getenv('MYSQL_USER'),
    'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD'),
    'MYSQL_HOST': os.getenv('MYSQL_HOST'),
    'MYSQL_DATABASE': os.getenv('MYSQL_DATABASE'),
}


def get_connection(app):
    return mysql.connector.connect(
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        host=app.config['MYSQL_HOST']
    )


def setup_db(app):
    logging.getLogger().info("Create db...")
    test_db_name = app.config['MYSQL_DATABASE']
    # Разделяем создание базы на отдельные запросы
    create_db_queries = [
        f'DROP DATABASE IF EXISTS {test_db_name}',
        f'CREATE DATABASE {test_db_name}',
        f'USE {test_db_name}',
    ]

    connection = get_connection(app)
    with connection.cursor() as cursor:
        for q in create_db_queries:
            cursor.execute(q)
    connection.commit()

    # Подключаемся к созданной базе
    connection.database = test_db_name

    # Загружаем схему из файла
    with app.open_resource('schema.sql') as f:
        schema_sql = f.read().decode('utf8')

    # Разделяем SQL из schema.sql на отдельные запросы
    for q in schema_sql.split(';'):
        q = q.strip()
        if q:  # пропускаем пустые строки
            with connection.cursor() as cursor:
                cursor.execute(q)

    connection.commit()
    connection.close()


def teardown_db(app):
    logging.getLogger().info("Drop db...")
    test_db_name = app.config['MYSQL_DATABASE']
    connection = get_connection(app)
    with connection.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS {test_db_name};')
    connection.close()


@pytest.fixture(scope='session')
def app():
    return create_app(TEST_DB_CONFIG)


@pytest.fixture(scope='session')
def db_connector(app):
    setup_db(app)
    with app.app_context():
        connector = DBConnector(app)
        yield connector
        connector.disconnect()
    teardown_db(app)


@pytest.fixture
def role_repository(db_connector):
    return RoleRepository(db_connector)


@pytest.fixture
def existing_role(db_connector):
    data = (1, 'admin')
    row_class = namedtuple('Row', ['id', 'name'])
    role = row_class(*data)

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        query = 'INSERT INTO roles(id, name) VALUES (%s, %s);'
        cursor.execute(query, data)
        connection.commit()

    yield role

    with connection.cursor() as cursor:
        query = 'DELETE FROM roles WHERE id=%s;'
        cursor.execute(query, (role.id,))
        connection.commit()


@pytest.fixture
def nonexisting_role_id():
    return 1


@pytest.fixture
def example_roles(db_connector):
    data = [(1, 'admin'), (2, 'test')]
    row_class = namedtuple('Row', ['id', 'name'])
    roles = [row_class(*row_data) for row_data in data]

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        placeholders = ', '.join(['(%s, %s)' for _ in range(len(data))])
        query = f"INSERT INTO roles(id, name) VALUES {placeholders};"
        cursor.execute(query, reduce(lambda seq, x: seq + list(x), data, []))
        connection.commit()

    yield roles

    with connection.cursor() as cursor:
        role_ids = ', '.join([str(role.id) for role in roles])
        query = f"DELETE FROM roles WHERE id IN ({role_ids});"
        cursor.execute(query)
        connection.commit()


@pytest.fixture
def client(app):
    return app.test_client()



@pytest.fixture
def user_repository(db_connector):
    return UserRepository(db_connector)


@pytest.fixture
def example_role(db_connector):
    data = (1, 'test_role')
    row_class = namedtuple('Row', ['id', 'name'])
    role = row_class(*data)

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        query = 'INSERT INTO roles(id, name) VALUES (%s, %s);'
        cursor.execute(query, data)
        connection.commit()

    yield role

    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM roles WHERE id = %s;', (role.id,))
        connection.commit()


@pytest.fixture
def existing_user(db_connector, example_role):
    data = {
        "id": 1,
        "username": "testuser",
        "password": "TestPass123",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "last_name": "Иванов",
        "role_id": example_role.id
    }
    row_class = namedtuple('Row', data.keys())
    user = row_class(**data)

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        query = """
        INSERT INTO users (id, username, password_hash, first_name, middle_name, last_name, role_id)
        VALUES (%s, %s, SHA2(%s, 256), %s, %s, %s, %s)
        """
        cursor.execute(query, (user.id, user.username, user.password, user.first_name, user.middle_name, user.last_name, user.role_id))
        connection.commit()

    yield user

    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM users WHERE id = %s;', (user.id,))
        connection.commit()


@pytest.fixture
def nonexisting_user_id():
    return 9999

