import pytest
from src.fitnesstracker import create_app, db

@pytest.fixture
def app():
    app = create_app(environment='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_redirect_when_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302  # redirect to login
    assert b'/login' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data