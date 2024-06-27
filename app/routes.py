from copy import deepcopy
from flask import render_template, request, redirect, jsonify, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.models import Card, User
from app.forms import LoginForm, RegistrationForm
from app.scheduler import Scheduler

# Import modules
from .utils import update_user_json, calculate_score


# ROUTE 1.1: Register Page
# ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    GET: Render the registration form.
    POST: Process the registration form submission, create a new user, and save to the JSON file.
    """
    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            users, message = User.load_users()
            users[user.username] = user
            User.save_users(users)
            return redirect("/login")

    if current_user.is_authenticated:
        return redirect("/post_login")
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        users, message = User.load_users()
        users[user.username] = user
        User.save_users(users)
        flash('Congratulations, you are now a registered user!')
        return redirect("/login")
    return render_template('register.html', title='Register', form=form)


# ROUTE 1.2: Login Page
# --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    GET: Render the login form.
    POST: Process the login form submission, verify user credentials, and log in the user.
    """
    if current_user.is_authenticated:
        return redirect("/post_login")
    form = LoginForm()
    if form.validate_on_submit():
        json_status = update_user_json({"username": form.username.data, "password": form.password.data}, "login")
        # Check for User
        # --------------
        # If the user exists and enter's valid credentials
        if json_status == "Valid":
            user = User.get_by_username(form.username.data)
            login_user(user, remember=form.remember_me.data)
            # Redirect the user to /post_login page
            return redirect("/post_login")
        else:
            flash(f"{json_status}")
            # Redirect the user to /login page TODO: Add some message to the user
            return redirect("/login")
    return render_template('login.html', title='Sign In', form=form)


# ROUTE 2: Display All Cards
# --------------------------
# Under "Manage Cards" -> "View All Cards"
@app.route("/all_cards")
@login_required
def all_cards():
    """
    Display all cards for the logged-in user.
    """
    u = User.get_by_username(current_user.id)
    cards = Card.get_by_user_id(u.id)
    return render_template("all_cards.html", cards=cards)


# ROUTE 3: Logout the User
# -------------------
@app.route('/logout')
def logout():
    """
    Log out the current user and redirect to the login page.
    """
    logout_user()
    return redirect("/login")


# ROUTE 4: INDEX "Manage Cards" Page
# ---------------------------------
# Shows
@app.route("/")
@login_required
def index():
    """
    Display the index page.
    Shows Add-Cards, View All Cards, Filter Cards option
    """
    try:
        u = User.get_by_username(current_user.id)
        cards = Card.get_by_user_id(u.id)
        total_cards = len(cards)
        page = request.args.get('page', 1, type=int)
        if page > total_cards:
            page = total_cards
        if page < 1:
            page = 1
        card = cards[page - 1] if cards else None
        topics = set(card.topic for card in cards)
        all_topics_len = len(topics)
        all_topics = sorted(topics)
    except Exception as e:
        print(e)
        page = 1
        card = None
        total_cards = 0
        all_topics_len = 0
        all_topics = []

    return render_template("index.html", card=card, page=page, total_cards=total_cards, all_topics_len=all_topics_len,
                           all_topics=all_topics)


# ROUTE 5.1: POST LOGIN PAGE DISPLAY
# ---------------------------------------
@app.route("/post_login")
@login_required
def post_login():
    """
    Display the post-login page.
    """
    return render_template('post_login.html')


# TOPIC 5.2: POST LOGIN ACTIONS
# ------------------------------------------
@app.route("/post_login_action", methods=["POST"])
@login_required
def post_login_action():
    """
    Handle actions from the post-login page, redirecting based on the action chosen.
    """
    action = request.form.get("action")
    if action == "start_game":
        # Takes the user to start_game method by "random" or "topic"
        return redirect("/start_game")
    else:
        # Takes the user to add a new card (See Route below)
        return redirect("/cards/new")


# ROUTE 6.1: CHOOSE TOPIC TO PLAY GAME
# ---------------------------------------
@app.route("/start_by_topic")
@login_required
def start_by_topic():
    """
    Display a page for starting a game by selecting a topic.
    """
    u = User.get_by_username(current_user.id)
    cards = Card.get_by_user_id(u.id)
    topics = sorted(set(card.topic for card in cards))
    return render_template("start_by_topic.html", topics=topics)


# ROUTE 6.2: START GAME by selected topic
# --------------------------------------------
@app.route("/start_game_by_topic/<string:topic>")
@login_required
def start_game_by_topic(topic):
    """
    Start a game based on the selected topic.
    """
    print(topic)
    u = User.get_by_username(current_user.id)
    # Gather cards by topic into a list
    cards = [card for card in Card.get_by_user_id(u.id) if card.topic.lower() == topic.lower()]
    # card_queue = Scheduler(cards)
    #####
    # Section to use algorithm to pick cards TODO
    #####
    _cards = cards
    # card_queue.pick_cards() # Previous version of algorithm
    # print(_cards)
    total_cards = len(_cards)

    if not _cards:
        flash("There are no cards available today for this topic.")
        return redirect("/post_login")

    # Page: Card's served
    page = request.args.get('page', 1, type=int)
    if page > total_cards:
        page = total_cards
    if page < 1:
        page = 1
    card = _cards[page - 1]

    return render_template('start_game.html', card=card, page=page, total_cards=total_cards, topic=topic)


