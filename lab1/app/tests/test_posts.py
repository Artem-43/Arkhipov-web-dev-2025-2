import pytest
from app import app as flask_app, posts_list

@pytest.fixture
def client():
    flask_app.config.update({
        "TESTING": True,
    })
    with flask_app.test_client() as client:
        yield client

def test_index_template_used(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Задание к лабораторной работе".encode('utf-8') in response.data

def test_posts_template_used(client):
    response = client.get('/posts')
    assert response.status_code == 200
    assert "Последние посты".encode('utf-8') in response.data

def test_post_template_used(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Заголовок поста".encode('utf-8') in response.data

def test_about_template_used(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert "Об авторе".encode('utf-8') in response.data

def test_posts_data_passed(client):
    response = client.get('/posts')
    assert response.status_code == 200
    for post in posts_list:
        assert post['title'].encode('utf-8') in response.data
        assert post['author'].encode('utf-8') in response.data
        assert post['date'].strftime('%d.%m.%Y').encode('utf-8') in response.data

def test_post_data_passed(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    assert post['title'].encode('utf-8') in response.data
    assert post['text'].encode('utf-8') in response.data
    assert post['author'].encode('utf-8') in response.data
    assert post['date'].strftime('%d.%m.%Y %H:%M').encode('utf-8') in response.data

def test_post_content_displayed(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    assert post['title'].encode('utf-8') in response.data
    assert post['text'].encode('utf-8') in response.data
    assert post['author'].encode('utf-8') in response.data
    assert post['date'].strftime('%d.%m.%Y %H:%M').encode('utf-8') in response.data

def test_post_date_format(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    expected_date = post['date'].strftime('%d.%m.%Y %H:%M')
    assert expected_date.encode('utf-8') in response.data

def test_post_404(client):
    response = client.get('/posts/963')
    assert response.status_code == 404

def test_index_page_content(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Задание к лабораторной работе".encode('utf-8') in response.data

def test_about_page_content(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert "Об авторе".encode('utf-8') in response.data

def test_posts_page_content(client):
    response = client.get('/posts')
    assert response.status_code == 200
    for post in posts_list:
        assert post['title'].encode('utf-8') in response.data
        assert post['author'].encode('utf-8') in response.data
        assert post['date'].strftime('%d.%m.%Y').encode('utf-8') in response.data

def test_post_image_displayed(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    assert f"images/{post['image_id']}".encode('utf-8') in response.data

def test_post_comments_displayed(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    for comment in post['comments']:
        assert comment['author'].encode('utf-8') in response.data
        assert comment['text'].encode('utf-8') in response.data

def test_post_replies_displayed(client):
    response = client.get('/posts/0')
    assert response.status_code == 200
    post = posts_list[0]
    for comment in post['comments']:
        if 'replies' in comment:
            for reply in comment['replies']:
                assert reply['author'].encode('utf-8') in response.data
                assert reply['text'].encode('utf-8') in response.data