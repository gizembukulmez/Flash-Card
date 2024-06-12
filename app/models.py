import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import login


class User(UserMixin):
    """
    User class for managing user information and authentication.

    Attributes:
        id (str): The username of the user, used as the ID.
        username (str): The username of the user.
        email (str): The email address of the user.
        password_hash (str): The hashed password of the user.
    """
    def __init__(self, username, email, password_hash=None) -> None:
        """
        Initialize a User object.

        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password_hash (str, optional): The hashed password of the user. Defaults to None.
        """
        self.id = username  # Using username as the ID
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def set_password(self, password) -> None:
        """
        Set the password for the user by generating a password hash.

        Args:
            password (str): The password to be hashed and set.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """
        Check if the provided password matches the stored password hash.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def load_users() -> tuple:
        """
        Load users from the user_data.json file.

        Returns:
            tuple: A dictionary of User objects and an error message (None if no error).
        """
        try:
            with open('user_data.json', 'r') as file:
                user_data = json.load(file)
                users = {k: User(username=k, email=v['email'], password_hash=v['password_hash']) for k, v in user_data.items()}
                return users, "Success - load users"
        except FileNotFoundError:
            return {}, "Login details not found - please register to use the service"  # Add error message for no user found --> Currently the form doesn't do anything.
        except json.JSONDecodeError:
            return {}, "Error decoding the user data - please contact support"

    @staticmethod
    def save_users(users) -> None:
        """
        Save users to the user_data.json file.

        Args:
            users (dict): A dictionary of User objects to be saved.
        """
        with open('user_data.json', 'w') as file:
            user_data = {k: {'email': v.email, 'password_hash': v.password_hash} for k, v in users.items()}
            json.dump(user_data, file)

    @staticmethod
    def get_by_username(username):
        """
        Get a User object by username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The User object if found, otherwise None.
        """
        users, message = User.load_users()
        return users.get(username)


@login.user_loader
def load_user(username):
    """
    Load a user by username for Flask-Login.
    Args:
        username (str): The username of the user to load.

    Returns:
        User: The User object if found, otherwise None.
    """
    return User.get_by_username(username)


class Card:
    """
    Card class for managing card information and operations.
    """
    def __init__(self,
                 id,
                 topic,
                 question,
                 answer,
                 author_id,
                 hint=None,
                 timestamp=None,
                 flags=None,
                 next_review_date=None):
        """
        Initialize a Card object.

        Args:
            id (str): The unique identifier of the card.
            topic (str): The topic of the card.
            question (str): The question on the card.
            answer (str): The answer to the question.
            hint (str): The hint for the question.
            author_id (str): The ID of the author who created the card.
            timestamp (str, optional): The timestamp when the card was created. Defaults to current time if not provided.
            flags (dict, optional): Any flags associated with the card. Defaults to an empty dictionary.
        """
        if flags is None:
            flags = {}
        self.id = id
        self.topic = topic
        self.question = question
        self.hint = hint
        self.answer = answer
        self.author_id = author_id
        self.timestamp = timestamp or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.flags = flags
        self.next_review_date = next_review_date

    @staticmethod
    def load_cards():
        """
        Load cards from the card_data.json file.

        Returns:
            list: A list of Card objects.
        """
        try:
            with open('card_data.json', 'r') as file:
                card_data = json.load(file)
                cards = [Card(**card) for card in card_data]
                return cards
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_cards(cards):
        """
        Save cards to the card_data.json file.

        Args:
            cards (list): A list of Card objects to be saved.
        """
        with open('card_data.json', 'w') as file:
            # Prepares the card data to be stored in JSON format -- card.__dict__
            # Converts data associated with attributes of a card object into a dict format to
            # store in JSON
            card_data = [card.__dict__ for card in cards]
            # Writes the card into JSON
            json.dump(card_data, file)

    @staticmethod
    def get_by_user_id(user_id):
        """
        Get a list of Card objects by author ID.

        Args:
            user_id (str): The ID of the author to filter cards by.

        Returns:
            list: A list of Card objects created by the specified author.
        """
        cards = Card.load_cards()
        return [card for card in cards if card.author_id == user_id]

    @staticmethod
    def get_by_id(card_id):
        """
        Get a Card object by its unique ID.

        Args:
            card_id (str): The unique identifier of the card.

        Returns:
            Card: The Card object if found, otherwise None.
        """
        cards = Card.load_cards()
        for card in cards:
            if card.id == card_id:
                return card
        return None

    @staticmethod
    def add_card(card):
        """
        Add a new card to the card_data.json file.

        Args:
            card (Card): The Card object to be added.
        """
        cards = Card.load_cards()
        cards.append(card)
        Card.save_cards(cards)

    @staticmethod
    def delete_card(card_id):
        """
        Delete a card from the card_data.json file by its unique ID.

        Args:
            card_id (str): The unique identifier of the card to be deleted.
        """
        # Loads the existing cards
        cards = Card.load_cards()
        # Creates a new list of card except the card's matching the card_id that needs to be deleted
        cards = [card for card in cards if card.id != card_id]
        # Saves the updated list back - this excludes the selected id - in effect deleting the card
        Card.save_cards(cards)
