import json

from flask import Blueprint, session, redirect, url_for, current_app

from .db import get_db

app = Blueprint('main', __name__,
                static_folder='static',
                template_folder='templates')

@app.route('/')
def index():
    with get_db('EXCLUSIVE') as db:
        c = db.execute('select rowid, body from task where selected=0 limit 1;')
        row = c.fetchone()
        task_id = row['rowid']
        task = json.loads(row['body'])
        db.execute('update task set selected=1 where rowid=?', (task_id,))

    session['task_id'] = task_id # save the task_id
    log = task['log']
    if not log or ('metadata' in log[-1]):
        current_app.logger.info('Redirect to user index.')
        return redirect(url_for('user.index'))
    current_app.logger.info('Redirect to wizard index.')
    return redirect(url_for('wizard.index'))
