import os
from logging.config import dictConfig

from flask import Flask

from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(test_config=None):
    """
    Create and configure an instance of the Flask application.

    Some config variable we need to specify in 'instance/config.py'

    DEBUG
    SECRET_KEY
    GITHUB_SECRET
    REPO_PATH
    """
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'dc_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'filename': '/var/log/flask/flask.log',
                'mode': 'a',
                'maxBytes': 2048,
                'backupCount': 10
            },
        },
        'loggers': {
            'flask.app': {
                'handlers': ['dc_handler']
            }
        },
    })

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'nju_dc.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from nju_dc import db
    db.init_app(app)

    # apply the blueprints to the app
    from nju_dc import main, user, wizard, webhook
    app.register_blueprint(main.app, url_prefix='/dc')
    app.register_blueprint(user.app, url_prefix='/dc')
    app.register_blueprint(wizard.app, url_prefix='/dc')
    app.register_blueprint(webhook.app, url_prefix='/dc')

    socketio.init_app(app)

    return app
