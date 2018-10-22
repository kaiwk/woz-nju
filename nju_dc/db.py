import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db(isolation_leve=None):
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=isolation_leve
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    task_dir = os.path.join(current_app.instance_path, 'tasks')
    tasks = os.listdir(task_dir)
    task_items = []
    for t in tasks:
        with open(os.path.join(task_dir, t)) as f:
            task_items.append((f.read(), 0, 0))
    db.executemany('insert into task values (?, ?, ?)', task_items)
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
