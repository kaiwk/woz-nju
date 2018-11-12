import os
from logging.config import dictConfig

from flask import Flask


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
                'formatter': 'default',
                'mode': 'a',
                'maxBytes': 10000,
                'backupCount': 1
            },
        },
        'loggers': {
            'flask.app': {
                'handlers': ['dc_handler']
            }
        },
    })

    flask = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(flask.instance_path)
    except OSError:
        pass

    # a default secret that should be overridden by instance config
    flask.config.from_mapping(
        SECRET_KEY='this-is-a-secret-key'
    )

    if test_config is None:
        if flask.config['ENV'] == 'development':
            flask.config.from_object('instance.config.DevelConfig')
        else:
            flask.config.from_object('instance.config.ProductionConfig')
    else:
        # load the test config if passed in
        flask.config.update(test_config)

    # register the database commands
    from app import database
    database.init_app(flask)

    # apply the blueprints to the app
    from app import main, user, wizard, webhook, online_help
    flask.register_blueprint(main.bp, url_prefix='/dc')
    flask.register_blueprint(user.bp, url_prefix='/dc')
    flask.register_blueprint(wizard.bp, url_prefix='/dc')
    flask.register_blueprint(webhook.bp, url_prefix='/dc')
    flask.register_blueprint(online_help.bp, url_prefix='/dc')

    return flask
