import pytest
from app import app
from app.models import User, Card


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            # setup database and other initializations
            yield client


@pytest.fixture
def new_user():
    user = User(username='test_user', email='test@example.com')
    user.set_password('password')
    users, message = User.load_users()
    users[user.username] = user
    User.save_users(users)
    return user


@pytest.fixture
def login(client, new_user):
    response = client.post('/login', data=dict(
        username=new_user.username,
        password='password'
    ), follow_redirects=True)
    assert response.status_code == 200
    return response


# to do - fix this module
def test_register(client):
    response = client.get('/register')
    assert response.status_code == 200

    response = client.post('/register', data=dict(
        username='test_user2',
        email='test2@example.com',
        password='password',
        password2='password'
    ), follow_redirects=True)
    assert response.status_code == 200


def test_login(client, new_user):
    response = client.get('/login')
    assert response.status_code == 200

    response = client.post('/login', data=dict(
        username='test_user',
        password='password'
    ), follow_redirects=True)
    assert response.status_code == 200


def test_logout(client, login):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


def test_all_cards(client, login):
    response = client.get('/all_cards')
    assert response.status_code == 200


def test_index(client, login):
    response = client.get('/')
    assert response.status_code == 200


def test_post_login(client, login):
    response = client.get('/post_login')
    assert response.status_code == 200
