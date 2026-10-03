import pytest
from app import create_app
from app.database import db
from app.models import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Smarter Budgeting' in response.data

def test_register_page(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data

def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

def test_dashboard_redirect_if_not_logged_in(client):
    response = client.get('/dashboard')
    # Should redirect to login
    assert response.status_code == 302
    assert '/auth/login' in response.location
