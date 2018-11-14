import json

from flask import (Blueprint, render_template, request, session, redirect,
                   url_for, current_app, flash)

from .database import Task, db
from .utils import get_priority, add_turn_count

bp = Blueprint('user', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('user/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if session.get('task_id'):
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
            current_app.logger.info('task id: {}'.format(task_id))
        else:
            return redirect(url_for('main.select_task'))

        body = json.loads(task.body)
        desc = body['goal']['message']
        log = body['log']
        db.session.commit()
        return render_template('user.html', desc=desc, log=log)

    elif request.method == 'POST':
        task_id = session['task_id']
        task = Task.query.filter_by(id=task_id).one()
        body = json.loads(task.body)
        desc = body['goal']['message']
        resp = request.form['resp']
        if resp.strip():
            body['log'].append({'text': [resp]})
            log = body['log']
            task.body = json.dumps(body, ensure_ascii=False)
            task.priority = get_priority(body)
            task.selected = False
            db.session.commit()
            session.pop('task_id')
            add_turn_count()
            return render_template('user.html', desc=desc, log=log)
        else:
            flash('回复内容不能为空哦')
            return redirect(url_for('user.index'))
