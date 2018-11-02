import json

from flask import (Blueprint, render_template, request, session, jsonify,
                   redirect, url_for, current_app, flash)

from .database import Task, db

bp = Blueprint('wizard', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('wizard/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if session.get('task_id'):
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
        else:
            return redirect(url_for('main.index'))

        current_app.logger.info('task id: {}'.format(task_id))
        body = json.loads(task.body)
        log = body['log']
        db.session.remove()
        return render_template('wizard.html', log=log)

    elif request.method == 'POST':
        resp = request.form['sys_resp']
        if resp.strip():
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
            body = json.loads(task.body)
            # save the wizard response and metadata
            body['log'][-1]['text'].append(request.form['sys_resp'])
            body['log'][-1]['metadata'] = session['metadata']
            task.body = json.dumps(body, ensure_ascii=False)
            task.selected = False
            db.session.commit()
            return render_template('wizard.html', log=body['log'])
        else:
            flash('回复内容不能为空哦')
            return redirect(url_for('wizard.index'))


@bp.route('update_metadata/', methods=['POST'])
def update_metadata():
    """
    This method will not save the metadata, and metadata will be saved until
    worker submit the whole form.
    """
    food_type = request.form['want_food_type']
    pricerange = request.form['want_pricerange']
    request_food_type = True if request.form['request_food_type'] == 'yes' else False
    request_pricerange = True if request.form['request_pricerange'] == 'yes' else False
    request_recom = True if request.form['request_recom'] == 'yes' else False
    request_phone = True if request.form['request_phone'] == 'yes' else False
    request_addr = True if request.form['request_addr'] == 'yes' else False

    metadata = {'inform': {}, 'request': []}

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

    session['metadata'] = metadata
    return jsonify(metadata)


