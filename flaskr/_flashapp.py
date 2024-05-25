from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for)
 
from werkzeug.exceptions import abort # What is the wekzeug library? 

from flaskr.auth import login_required
from flaskr.db import get_db 

bp = Blueprint('_flashcard_app', __name__)


"""
The following methods intereact with the Database to read / write information 
These need to be redesigned as sqlite3 will not be used and instead these will fetcht 
the json files directly 
TODO: Figure out how to integrate JSON file fetch method for the 
"""
@bp.route('/')
def index():
    """
    Provides default view for the app - eg: Index lists all decks available 
    (__scope__): Could be used as a way for the user to browse the cards
    """
    db = get_db()
    cards = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC' # These are all SQLITE DB specific codes here is where the methods and commands need to change
    ).fetchall()
    return render_template('_flashapp/index.html', cards=cards)

"""
Create method of the app to create post - as a basic component
To be extended to create the cards / decks 
A pattern emerges where each of the app components are extended to both dekcs and cards
Except for edit / update
"""
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create(): 
    if request.method == 'POST': 
        title = request.form['title']
        body = request.form['body']
        error = None 

        if not title: 
            error = 'Title is required'
        
        if error is not None: 
            flash(error)
        
        else: 
            db = get_db() 
            db.execute(
                'INSERT INTO post (title, body, tags)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('_flashapp.index'))
    return render_template('_flashapp/create.html')

def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post

"""
Delete method for the app compoenent post from the tutorial 
Perhaps you can modify this to have it perform the same for decks and cards 
"""
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('_flashapp.index'))


"""
Update method for the app - 
Useful for the cards content to be updated
"""
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('_flashapp/update.html', post=post)
