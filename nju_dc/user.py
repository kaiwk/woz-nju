import json

from flask import (Blueprint, render_template, request, session, redirect,
                   url_for, current_app, flash)

from .db import get_db, close_db
from . import socketio

app = Blueprint('user', __name__,
                static_folder='static',
                template_folder='templates')

@app.route('user/', methods=['GET', 'POST'])
def index():
    if session.get('task_id'):
        task_id = session['task_id']
    else:
        return redirect(url_for('main.index'))

    current_app.logger.info('task id: {}'.format(task_id))
    with get_db() as db:
        res = db.execute('select body from task where rowid=?', (task_id,))
        task = json.loads(res.fetchone()[0])
        desc = task['goal']['message']
        log = task['log']

    if request.method == 'GET':
        return render_template('user.html', desc=desc, log=log)
    elif request.method == 'POST':
        resp = request.form['resp']
        if resp.strip():
            task['log'].append({'text': [resp]})
            log = task['log']
            with get_db('EXCLUSIVE') as db:
                db.execute('update task set body=?, selected=0 where rowid=?',
                           (json.dumps(task, ensure_ascii=False), task_id))

            session.clear()         # clear session
            return render_template('user.html', desc=desc, log=log)
        else:
            flash('回复内容不能为空哦')
            return redirect(url_for('user.index'))

@socketio.on('disconnect', namespace='/user')
def disconnect_handler():
    current_app.logger.info('disconnect!')
    if session.get('task_id'):
        with get_db('EXCLUSIVE') as db:
            db.execute('update task set selected=0 where rowid=?', (session['task_id'],))
    close_db()