# ROUTE 6.3: PLAY GAME WITH ALL CARDS
# -----------------------------------------
@app.route("/start_game", methods=['GET', 'POST'])
@login_required
def start_game():
    """
    Start a game with all available cards for the logged-in user.
    """
    u = User.get_by_username(current_user.id)
    cards = Card.get_by_user_id(u.id)
    # card_queue = Scheduler(cards)
    #####
    # Section to use algorithm to pick cards TODO
    #####
    _cards = cards
    # card_queue.pick_cards()
    total_cards = len(_cards)

    if not _cards:
        flash("There are no cards available today to start the game.")
        return redirect("/post_login")

    if request.method == 'POST':
        flag = request.json['flag']
        card_id = int(request.json['card_id'])
        page = int(request.json['page'])

        print(flag, card_id, page)

        # Update the flags dictionary in the JSON file
        cards_dataset = deepcopy(Card.load_cards())
        updated_card_dataset = []
        current_id_card_dataset = {}
        for card_details in cards_dataset:
            if card_details.id == card_id:
                current_id_card_dataset = card_details
            else:
                updated_card_dataset.append(card_details)

        # right / wrong
        current_id_flag_details = current_id_card_dataset.flags
        if flag in current_id_flag_details.keys():
            current_id_flag_details[flag] += 1
        else:
            current_id_flag_details[flag] = 1

        current_id_card_dataset.flags = current_id_flag_details
        updated_card_dataset.append(current_id_card_dataset)

        # save back json
        Card.save_cards(updated_card_dataset)

        next_page = page + 1
        if next_page > total_cards:
            return jsonify(next_page=None)
        return jsonify(next_page=next_page)

    page = request.args.get('page', 1, type=int)
    if page > total_cards:
        page = total_cards
    if page < 1:
        page = 1
    card = _cards[page - 1]

    return render_template('start_game.html', card=card, page=page, total_cards=total_cards)


# ROUTE 7: ADD CARDS
# -------------------------------------
@app.route("/cards/new", methods=["GET", "POST"])
@login_required
def new_card():
    """
    Handle creating a new card.
    GET: Render the form to create a new card.
    POST: Process the form submission and save the new card.
    """
    u = User.get_by_username(current_user.id)

    if request.method == "GET":
        all_topics = sorted(set(card.topic for card in Card.get_by_user_id(u.id)))
        return render_template("new.html", all_topics=all_topics)
    else:
        topic = request.form["topic"]
        question = request.form["question"]
        hint = request.form.get("hint")
        if not hint:
            hint = "No hints available!"
        answer = request.form["answer"]
        cards = Card.load_cards()
        card_id = max(card.id for card in cards) + 1 if cards else 1
        card = Card(id=card_id,
                    topic=topic,
                    question=question,
                    hint=hint,
                    answer=answer,
                    author_id=u.id)
        Card.add_card(card)
        return redirect("/post_login")  # Redirect back to the post-login page


# ROUTE 8: Display All Cards
# -----------------------------
@app.route("/cards")
@login_required
def show_cards():
    """Shows all the cards in the database belonging to all the topics"""
    u = User.get_by_username(current_user.id)
    cards = sorted(Card.get_by_user_id(u.id), key=lambda card: card.topic)
    all_topics = sorted(set(card.topic for card in cards))

    return render_template("cards.html",
                           cards=cards,
                           all_topics=all_topics,
                           page=1,
                           total_cards=len(cards),
                           all_topics_len=len(all_topics))


# ROUTE 9.1: Display Cards by Topic
# ---------------------------------
@app.route("/cards/category/<string:card_category>")
@login_required
def get_card_category(card_category):
    """
    Display card by a certain Topic of choice.
    Enabled by choosing from Filter Button
    #TODO: Get Filter button inside View All Cards
    """
    u = User.get_by_username(current_user.id)
    cards = [card for card in Card.get_by_user_id(u.id) if card.category == card_category]
    return render_template("cards.html", cards=cards)


# ROUTE 9.2:
# ---------------------------------
@app.route("/cards/topic/<string:card_topic>")
@login_required
def get_card_topic(card_topic):
    u = User.get_by_username(current_user.id)
    cards = [card for card in Card.get_by_user_id(u.id) if card.topic == card_topic]
    return render_template("all_cards.html", cards=cards)


# ROUTE 10: GET CARD
# ------------------------------
@app.route("/cards/<int:card_id>")
@login_required
def get_card(card_id):
    """
    Fetches selected card to be displayed
    """
    card = Card.get_by_id(card_id)
    return render_template("show.html", card=card)


# ROUTE 11: EDIT CARD
# --------------------------------
@app.route("/cards/<int:card_id>", methods=["POST"])
@login_required
def edit(card_id):
    """Enables to edit card"""
    card = Card.get_by_id(card_id)
    card.question = request.form["question"]
    card.topic = request.form["topic"]
    cards = Card.load_cards()
    for i, c in enumerate(cards):
        if c.id == card_id:
            cards[i] = card
    Card.save_cards(cards)
    return redirect("/")


# ROUTE 12: DELETE CARD
# ----------------------------------
@app.route("/cards/<int:card_id>/delete", methods=["POST"])
@login_required
def delete_card(card_id):
    Card.delete_card(card_id)
    return redirect("/")


# ROUTE 13: SCOREBOARD
# ----------------------------------
@app.route('/scoreboard')
@login_required
def scoreboard():
    """
    Display scoreboard with user's performance stats.
    """
    u = User.get_by_username(current_user.id)
    cards = Card.get_by_user_id(u.id)

    scoreboard = {}
    for card in cards:
        topic = card.topic
        if topic not in scoreboard:
            scoreboard[topic] = {
                'right': 0,
                'wrong': 0,
                'hints': 0,
                'score': 0
            }
        scoreboard[topic]['right'] += card.flags.get('right', 0)
        scoreboard[topic]['wrong'] += card.flags.get('wrong', 0)
        scoreboard[topic]['hints'] += card.flags.get('hint_used', 0)
        scoreboard[topic]['score'] = calculate_score(scoreboard[topic])

    return render_template('scoreboard.html', scoreboard=scoreboard)
