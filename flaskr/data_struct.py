"""
Defines how the backend data structure is working. 
Using JSON files 
Check the db-py for methods used and structure 
Then create the real-interface 
"""
import click 
from flask import (jsonify, 
                   g, 
                   current_app)


def init_db():
    db = get_db() 

    with current_app.open_resource('test_data.json') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Create a new deck: ? """
    init_db()
    click.echo('Initialized the creation process')

def get_db():
    if 'db' not in g: 
        
