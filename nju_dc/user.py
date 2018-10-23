import json

from flask import Blueprint, render_template, request, session, redirect, url_for

from .db import get_db, close_db
from . import socketio

app = Blueprint('user', __name__,
                static_folder='static',
                template_folder='templates')

@app.route('user/', methods=['GET', 'POST'])
def index():
    if session['task_id']:
        task_id = session['task_id']
    else:
        return redirect(url_for('main.index'))
    with get_db() as db:
        res = db.execute('select body from task where rowid=?', (task_id,))
        task = json.loads(res.fetchone()[0])
        desc = task['goal']['message']
        log = task['log']

    if request.method == 'GET':
        return render_template('user.html', desc=desc, log=log)
    elif request.method == 'POST':
        resp = request.form['resp']
        task['log'].append({'text': [resp]})
        log = task['log']
        with get_db('EXCLUSIVE') as db:
            db.execute('update task set body=? where rowid=?', (json.dumps(task, ensure_ascii=False), task_id))
        return render_template('user.html', desc=desc, log=log)

@socketio.on('disconnect', namespace='/user')
def disconnect_handler():
    print('user:dislfjalskdjflaskjdf')
    with get_db('EXCLUSIVE') as db:
        db.execute('update task set selected=0 where rowid=?', (session['task_id'],))
    session['task_id'] = None
    close_db()
