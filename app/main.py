import json
import datetime

from flask import Blueprint, session, redirect, url_for, current_app

from .database import Task, db
from .gentasks import get_task

bp = Blueprint('main', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('/')
def index():

    current_time = datetime.datetime.utcnow()
    one_hour_ago = current_time - datetime.timedelta(hours=2)
    tasks = db.session.query(Task).with_for_update()\
        .filter((Task.updated_at < one_hour_ago) & Task.selected)

    for task in tasks:
        task.selected = False

    task = db.session.query(Task).with_for_update()\
        .filter_by(selected=False)\
        .first()
    if task is None:
        task = Task(body=get_task())
        db.session.add(task)

    task.selected = True
    db.session.commit()

    session['task_id'] = task.id
    session.permanent = True

    body = json.loads(task.body)
    log = body['log']

    if not log or ('metadata' in log[-1]):
        current_app.logger.info('Redirect to user index.')
        return redirect(url_for('user.index'))
    current_app.logger.info('Redirect to wizard index.')
    return redirect(url_for('wizard.index'))
