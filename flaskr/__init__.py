import os 
from flask import Flask, jsonify

def create_app(test_config=None):
    """
    Creates and configues the app
    """
    app = Flask(__name__, instance_relative_config=True)
    
    """
    instance_relative_config=True tells the app that configuration 
    files are relative to the instance folder. The instance folder 
    is located outside the flaskr package and can hold local data 
    that shouldn’t be committed to version control, such as 
    configuration secrets and the database file.
    """
    ##### Imports the database component of the app ##### 
    from . import db 
    db.init_app(app)

    ###### Imports the Authentication component of the app #####
    from . import auth 
    app.register_blueprint(auth.bp) # basically tells what the app will show when the user has to "login"

    ###### Imports the Core app component of the app ###### 
    from . import _flashapp
    app.register_blueprint(_flashapp.bp)
    app.add_url_rule('/', endpoint='index')

    ######################## NO IDEA WHAT THESE DO #######################
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ################### PLANNED COMPONENTS ###################### 

    # a simple page that says hello
    @app.route('/') # -> home page. Default that is loaded when app opens up
    def hello():
        return 'Yello, Nerd!'
    
    @app.route('/edit')
    def edit_mode():
        """
        Enable user to enter edit mode and edit decks & cards 
        """
        return 'You\'re in edit mode' 
    
    @app.route('/edit/deck')
    def edit_deck():
        """
        If chosen let's user view all the decks and choose a particular deck  
        """
        return 'You can edit decks in here'  

    
    return app