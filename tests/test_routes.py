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


def test_post_login_action(client, login):
    response = client.post('/post_login_action', data=dict(action="start_game"), follow_redirects=True)
    assert response.status_code == 200


def test_start_by_topic(client, login):
    response = client.get('/start_by_topic')
    assert response.status_code == 200


def test_new_card(client, login):
    response = client.get('/cards/new')
    assert response.status_code == 200

    response = client.post('/cards/new', data=dict(
        topic='Test Topic',
        question='Test Question',
        hint='Test Hint',
        answer='Test Answer'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Check if the card was actually added
    cards = Card.load_cards()
    assert any(card.topic == 'Test Topic' and card.question == 'Test Question' for card in cards)


def test_show_cards(client, login):
    response = client.get('/all_cards')
    assert response.status_code == 200


def test_start_game_by_topic(client, login):
    # First, add a card to ensure there's at least one card
    client.post('/cards/new', data=dict(
        topic='TestTopic',
        question='TestQuestion',
        hint='TestHint',
        answer='TestAnswer'
    ))

    response = client.get('/start_game_by_topic/TestTopic')
    assert response.status_code == 200


def test_get_card_topic(client, login):
    response = client.get('/cards/topic/test_topic')
    assert response.status_code == 200


def test_edit_card(client, login):
    # First, add a card
    client.post('/cards/new', data=dict(
        topic='EditTopic',
        question='EditQuestion',
        hint='EditHint',
        answer='EditAnswer'
    ))

    # Get the id of the newly added card
    cards = Card.load_cards()
    card_id = max(card.id for card in cards)

    # Edit the card
    response = client.post(f'/cards/{card_id}', data=dict(
        topic='EditedTopic',
        question='EditedQuestion'
    ), follow_redirects=True)
    assert response.status_code == 200

    # Check if the card was actually edited
    updated_cards = Card.load_cards()
    edited_card = next((card for card in updated_cards if card.id == card_id), None)
    assert edited_card is not None
    assert edited_card.topic == 'EditedTopic'
    assert edited_card.question == 'EditedQuestion'


def test_delete_card(client, login):
    # First, add a card
    client.post('/cards/new', data=dict(
        topic='DeleteTopic',
        question='DeleteQuestion',
        hint='DeleteHint',
        answer='DeleteAnswer'
    ))

    # Get the id of the newly added card
    cards = Card.load_cards()
    card_id = max(card.id for card in cards)

    # Delete the card
    response = client.post(f'/cards/{card_id}/delete', follow_redirects=True)
    assert response.status_code == 200

    # Check if the card was actually deleted
    updated_cards = Card.load_cards()
    assert all(card.id != card_id for card in updated_cards)


def test_scoreboard(client, login):
    response = client.get('/scoreboard')
    assert response.status_code == 200
