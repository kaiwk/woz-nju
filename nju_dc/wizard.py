import json

from flask import (Blueprint, render_template, request, session, jsonify,
                   redirect, url_for, current_app)

from .db import get_db, close_db
from . import socketio

app = Blueprint('wizard', __name__,
                static_folder='static',
                template_folder='templates')

@app.route('wizard/', methods=['GET', 'POST'])
def index():
    if session.get('task_id'):
        task_id = session['task_id']
    else:
        return redirect(url_for('main.index'))

    with get_db() as db:
        res = db.execute('select body from task where rowid=?', (task_id,))
        task = json.loads(res.fetchone()[0])

    if request.method == 'GET':
        log = task['log']
        return render_template('wizard.html', log=log)
    elif request.method == 'POST':
        task['log'][-1]['text'].append(request.form['sys_resp'])
        with get_db('EXCLUSIVE') as db:
            res = db.execute('update task set body=?, selected=0 where rowid=?',
                             (json.dumps(task, ensure_ascii=False), task_id))

        session.clear()         # clear the task_id
        return render_template('wizard.html', log=task['log'])

@app.route('update_metadata/', methods=['POST'])
def update_metadata():
    food_type = request.form['want_food_type']
    pricerange = request.form['want_pricerange']
    request_food_type = True if request.form['request_food_type'] == 'yes' else False
    request_pricerange = True if request.form['request_pricerange'] == 'yes' else False
    request_recom = True if request.form['request_recom'] == 'yes' else False
    request_phone = True if request.form['request_phone'] == 'yes' else False
    request_addr = True if request.form['request_addr'] == 'yes' else False

    task_id = session['task_id']
    with get_db('EXCLUSIVE') as db:
        res = db.execute('select body from task where rowid=?', (task_id,))
        task = json.loads(res.fetchone()[0])
        metadata = {}
        metadata['inform'] = {}
        metadata['request'] = []
        if food_type.strip():
            metadata['inform']['food_type'] = food_type
        if pricerange.strip():
            metadata['inform']['pricerange'] = pricerange
        if request_food_type:
            metadata['request'].append('food_type')
        if request_pricerange:
            metadata['request'].append('pricerange')
        if request_recom:
            metadata['request'].append('recommendation')
        if request_phone:
            metadata['request'].append('phone')
        if request_addr:
            metadata['request'].append('address')

        task['log'][-1]['metadata'] = metadata
        with get_db() as db:
            db.execute('update task set body=? where rowid=?',
                       (json.dumps(task, ensure_ascii=False), task_id))
        return jsonify(metadata)

@socketio.on('disconnect', namespace='/wizard')
def disconnect_handler():
    current_app.logger.info('wizard disconnect!!!')
    if session.get('task_id'):
        with get_db('EXCLUSIVE') as db:
            db.execute('update task set selected=0 where rowid=?', (session['task_id'],))
    close_db()
