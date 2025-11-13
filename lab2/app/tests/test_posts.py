import pytest
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def decode_response(response):
    return response.data.decode('utf-8')

# 1. Тест параметров URL - отображаются все переданные параметры
def test_url_params_display(client):
    response = client.get('/args?param1=value1&param2=value2')
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'param1' in decoded
    assert 'value1' in decoded
    assert 'param2' in decoded
    assert 'value2' in decoded

# 2. Тест заголовков запроса - отображаются все заголовки
def test_request_headers_display(client):
    custom_headers = {'Test-Header': 'TestValue'}
    response = client.get('/headers', headers=custom_headers)
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'Test-Header' in decoded
    assert 'TestValue' in decoded

# 3. Тест cookie - устанавливается при первом запросе
def test_cookie_set_on_first_request(client):
    response = client.get('/cookie')
    assert response.status_code == 200
    assert 'cookie_name=new_cookie' in response.headers.get('Set-Cookie', '')

# 4. Тест cookie - удаляется при повторном запросе
def test_cookie_deleted_on_second_request(client):
    client.get('/cookie')
    response = client.get('/cookie', headers={'Cookie': 'cookie_name=test'})
    assert 'cookie_name=;' in response.headers.get('Set-Cookie', '')

# 5. Тест формы - отображаются отправленные значения
def test_form_params_display(client):
    form_data = {'field1': 'test1', 'field2': 'test2'}
    response = client.post('/form', data=form_data)
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'field1' in decoded
    assert 'test1' in decoded
    assert 'field2' in decoded
    assert 'test2' in decoded

# 6. Тест телефона - правильный формат с +7
def test_valid_phone_format_plus7(client):
    response = client.post('/phone_numbr', data={'phone': '+7 (123) 456-75-90'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert '8-123-456-75-90' in decoded

# 7 Тест телефона - правильный формат с 8
def test_valid_phone_format_8(client):
    response = client.post('/phone_numbr', data={'phone': '8(123)4567590'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert '8-123-456-75-90' in decoded

# 8 Тест телефона - правильный формат без кода страны
def test_valid_phone_format_no_country_code(client):
    response = client.post('/phone_numbr', data={'phone': '123.456.75.90'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert '8-123-456-75-90' in decoded

# 9 Тест телефона - ошибка недопустимых Символов
def test_phone_invalid_chars(client):
    response = client.post('/phone_numbr', data={'phone': '8(123)abc-75-90'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in decoded

# 10 Тест телефона -ошибка неверного количества цифр
def test_phone_invalid_length_short(client):
    response = client.post('/phone_numbr', data={'phone': '12345'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'Недопустимый ввод. Неверное количество цифр.' in decoded

# 11. Тест телефона - ошибка неверного количества цифр
def test_phone_invalid_length_long(client):
    response = client.post('/phone_numbr', data={'phone': '8123456789012'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'Недопустимый ввод. Неверное количество цифр.' in decoded

# 12. Тес телефона - проверка is-invalid класса при ошибке
def test_phone_error_class(client):
    response = client.post('/phone_numbr', data={'phone': 'invalid'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'is-invalid' in decoded

# 13. Тест телефона - проверка invalid-feedback при ошибке
def test_phone_error_feedback(client):
    response = client.post('/phone_numbr', data={'phone': 'invalid'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'invalid-feedback' in decoded

# 14. Тест телефона - отображение отформатированного номера
def test_formatted_phone_display(client):
    response = client.post('/phone_numbr', data={'phone': '+7 (123) 456-75-90'})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert 'alert-success' in decoded
    assert '8-123-456-75-90' in decoded

# 15. тест телефона - сохранение введенного значения при ошибке
def test_phone_value_preserved_on_error(client):
    test_phone = '8(123)abc'
    response = client.post('/phone_numbr', data={'phone': test_phone})
    assert response.status_code == 200
    decoded = decode_response(response)
    assert test_phone in decoded